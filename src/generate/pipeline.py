from vertexai.generative_models import HarmBlockThreshold
from vertexai.generative_models import GenerationConfig
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import HarmCategory
from vertexai.generative_models import Part
from src.config.logging import logger
from src.config.setup import config
from typing import List, Dict, Any
import json
import os


DATA_DIR = './data'
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')


def load_file(file_path: str) -> str:
    """
    Load text content from a file.
    """
    logger.info(f"Loading text file from {file_path}")
    with open(file_path, 'r') as file:
        return file.read()


def load_binary_file(file_path: str) -> bytes:
    """
    Load binary content from a file.
    """
    logger.info(f"Loading binary file from {file_path}")
    with open(file_path, 'rb') as file:
        return file.read()


def save_json(data: Any, file_path: str) -> None:
    """
    Save JSON data to a file.
    """
    logger.info(f"Saving JSON data to {file_path}")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def create_generation_config() -> GenerationConfig:
    """
    Create a GenerationConfig instance.
    """
    logger.info("Creating generation configuration")
    return GenerationConfig(
        temperature=0.0, 
        top_p=0.0, 
        top_k=1, 
        candidate_count=1, 
        max_output_tokens=8192,
        response_mime_type="application/json"
    )


def create_safety_settings() -> Dict[HarmCategory, HarmBlockThreshold]:
    """
    Create a safety settings dictionary.
    """
    logger.info("Creating safety settings")
    return {
        HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
    }

def generate_response(model: GenerativeModel, contents: List[Part], response_schema: Dict[str, Any]) -> Any:
    """
    Generate content using the generative model.
    """
    logger.info("Generating response using the generative model")
    response = model.generate_content(contents, 
                                      generation_config=GenerationConfig(
                                          response_mime_type="application/json", 
                                          response_schema=response_schema
                                      ),
                                      safety_settings=create_safety_settings())
    output_json = json.loads(response.text.strip())
    logger.info(f"Response generated: {output_json}")
    logger.info(f"Finish reason: {response.candidates[0].finish_reason}")
    logger.info(f"Safety ratings: {response.candidates[0].safety_ratings}")
    return output_json


def step_1(model: GenerativeModel, pdf_parts: Part, output_path: str):
    try:
        logger.info("Starting step 1")
        system_instruction = [load_file(os.path.join(DATA_DIR, 'templates/system_instructions_step_1.txt'))]
        model = GenerativeModel(config.TEXT_GEN_MODEL_NAME, system_instruction=system_instruction)
        user_prompt = "Identify all energy consumption metrics mentioned in the document. Return each metric with its code and item name."
        contents = [pdf_parts, user_prompt]

        response_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "pattern": "^[A-Za-z0-9_]{1,20}$"},
                    "item": {"type": "string", "pattern": "^[A-Za-z0-9 ]{1,50}$"}
                },
                "required": ["code", "item"]
            }
        }

        output_json = generate_response(model, contents, response_schema)
        save_json(output_json, output_path)
        logger.info("Step 1 completed successfully")
    except Exception as e:
        logger.error(f"Error in step_1: {e}")


