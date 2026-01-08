from dataclasses import dataclass


@dataclass
class PublishArticleCommand:
    """Команда на публикацию статьи (начало SAGA)."""
    article_id: int
    user_id: int
