from pydantic import BaseModel
from typing import Optional, List


class ArticleInternalResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    body: str
    author_id: int
    status: str
    preview_url: Optional[str] = None
    tagList: Optional[List[str]] = None


class UpdatePreviewRequest(BaseModel):
    preview_url: str


class RejectRequest(BaseModel):
    reason: Optional[str] = None


class SetErrorRequest(BaseModel):
    error_message: Optional[str] = None
