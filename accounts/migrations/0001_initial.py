

import accounts.models
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "avatar",
                    models.ImageField(
                        blank=True,
                        default="avatars/default_profile.png",
                        upload_to=accounts.models.user_avatar_path,
                    ),
                ),
                ("phone_number", models.CharField(max_length=15, unique=True)),
                ("address", models.CharField(max_length=255)),
                ("user_type", models.CharField(max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Freelancer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("certificate_id", models.CharField(max_length=100)),
                ("certificate_expiration", models.DateField(blank=True, null=True)),
                (
                    "certificate_image",
                    models.ImageField(upload_to=accounts.models.user_certificate_path),
                ),
                (
                    "internal_rating",
                    models.FloatField(
                        default=10,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(10),
                        ],
                    ),
                ),
                ("is_verified", models.BooleanField(default=False)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-internal_rating"],
            },
        ),
    ]
