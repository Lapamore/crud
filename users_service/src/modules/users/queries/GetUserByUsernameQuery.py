from pydantic import BaseModel, ConfigDict


class GetUserByUsernameQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    username: str
