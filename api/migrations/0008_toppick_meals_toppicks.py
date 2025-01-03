# Generated by Django 5.1.4 on 2025-01-02 15:51

import api.models
import django.core.validators
import uuid
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_categories_image_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Toppick',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('image', models.ImageField(blank=True, null=True, upload_to=api.models.user_directory_path)),
                ('image_url', models.URLField(blank=True, max_length=500, null=True)),
            ],
            options={
                'verbose_name': 'Toppick',
                'verbose_name_plural': 'Toppicks',
                'ordering': ['-uid'],
            },
        ),
        migrations.AddField(
            model_name='meals',
            name='toppicks',
            field=models.BooleanField(default=False),
        ),
    ]