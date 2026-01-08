"""
Publish Worker - публикация постов.
"""
import logging
import requests

from .SagaConfig import celery, broker, BACKEND_URL, get_internal_headers, send_to_dlq

logger = logging.getLogger(__name__)


@celery.task(
    name="post.publish",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    autoretry_for=(requests.RequestException,),
    retry_backoff=True
)
def publish_post(self, data: dict):
    """
    Публикация поста.
    Переводит статус в PUBLISHED и ставит задачу на уведомления.
    """
    post_id = data.get("post_id")
    author_id = data.get("author_id")
    title = data.get("title")
    
    logger.info(f"[PUBLISH] Publishing post_id={post_id}")
    
    dedup_key = f"publish:{post_id}"
    if broker.get_dedup_key(dedup_key):
        logger.info(f"[PUBLISH] Post {post_id} already published, skipping")
        return {"status": "skipped", "reason": "already_processed"}
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/internal/posts/{post_id}/publish",
            headers=get_internal_headers(),
            timeout=10
        )
        response.raise_for_status()
        
        logger.info(f"[PUBLISH] Post {post_id} published successfully")
        
        celery.send_task(
            "post.notify",
            args=[{
                "post_id": post_id,
                "author_id": author_id,
                "title": title
            }]
        )
        
        broker.set_dedup_key(dedup_key, "published", 86400)
        return {"status": "published", "post_id": post_id}
        
    except requests.RequestException as e:
        logger.error(f"[PUBLISH] Request error for post {post_id}: {e}")
        if self.request.retries >= self.max_retries:
            send_to_dlq("post.publish", data, str(e))
        raise
    except Exception as e:
        logger.error(f"[PUBLISH] Unexpected error for post {post_id}: {e}")
        send_to_dlq("post.publish", data, str(e))
        raise
