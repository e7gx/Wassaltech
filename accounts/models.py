from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20,) 
    is_verified = models.BooleanField(default=False,)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} | {self.first_name} {self.last_name} | {self.is_verified}"


class Freelancer(models.Model):
    STATUS = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Pending', 'Pending'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    certificate_id = models.CharField(max_length=50)
    certificate_expiration = models.DateField()
    certificate_image = models.FileField(upload_to='media/certificates/',)
    avatar = models.ImageField(upload_to='media/avatar/', default='media/avatar/default.jpg')
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')
    
    def __str__(self):
        return f"{self.user.username} | {self.status}"