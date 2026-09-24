from pydantic import BaseModel, EmailStr, Field
import uuid

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=128)

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: str
    is_active: bool

    model_config = {
        "from_attibutes" : True,
    }