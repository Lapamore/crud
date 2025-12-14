from celery import Celery
from config import config

from ...broker.impl.RedisBroker import RedisBroker
from .IoCContainer import IoCContainer

def build_container() -> IoCContainer:
    container = IoCContainer()
    
    # Register Celery
    celery_app = Celery("worker", broker=config.redis_url)
    container.register_singleton("celery", celery_app)
    
    # Register Broker
    broker = RedisBroker(config.redis_url)
    container.register_singleton("broker", broker)
    
    return container

container = build_container()
