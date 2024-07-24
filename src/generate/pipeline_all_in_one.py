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
OUTPUT_DIR = os.path.join(DATA_DIR, 'output_all_in_one')
GEN_DIR = os.path.join(DATA_DIR, 'generated_all_in_one')


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


def step_all_in_one(model: GenerativeModel, pdf_parts: Part, output_path: str):
    try:
        logger.info("Starting processing ...")
        system_instruction = [load_file(os.path.join(DATA_DIR, 'templates/system_instructions.txt'))]
        model = GenerativeModel(config.TEXT_GEN_MODEL_NAME, system_instruction=system_instruction)
        user_prompt = "Analyze the following PDF and follow the rules."
        contents = [pdf_parts, user_prompt]

        response_schema = response_schema = {
    "type": "object",
    "properties": {
        "year": {
            "type": "number",
            "minimum": 1900,
            "maximum": 2100
        },
        "metrics": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "pattern": "^[A-Za-z0-9_]{1,20}$"
                    },
                    "item": {
                        "type": "string",
                        "pattern": "^[A-Za-z0-9 ]{1,50}$"
                    },
                    "scope": {
                        "type": "string",
                        "pattern": "^[A-Za-z0-9 ]{1,100}$"
                    },
                    "flag": {
                        "type": "string",
                        "pattern": "^[A-Za-z ]{1,50}$"
                    },
                    "value": {
                        "type": "string",
                        "pattern": "^[A-Za-z0-9 ]{1,50}$"
                    },
                    "unit": {
                        "type": "string",
                        "pattern": "^[A-Za-z0-9 ]{1,20}$"
                    },
                    "page_number": {
                        "type": "number"
                    },
                    "snippet": {
                        "type": "string",
                        "pattern": "^.{1,500}$"
                    },
                    "relevant_information": {
                        "type": "string",
                        "pattern": "^.{1,500}$"
                    },
                    "flag_reasoning": {
                        "type": "string",
                        "pattern": "^.{1,500}$"
                    },
                    "consumption_type": {
                        "type": "string",
                        "pattern": "^[A-Za-z ]{1,50}$"
                    }
                },
                "required": ["code", "item", "scope", "flag", "value", "unit", "page_number", "snippet", "flag_reasoning", "consumption_type"]
            }
        },
        "metadata": {
            "type": "object",
            "properties": {
                "data_sources": {
                    "type": "string",
                    "pattern": "^.{1,200}$"
                },
                "data_collector": {
                    "type": "string",
                    "pattern": "^.{1,100}$"
                },
                "fiscal_year_end": {
                    "type": "string",
                    "pattern": "^(0[1-9]|1[0-2])\/(0[1-9]|[12][0-9]|3[01])\/(19|20)\d\d$"  # Date in MM/DD/YYYY format
                },
                "geographical_scope": {
                    "type": "string",
                    "pattern": "^[A-Za-z ]{1,50}$"
                },
                "country": {
                    "type": "string",
                    "pattern": "^[A-Za-z ]{1,50}$"
                },
                "organization_name": {
                    "type": "string",
                    "pattern": "^[A-Za-z0-9 ]{1,100}$"
                }
            },
            "required": ["data_sources", "data_collector", "fiscal_year_end", "geographical_scope", "country", "organization_name"]
        }
    },
    "required": ["year", "metrics", "metadata"]
}

        output_json = generate_response(model, contents, response_schema)
        save_json(output_json, output_path)
        logger.info("Step completed successfully")
    except Exception as e:
        logger.error(f"Error in step: {e}")


def convert_json_to_jsonl(input_file, output_file):
    # Read the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)
        
     # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write each item as a separate line in the output JSONL file
    with open(output_file, 'w') as f:
        for item in data["metrics"]:
            json_line = json.dumps(item)
            f.write(json_line + '\n')


def step_4(input_file, output_file):
    convert_json_to_jsonl(input_file, output_file)
    print(f"Conversion complete. JSONL file saved as {output_file}")

def main():
    
    try:
        for filename in os.listdir('./data/pdfs'):
            if filename.endswith('.pdf'):
                # Get the full path to the PDF file
                full_path = os.path.join('./data/pdfs', filename)
                print(full_path)
                logger.info("Starting main process")
                pdf_bytes = load_binary_file(full_path)
                pdf_parts = Part.from_data(data=pdf_bytes, mime_type='application/pdf')

                step_all_in_one(config.TEXT_GEN_MODEL_NAME, pdf_parts, os.path.join(OUTPUT_DIR, 'out_step.txt'))
                filename = filename.replace('.pdf', '')
                step_4(os.path.join(OUTPUT_DIR, 'out_step.txt'), os.path.join(GEN_DIR, f'{filename}.jsonl'))
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == '__main__':
    main()