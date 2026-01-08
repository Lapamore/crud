import logging
import requests

from .SagaConfig import celery, BACKEND_URL, DLQ_QUEUE, get_internal_headers

logger = logging.getLogger(__name__)


@celery.task(name="dlq.process", bind=True, queue=DLQ_QUEUE)
def process_dlq(self, data: dict):
    """
    Обработчик DLQ - выполняет компенсирующие действия.
    
    Для разных типов задач выполняет разные компенсации:
    - post.moderate: помечает пост как REJECTED
    - post.generate_preview: помечает пост как ERROR
    - post.publish: откатывает статус в ERROR
    - post.notify: просто логирует (пост уже опубликован)
    """
    original_task = data.get("original_task")
    task_data = data.get("data", {})
    error = data.get("error")
    post_id = task_data.get("post_id")
    
    logger.info(f"[DLQ] Processing failed task: {original_task}, post_id={post_id}, error={error}")
    
    try:
        if original_task == "post.moderate":
            logger.info(f"[DLQ] Compensation for post.moderate: rejecting post {post_id}")
            response = requests.post(
                f"{BACKEND_URL}/api/internal/posts/{post_id}/reject",
                headers=get_internal_headers(),
                json={"reason": f"Moderation failed: {error}"},
                timeout=10
            )
            if response.status_code != 404:
                response.raise_for_status()
            return {"status": "compensated", "action": "rejected"}
            
        elif original_task == "post.generate_preview":
            logger.info(f"[DLQ] Compensation for post.generate_preview: setting ERROR for post {post_id}")
            response = requests.post(
                f"{BACKEND_URL}/api/internal/posts/{post_id}/error",
                headers=get_internal_headers(),
                json={"error_message": f"Preview generation failed: {error}"},
                timeout=10
            )
            if response.status_code != 404:
                response.raise_for_status()
            return {"status": "compensated", "action": "set_error"}
            
        elif original_task == "post.publish":
            logger.info(f"[DLQ] Compensation for post.publish: setting ERROR for post {post_id}")
            response = requests.post(
                f"{BACKEND_URL}/api/internal/posts/{post_id}/error",
                headers=get_internal_headers(),
                json={"error_message": f"Publication failed: {error}"},
                timeout=10
            )
            if response.status_code != 404:
                response.raise_for_status()
            return {"status": "compensated", "action": "set_error"}
            
        elif original_task == "post.notify":
            logger.info(f"[DLQ] No compensation needed for post.notify: post {post_id} is already published")
            return {"status": "logged", "action": "none"}
        
        else:
            logger.warning(f"[DLQ] Unknown task type: {original_task}")
            return {"status": "unknown_task", "action": "none"}
            
    except Exception as e:
        logger.error(f"[DLQ] Error during compensation for {original_task}: {e}")
        return {"status": "compensation_failed", "error": str(e)}
