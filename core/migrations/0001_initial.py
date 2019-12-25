# Generated by Django 2.2.3 on 2019-08-09 21:36

from django.db import migrations, models


def create_default_config(apps, schema_editor):
    AppConfig = apps.get_model("core", "AppConfig")
    AppConfig().save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('html_form_template', models.TextField(blank=True)),
                ('number_of_videos_per_age', models.IntegerField(default=10)),
            ],
        ),
        migrations.RunPython(create_default_config),
    ]
