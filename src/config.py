import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

BASE_URL = os.getenv("LITELLM_BASE_URL", "http://a6k2.dgx:34000/v1")
API_KEY = os.getenv("LITELLM_API_KEY", "sk-vZZ7EeJSkwBRqSQnKNiLsw")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3-32b")