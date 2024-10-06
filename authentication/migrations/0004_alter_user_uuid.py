# Generated by Django 5.1.1 on 2024-10-06 07:15

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_alter_user_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('a5ee0831-6710-4508-98d4-25d520cb8521'), editable=False, unique=True),
        ),
    ]
