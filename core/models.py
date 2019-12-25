from django.db import models
from tinymce import HTMLField


class AppConfig(models.Model):
    email_subject = models.CharField(max_length=64, blank=True)
    html_form_template = HTMLField("Email Template", blank=True)
    number_of_videos_per_age = models.IntegerField(default=10)

    ORDER_BY_CHOICES = [
        ('modified_timestamp', 'MODIFIED_TIMESTAMP_ASC'),
        ('-modified_timestamp', 'MODIFIED_TIMESTAMP_DESC'),
        ('video_path', 'VIDEO_PATH_ASC'),
        ('-video_path', 'VIDEO_PATH_DESC'),
    ]

    order_by_field = models.CharField(
        max_length=64,
        choices=ORDER_BY_CHOICES,
        default='-modified_timestamp',
    )

    def __str__(self):
        return "Application Settings"