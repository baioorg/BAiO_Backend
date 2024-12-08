# Generated by Django 5.1.1 on 2024-12-07 22:25

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0007_csvfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='llmprovider',
            name='last_updated',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='llmprovider',
            name='url',
            field=models.URLField(default='https://api.openai.com/v1/', max_length=255),
            preserve_default=False,
        ),
    ]