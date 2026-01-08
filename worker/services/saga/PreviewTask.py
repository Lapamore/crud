"""
Preview Worker - генерация превью постов.
"""
import logging
import hashlib
import requests

from .SagaConfig import celery, broker, BACKEND_URL, get_internal_headers, send_to_dlq

logger = logging.getLogger(__name__)


@celery.task(
    name="post.generate_preview",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    autoretry_for=(requests.RequestException,),
    retry_backoff=True
)
def generate_preview(self, data: dict):
    """
    Генерация превью для поста.
    Создаёт фейковый URL превью (заглушка).
    
    При успехе: обновляет preview_url и ставит задачу post.publish
    """
    post_id = data.get("post_id")
    author_id = data.get("author_id")
    title = data.get("title")
    body = data.get("body")
    
    logger.info(f"[PREVIEW] Generating preview for post_id={post_id}")
    
    dedup_key = f"preview:{post_id}"
    if broker.get_dedup_key(dedup_key):
        logger.info(f"[PREVIEW] Preview for post {post_id} already generated, skipping")
        return {"status": "skipped", "reason": "already_processed"}
    
    try:
        content_hash = hashlib.md5(f"{title}{body}".encode()).hexdigest()[:8]
        preview_url = f"https://preview.example.com/posts/{post_id}/{content_hash}.png"
        
        response = requests.put(
            f"{BACKEND_URL}/api/internal/posts/{post_id}/preview",
            headers=get_internal_headers(),
            json={"preview_url": preview_url},
            timeout=10
        )
        response.raise_for_status()
        
        logger.info(f"[PREVIEW] Preview URL set for post {post_id}: {preview_url}")
        
        celery.send_task(
            "post.publish",
            args=[{
                "post_id": post_id,
                "author_id": author_id,
                "title": title
            }]
        )
        
        broker.set_dedup_key(dedup_key, preview_url, 86400)
        return {"status": "success", "post_id": post_id, "preview_url": preview_url}
        
    except requests.RequestException as e:
        logger.error(f"[PREVIEW] Request error for post {post_id}: {e}")
        if self.request.retries >= self.max_retries:
            send_to_dlq("post.generate_preview", data, str(e))
        raise
    except Exception as e:
        logger.error(f"[PREVIEW] Unexpected error for post {post_id}: {e}")
        send_to_dlq("post.generate_preview", data, str(e))
        raise
