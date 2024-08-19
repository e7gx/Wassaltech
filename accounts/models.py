from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20,)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.user.first_name} {self.user.last_name}"

def user_avatar_path(instance, filename):
    return f'avatars/{instance.user.username}/{filename}'

def user_certificate_path(instance, filename):
    return f'certificates/{instance.user.username}/{filename}'

class Freelancer(models.Model):
    STATUS = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Pending', 'Pending'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    certificate_id = models.CharField(max_length=100)
    certificate_expiration = models.DateField(blank=True, null=True)
    certificate_image = models.ImageField(upload_to=user_certificate_path)
    avatar = models.ImageField(upload_to=user_avatar_path)
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')
    is_verified = models.BooleanField(default=False,)#! review this field to see if it is necessary for the Customer model to have this field - but it's necessary for the Freelancer model

    def __str__(self):
        return f"{self.user.username} | {self.status}"
