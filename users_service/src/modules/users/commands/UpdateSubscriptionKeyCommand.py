from pydantic import BaseModel

class UpdateSubscriptionKeyCommand(BaseModel):
    user_id: int
    subscription_key: str

