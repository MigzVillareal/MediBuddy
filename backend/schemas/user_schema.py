from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserSchema(BaseModel):
    # "public" definition of a user
    user_id: int
    username: str
    # email: EmailStr # uncomment if may email, Pydantic check if valid email format

    # Optional fields
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)