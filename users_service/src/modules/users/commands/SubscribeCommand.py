from pydantic import BaseModel

class SubscribeCommand(BaseModel):
    subscriber_id: int
    target_user_id: int

