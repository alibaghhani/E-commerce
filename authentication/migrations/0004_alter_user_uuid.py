# Generated by Django 5.1.1 on 2024-10-21 10:39

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
            field=models.UUIDField(default=uuid.UUID('f3529ccd-589a-4aab-b22a-62b36df8a776'), editable=False, unique=True),
        ),
    ]