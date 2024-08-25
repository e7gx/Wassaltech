from django.core.validators import MinValueValidator
from django.db import models
from accounts.models import Account, Freelancer


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


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
    ('Discarded', 'Discarded'),
    ('In Progress', 'In Progress'),
    ('Closed', 'Closed'),
]

offer_stages = (
    # No payment involved here
    ('Pending', 'Pending'),
    ('Discarded', 'Discarded'),
    ('Declined', 'Declined'),
    # There is payment here
    ('Accepted', 'Accepted'),
    ('Cancelled', 'Cancelled'),
    ('Completed', 'Completed'),

)


class Order(models.Model):
    customer = models.ForeignKey(Account, on_delete=models.PROTECT)
    assigned_to = models.ForeignKey(Freelancer, on_delete=models.PROTECT, null=True, blank=True)
    category = models.CharField(max_length=100, choices=categories)
    issue_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    freelancer_completed = models.BooleanField(default=False)
    customer_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=order_statuses, default='Open')

    def update_status(self):
        if self.customer_completed and self.freelancer_completed:
            self.status = 'Completed'
        elif self.assigned_to and self.status == 'Open':
            self.status = 'In Progress'
        self.save()
    def __str__(self):
        if self.status == 'In Progress' or self.status == 'Closed':
            return f"Order #{self.id} by {self.customer} - Assigned to: {self.assigned_to} - Status: {self.status}"
        else:
            return f"Order #{self.id} by {self.customer} - Status: {self.status}"

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
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    complete_on_time = models.BooleanField(default=False)
    description = models.TextField()
    proposed_service_date = models.DateField()
    appointment = models.DateField()
    stage = models.CharField(max_length=100, choices=offer_stages, default='Pending')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offer by {self.freelancer} to {self.order.customer} - Price: {self.price} - Stage: {self.stage}"
