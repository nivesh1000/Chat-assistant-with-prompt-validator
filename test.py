from pydantic import BaseModel, ValidationError, field_validator

class UserModel(BaseModel):
    user_query: str

    @field_validator("user_query")
    def validate_user_query(cls, query: str) -> str:
        if not query.strip():
            raise ValueError("User query cannot be empty or only whitespace.")
        if query.isdigit():
            raise ValueError("User query cannot be only digits.")
        
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?;'\"[]%&*|\\/`–—_-")
        invalid_chars = set(query) - allowed_chars
        
        if invalid_chars:
            raise ValueError(f"User query contains invalid symbols: {', '.join(invalid_chars)}")
        
        flag = None
        for c in query:
            if c.isalpha():
                flag =1
                break
        if not flag:
            raise ValueError("User query must contain at least one English alphabet letter (a-z, A-Z).")
        
        return query

