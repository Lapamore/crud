import logging
import requests
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from config import config
from infrastructure.core.ioc.container import container

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery = container.resolve("celery")
broker = container.resolve("broker")

USERS_DATABASE_URL = config.users_database_url

async def get_subscribers(author_id: int):
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

@celery.task(name="notify_followers", bind=True, max_retries=5)
def notify_followers(self, author_id: int, post_id: int, post_title: str):
    logger.info(f"Processing notification for author_id={author_id}, post_id={post_id}")
    
    try:
        subscribers = asyncio.run(get_subscribers(author_id))

        logger.info(f"Found {len(subscribers)} subscribers for author {author_id}")

        for sub in subscribers:
            subscriber_id = sub.subscriber_id
            subscription_key = sub.subscription_key

            if not subscription_key:
                logger.warning(f"Skip: no key for subscriber={subscriber_id}")
                continue

            dedup_key = f"notification:{post_id}:{subscriber_id}"
            if broker.get_dedup_key(dedup_key):
                logger.info(f"Skip: notification already sent to {subscriber_id} for post {post_id}")
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
                logger.info(f"Notification sent to subscriber {subscriber_id}")
                
                broker.set_dedup_key(dedup_key, "1", 86400)
            except requests.RequestException as e:
                logger.error(f"Failed to send notification to subscriber {subscriber_id}: {e}")
                pass

    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)