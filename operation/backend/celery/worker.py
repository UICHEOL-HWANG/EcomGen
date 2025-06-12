from celery import Celery
from model.database import settings

image_celery = Celery(
    "worker",
    broker="sqs://",
)

# AWS 인증
image_celery.conf.broker_transport_options = {
    'region': 'ap-northeast-2',  # 서울 리전 등
    'predefined_queues': {
        'my-task-queue': {
            'url': '공사중 아직 제대로 안 만듬'
        }
    },
    'visibility_timeout': 3600,
}

image_celery.autodiscover_tasks(["celery_task.tasks"])