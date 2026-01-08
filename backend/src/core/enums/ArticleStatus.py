import enum

__all__ = ["ArticleStatus"]


class ArticleStatus(str, enum.Enum):
    """
    Жизненный цикл поста (статьи):
    - DRAFT: черновик (по умолчанию)
    - PENDING_PUBLISH: автор запросил публикацию, идёт модерация/обработка
    - PUBLISHED: пост опубликован
    - REJECTED: модерация отклонила
    - ERROR: произошла техническая ошибка при обработке
    """
    DRAFT = "DRAFT"
    PENDING_PUBLISH = "PENDING_PUBLISH"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"
    ERROR = "ERROR"
