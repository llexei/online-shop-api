import smtplib
import logging

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.order import OrderOrm
from app.models.user import UserOrm
from email.message import EmailMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name='send_order_email')   
def send_order_email(order_id:int):
    print("SMTP", settings.SMTP_HOST, settings.SMTP_PORT, repr(settings.SMTP_USER))
    db=SessionLocal()
    try:
        order=db.get(OrderOrm, order_id)
        logger.info("send_order_email start order_id=%s", order_id)
        if order is None:
            logger.warning("order not found order_id=%s", order_id)
            return 'order_not_found'

        user=db.get(UserOrm, order.user_id)
        if user is None:
            logger.warning("user not found order_id=%s", order_id)
            return 'user_not_found'
        msg = EmailMessage()
        msg["Subject"] =f'Заказ #{order.id} оформлен'
        msg["From"] = settings.SMTP_FROM
        msg["To"] = user.email
        msg.set_content(
            f'Здравствуйте, {user.username}!\n'
            f'Ваш заказ #{order.id} создан.\n'
            f'Сумма: {order.total_price}'
        )
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            smtp.ehlo()
            if settings.SMTP_USER:
                smtp.starttls()
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)
            logger.info("email sent order_id=%s", order_id)
        return 'ok'
    except Exception as e:
            logger.exception("smtp error order_id=%s", order_id)
            return 'smtp_error'
    finally:
        db.close()