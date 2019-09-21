
from django.conf import settings
from django.core.mail import send_mail


def send(subject, body, to, html=None):
    if not settings.ENABLE_MAIL:
        return
    send_mail(subject=subject, from_email=None, message=body, recipient_list=to, html_message=html)





