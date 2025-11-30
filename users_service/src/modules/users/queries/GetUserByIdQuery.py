from pydantic import BaseModel, ConfigDict


class GetUserByIdQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: int
