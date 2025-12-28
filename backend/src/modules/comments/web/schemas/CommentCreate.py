from pydantic import BaseModel, ConfigDict

__all__ = ["CommentCreate"]


class CommentCreate(BaseModel):
    model_config = ConfigDict(from_atributes=True)

    body: str