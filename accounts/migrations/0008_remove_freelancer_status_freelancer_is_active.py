# Generated by Django 5.1 on 2024-08-20 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_freelancer_internal_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='freelancer',
            name='status',
        ),
        migrations.AddField(
            model_name='freelancer',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
