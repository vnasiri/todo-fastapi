from asgiref.sync import async_to_sync
from celery import Celery
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from src.core.config import (
    database_settings as dbsettings,
)
from src.core.config import (
    notification_settings as notify_settings,
)

fastmail = FastMail(
    ConnectionConfig(
        **notify_settings.model_dump(),
    )
)

celery = Celery(
    namespace="api_tasks",
    broker=dbsettings.REDIS_URL(0),
    backend=dbsettings.REDIS_URL(0),
)

send_messages = async_to_sync(fastmail.send_message)


@celery.task
def send_mail(recipients: list[str], subject: str, body: str, subtype: MessageType):
    send_messages(
        MessageSchema(
            recipients=recipients,
            subject=subject,
            body=body,
            subtype=MessageType(subtype),
        )
    )
    return "Message Sent!"


@celery.task
def send_mail_template(
    recipients: list[EmailStr],
    subject: str,
    context: dict,
    template_name: str,
):
    send_messages(
        message=MessageSchema(
            recipients=recipients,
            subject=subject,
            template_body=context,
            subtype=MessageType.html,
        ),
        template_name=template_name,
    )
