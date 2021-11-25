from celery import shared_task
from celery.utils.log import get_task_logger

from .utils import EmailHelper

logger = get_task_logger(__name__)

@shared_task(name="send_email_task")
def send_email_task(data):
    logger.info("Send email task is being executed")
    return EmailHelper.send_mail(data)