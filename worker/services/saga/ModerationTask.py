"""
Moderation Worker - модерация постов.
"""
import logging
import random
import requests

from .SagaConfig import celery, broker, BACKEND_URL, get_internal_headers, send_to_dlq

logger = logging.getLogger(__name__)


@celery.task(
    name="post.moderate",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    autoretry_for=(requests.RequestException,),
    retry_backoff=True
)
def moderate_post(self, post_id: int, author_id: int, title: str, body: str, requested_by: int):
    """
    Модерация поста.
    Симулирует AI-модерацию (random approve/reject).
    
    При успехе: ставит задачу post.generate_preview
    При отклонении: вызывает /posts/{id}/reject
    """
    
    logger.info(f"[MODERATE] Starting moderation for post_id={post_id}")
    
    dedup_key = f"moderation:{post_id}"
    if broker.get_dedup_key(dedup_key):
        logger.info(f"[MODERATE] Post {post_id} already moderated, skipping")
        return {"status": "skipped", "reason": "already_processed"}
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/internal/posts/{post_id}",
            headers=get_internal_headers(),
            timeout=10
        )
        
        if response.status_code == 404:
            logger.error(f"[MODERATE] Post {post_id} not found")
            return {"status": "error", "reason": "post_not_found"}
        
        response.raise_for_status()
        post_data = response.json()
        
        if post_data.get("status") not in ["PENDING_PUBLISH"]:
            logger.info(f"[MODERATE] Post {post_id} status is {post_data.get('status')}, skipping")
            return {"status": "skipped", "reason": f"invalid_status:{post_data.get('status')}"}
        
        approved = random.random() < 0.8
        
        if approved:
            logger.info(f"[MODERATE] Post {post_id} APPROVED")
            
            celery.send_task(
                "post.generate_preview",
                args=[{
                    "post_id": post_id,
                    "author_id": author_id,
                    "title": title,
                    "body": body
                }]
            )
            
            broker.set_dedup_key(dedup_key, "approved", 86400)
            return {"status": "approved", "post_id": post_id}
        else:
            logger.info(f"[MODERATE] Post {post_id} REJECTED")
            
            reject_response = requests.post(
                f"{BACKEND_URL}/api/internal/posts/{post_id}/reject",
                headers=get_internal_headers(),
                json={"reason": "Content did not pass moderation"},
                timeout=10
            )
            reject_response.raise_for_status()
            
            broker.set_dedup_key(dedup_key, "rejected", 86400)
            return {"status": "rejected", "post_id": post_id}
            
    except requests.RequestException as e:
        logger.error(f"[MODERATE] Request error for post {post_id}: {e}")
        if self.request.retries >= self.max_retries:
            send_to_dlq("post.moderate", data, str(e))
        raise
    except Exception as e:
        logger.error(f"[MODERATE] Unexpected error for post {post_id}: {e}")
        send_to_dlq("post.moderate", data, str(e))
        raise
