from pydantic import BaseModel

class SubscribeDTO(BaseModel):
    target_user_id: int
