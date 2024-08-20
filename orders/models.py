from django.db import models
from accounts.models import Account, Freelancer

categories = (
    ('Mobiles', 'Mobiles'),
    ('Laptops', 'Laptops'),
    ('Desktops', 'Desktops'),
    ('Smartwatches', 'Smartwatches'),
    ('Monitors', 'Monitors'),
    ('Printers', 'Printers'),
    ('Cameras', 'Cameras'),
    ('Headphones', 'Headphones'),
    ('Tablets', 'Tablets'),
)
order_statuses = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Closed', 'Closed'),
        #No need for these
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

offer_stages = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Declined', 'Declined'),
    ('Cancelled', 'Cancelled'),
    ('Completed', 'Completed'),
    ('Processed', 'Processed'),
    ('Finalized', 'Finalized'),
)

class Order(models.Model):
    customer = models.ForeignKey(Account, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(Freelancer, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=100, choices=categories)
    issue_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    freelancer_completed = models.BooleanField(default=False)
    customer_completed = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=order_statuses, default='Open')
    customer_completed = models.BooleanField(default=False)
    freelancer_completed = models.BooleanField(default=False)

    def update_status(self):
        if self.customer_completed and self.freelancer_completed:
            self.status = 'Completed'
        elif self.assigned_to and self.status == 'Open':
            self.status = 'In Progress'
        self.save()

class OrderImage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    image = models.FileField(upload_to='order_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderVideo(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    video = models.FileField(upload_to='order_videos/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Offer(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    refund = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    complete_on_time = models.BooleanField(default=False)
    description = models.TextField()
    proposed_service_date = models.DateField()
    appointment = models.DateTimeField()
    stage = models.CharField(max_length=100, choices=offer_stages, default='Pending')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
