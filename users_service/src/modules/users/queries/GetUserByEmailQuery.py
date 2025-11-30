from pydantic import BaseModel, ConfigDict


class GetUserByEmailQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    email: str
