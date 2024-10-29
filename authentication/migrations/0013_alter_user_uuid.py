# Generated by Django 5.1.1 on 2024-10-27 08:55

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_alter_user_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('97a73000-9120-43f6-85d3-f6d1eb1df64e'), editable=False, unique=True),
        ),
    ]