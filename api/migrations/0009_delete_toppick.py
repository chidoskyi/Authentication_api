# Generated by Django 5.1.4 on 2025-01-02 15:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_toppick_meals_toppicks'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Toppick',
        ),
    ]