def step_2(model: GenerativeModel, pdf_parts: Part, output_path: str):
    try:
        logger.info("Starting step 2")
        system_instruction = [load_file(os.path.join(DATA_DIR, 'templates/system_instructions_step_2.txt'))]
        model = GenerativeModel(config.TEXT_GEN_MODEL_NAME, system_instruction=system_instruction)
        metrics = load_binary_file(os.path.join(OUTPUT_DIR, 'out_step_1.txt'))
        out_step_1 = Part.from_data(data=metrics, mime_type='text/plain')

        user_prompt = """For each metric listed in the provided text file:
        
        Extract the following information from the corresponding PDF:
        
        * Raw numerical value
        * Unit of measurement
        * Page number
        * Relevant text snippet
        
        Important notes:
        
        * Include metrics with null values in the output
        * Maintain the original order of metrics as listed in the text file
        * Ensure the output contains the same number of items as the input list
        
        Present the information in a structured format for each metric."""

        contents = [pdf_parts, out_step_1, user_prompt]

        response_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "pattern": "^[A-Za-z0-9_]{1,20}$"},
                    "item": {"type": "string", "pattern": "^[A-Za-z0-9 ]{1,50}$"},
                    "value": {"type": "number"},
                    "unit": {"type": "string", "pattern": "^[A-Za-z0-9 ]{1,20}$"},
                    "page_number": {"type": "number"},
                    "snippet": {"type": "string", "pattern": "^.{1,500}$"}
                },
                "required": ["code", "item", "value", "unit", "page_number", "snippet"]
            }
        }

        output_json = generate_response(model, contents, response_schema)
        save_json(output_json, output_path)
        logger.info("Step 2 completed successfully")
    except Exception as e:
        logger.error(f"Error in step_2: {e}")


def step_3(model: GenerativeModel, pdf_parts: Part, output_path: str):
    try:
        logger.info("Starting step 3")
        system_instruction = [load_file(os.path.join(DATA_DIR, 'templates/system_instructions_step_3.txt'))]
        model = GenerativeModel(config.TEXT_GEN_MODEL_NAME, system_instruction=system_instruction)
        metrics = load_binary_file(os.path.join(OUTPUT_DIR, 'out_step_2.txt'))
        out_step_2 = Part.from_data(data=metrics, mime_type='text/plain')

        user_prompt = """For each extracted metric, using the provided PDF:
        
        * Determine the reporting year, focusing on the most recent if multiple years are present.
        * Assign a scope (Global, Regional, or Country-Specific) and a flag (Full or Partial) to each value. Provide reasoning for the flag assignment.
        * Classify each value as either 'Operational Consumption' or 'Supply Chain Consumption' based on the context in the document."""

        contents = [pdf_parts, out_step_2, user_prompt]

        response_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "pattern": "^[A-Za-z0-9_]{1,20}$"},
                    "item": {"type": "string", "pattern": "^[A-Za-z0-9 ]{1,50}$"},
                    "value": {"type": "number"},
                    "unit": {"type": "string", "pattern": "^[A-Za-z0-9 ]{1,20}$"},
                    "page_number": {"type": "number"},
                    "snippet": {"type": "string", "pattern": "^.{1,500}$"},
                    "year": {"type": "number", "minimum": 1900, "maximum": 2100},
                    "scope": {"type": "string", "pattern": "^[A-Za-z0-9 ]{1,100}$"},
                    "flag": {"type": "string", "pattern": "^[A-Za-z ]{1,50}$"},
                    "flag_reasoning": {"type": "string", "pattern": "^.{1,500}$"},
                    "consumption_type": {"type": "string", "pattern": "^[A-Za-z ]{1,50}$"}
                },
                "required": ["code", "item", "value", "unit", "page_number", "snippet", "year", "scope", "flag", "flag_reasoning", "consumption_type"]
            }
        }

        output_json = generate_response(model, contents, response_schema)
        save_json(output_json, output_path)
        logger.info("Step 3 completed successfully")
    except Exception as e:
        logger.error(f"Error in step_3: {e}")


def main():
    try:
        logger.info("Starting main process")
        pdf_bytes = load_binary_file(os.path.join(DATA_DIR, 'test_doc.pdf'))
        pdf_parts = Part.from_data(data=pdf_bytes, mime_type='application/pdf')

        step_1(config.TEXT_GEN_MODEL_NAME, pdf_parts, os.path.join(OUTPUT_DIR, 'out_step_1.txt'))
        step_2(config.TEXT_GEN_MODEL_NAME, pdf_parts, os.path.join(OUTPUT_DIR, 'out_step_2.txt'))
        step_3(config.TEXT_GEN_MODEL_NAME, pdf_parts, os.path.join(OUTPUT_DIR, 'out_step_3.txt'))
        logger.info("Main process completed successfully")
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
