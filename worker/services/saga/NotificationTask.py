"""
Notification Worker - уведомление подписчиков.
"""
import logging
import asyncio
import requests
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from config import config
from .SagaConfig import celery, broker, USERS_DATABASE_URL, send_to_dlq

logger = logging.getLogger(__name__)


async def get_subscribers(author_id: int):
    """Получить подписчиков автора из БД users."""
    local_engine = create_async_engine(USERS_DATABASE_URL, echo=False)
    LocalSession = sessionmaker(local_engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with LocalSession() as session:
            query = text("""
                SELECT s.subscriber_id, u.subscription_key 
                FROM subscribers s
                JOIN users u ON s.subscriber_id = u.id
                WHERE s.author_id = :author_id
            """)
            result = await session.execute(query, {"author_id": author_id})
            return result.fetchall()
    finally:
        await local_engine.dispose()


@celery.task(
    name="post.notify",
    bind=True,
    max_retries=5,
    default_retry_delay=2,
    retry_backoff=True
)
def notify_subscribers(self, data: dict):
    """
    Уведомление подписчиков о новом посте.
    Использует push-notificator из ЛР №3.
    """
    post_id = data.get("post_id")
    author_id = data.get("author_id")
    title = data.get("title")
    
    logger.info(f"[NOTIFY] Notifying subscribers for post_id={post_id}, author_id={author_id}")
    
    try:
        subscribers = asyncio.run(get_subscribers(author_id))
        logger.info(f"[NOTIFY] Found {len(subscribers)} subscribers for author {author_id}")
        
        for sub in subscribers:
            subscriber_id = sub.subscriber_id
            subscription_key = sub.subscription_key
            
            if not subscription_key:
                logger.warning(f"[NOTIFY] Skip: no key for subscriber={subscriber_id}")
                continue
            
            dedup_key = f"notification:{post_id}:{subscriber_id}"
            if broker.get_dedup_key(dedup_key):
                logger.info(f"[NOTIFY] Skip: notification already sent to {subscriber_id} for post {post_id}")
                continue
            
            msg = f"Новый пост от автора {author_id}: {title[:50]}..."
            
            try:
                response = requests.post(
                    config.push_url,
                    headers={
                        "Authorization": f"Bearer {subscription_key}",
                        "Content-Type": "application/json",
                    },
                    json={"message": msg},
                    timeout=5,
                )
                response.raise_for_status()
                logger.info(f"[NOTIFY] Notification sent to subscriber {subscriber_id}")
                broker.set_dedup_key(dedup_key, "1", 86400)
            except requests.RequestException as e:
                logger.error(f"[NOTIFY] Failed to send notification to subscriber {subscriber_id}: {e}")
        
        return {"status": "completed", "post_id": post_id, "subscribers_count": len(subscribers)}
        
    except Exception as e:
        logger.error(f"[NOTIFY] Error notifying subscribers for post {post_id}: {e}")
        if self.request.retries >= self.max_retries:
            send_to_dlq("post.notify", data, str(e))
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery.task(name="notify_followers", bind=True, max_retries=5)
def notify_followers(self, author_id: int, post_id: int, post_title: str):
    """Legacy task для обратной совместимости с ЛР №3."""
    logger.info(f"[LEGACY] Processing notification for author_id={author_id}, post_id={post_id}")
    
    try:
        subscribers = asyncio.run(get_subscribers(author_id))
        logger.info(f"[LEGACY] Found {len(subscribers)} subscribers for author {author_id}")

        for sub in subscribers:
            subscriber_id = sub.subscriber_id
            subscription_key = sub.subscription_key

            if not subscription_key:
                logger.warning(f"[LEGACY] Skip: no key for subscriber={subscriber_id}")
                continue

            dedup_key = f"notification:{post_id}:{subscriber_id}"
            if broker.get_dedup_key(dedup_key):
                logger.info(f"[LEGACY] Skip: notification already sent to {subscriber_id} for post {post_id}")
                continue

            msg = f"Пользователь {author_id} выпустил новый пост: {post_title[:10]}..."
            
            try:
                response = requests.post(
                    config.push_url,
                    headers={
                        "Authorization": f"Bearer {subscription_key}",
                        "Content-Type": "application/json",
                    },
                    json={"message": msg},
                    timeout=5,
                )
                response.raise_for_status()
                logger.info(f"[LEGACY] Notification sent to subscriber {subscriber_id}")
                broker.set_dedup_key(dedup_key, "1", 86400)
            except requests.RequestException as e:
                logger.error(f"[LEGACY] Failed to send notification to subscriber {subscriber_id}: {e}")

    except Exception as e:
        logger.error(f"[LEGACY] Task failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
