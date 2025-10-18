from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TTRequest(BaseModel):
    product_name: str
    tnved_code: str

class TTResponse(BaseModel):
    measure: str
    reason: str