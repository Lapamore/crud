from pydantic import BaseModel, ConfigDict


class LoginCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    username: str
    password: str
