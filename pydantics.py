from pydantic import BaseModel, ValidationError, field_validator
import re

class UserModel(BaseModel):
    user_query: str

    @field_validator("user_query")
    def validate_user_query(cls, query: str) -> str:
        if not query:
            raise ValueError("User query cannot be empty.")
        if query.isdigit():
            raise ValueError("User query cannot be only digits.")
        if re.match(r"^\s*$", query):
            raise ValueError("User query cannot be only whitespace.")
        if not re.match(r"^[a-zA-Z0-9\s.,!?;'\"\[\]%&*|\\/`–—_-]+$", query):
            raise ValueError(f"User query contains invalid symbols.")
        if not re.search(r"[a-zA-Z]", query):
            raise ValueError("User query must contain an english alphabet (a-z, A-Z).")
        return query


