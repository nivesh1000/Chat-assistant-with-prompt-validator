from pydantic import BaseModel, ValidationError, field_validator
import os
from dotenv import load_dotenv, find_dotenv
import re

env_path = find_dotenv("config/.env")
load_dotenv(env_path)

class UserModel(BaseModel):
    AZURE_OPENAI_ENDPOINT : str
    AZURE_ENDPOINT : str
    CONTENT_MODERATOR_ENDPOINT : str

    @field_validator("AZURE_OPENAI_ENDPOINT","AZURE_ENDPOINT","CONTENT_MODERATOR_ENDPOINT")
    def validate_https_url(url: str) -> None:
        pattern = r'^https://'
        if re.match(pattern, url):
            pass
        else:
            raise ValueError("Invalid Endpoint.")
    
env_vars = {
    "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "CONTENT_MODERATOR_ENDPOINT": os.getenv("CONTENT_MODERATOR_ENDPOINT"),
    "AZURE_ENDPOINT": os.getenv("AZURE_ENDPOINT"), 
}

try:
    user_model = UserModel(**env_vars)
except ValidationError as err:
    print(err.json(indent=4)) 
