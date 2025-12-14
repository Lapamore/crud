from pydantic import BaseModel

class SubscriptionKeyDTO(BaseModel):
    subscription_key: str
