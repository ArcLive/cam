import os

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.conf import settings
from django.template import Context, Template

from core.models import AppConfig


def send_video_email(email, video):
    config = AppConfig.objects.first()
    context = Context({
        'user': email
    })
    content = Template(config.html_form_template).render(context)
    msg = EmailMultiAlternatives(
        config.email_subject, content,
        settings.EMAIL_HOST_USER,
        [email],
        )
    msg.attach_alternative(content, "text/html")
    msg.attach_file(os.path.join(settings.WATCHING_DIR, video))
    msg.send()