# Generated by Django 5.1 on 2024-08-28 07:55

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0002_alter_ordervideo_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('currency', models.CharField(default='SAR', max_length=3)),
                ('status', models.CharField(choices=[('Processing', 'Processing'), ('Processed', 'Processed'), ('Deposited', 'Deposited')], default='Processing', max_length=10)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('refund_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('deposit_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('offer', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='orders.offer')),
            ],
            options={
                'ordering': ['-payment_date'],
            },
        ),
    ]
