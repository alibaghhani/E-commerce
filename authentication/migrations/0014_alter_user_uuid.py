# Generated by Django 5.1.1 on 2024-10-27 08:59

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0013_alter_user_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('e85e8fc9-63d3-40e6-9542-5e639d8523db'), editable=False, unique=True),
        ),
    ]
