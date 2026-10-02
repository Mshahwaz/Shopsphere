from pydantic import BaseModel, EmailStr, Field
import uuid

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=128)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=128)


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: str
    is_active: bool

    model_config = {
        "from_attributes" : True,
    }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"