import uuid

from pydantic import BaseModel

class UserResponse(BaseModel):
    id: uuid.UUID
    auth_user_id: uuid.UUID
    first_name: str | None
    last_name: str | None
    phone: str | None

    model_config = {
        "from_attributes": True
    }