from vertexai.generative_models import HarmBlockThreshold
from vertexai.generative_models import GenerationConfig
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import HarmCategory
from vertexai.generative_models import Part
from src.config.logging import logger
from src.config.setup import config


model = GenerativeModel(config.TEXT_GEN_MODEL_NAME)
print(model.__dict__)



generation_config = GenerationConfig(temperature=0.0, 
                                     top_p=1.0, 
                                     top_k=32, 
                                     candidate_count=1, 
                                     max_output_tokens=8192)


