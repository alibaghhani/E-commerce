# Generated by Django 5.1.1 on 2024-10-14 10:32

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('7624333f-5d6f-44df-8cb8-04e452c73518'), editable=False, unique=True),
        ),
    ]
