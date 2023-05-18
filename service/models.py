from typing import Any, List, Optional, Union

from pydantic import BaseModel


class Error(BaseModel):
    error_key: str
    error_message: str
    error_loc: Optional[Any] = None


class User(BaseModel):
    username: str
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


class ExplainResponse(BaseModel):
    p: int
    explanation: str


class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {
                "errors": [
                    {
                        "error_key": "http_exception",
                        "error_message": "Model not found",
                        "error_loc": None,
                    }
                ]
            }
        }
