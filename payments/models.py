from django.db import models

from orders.models import Offer


# Create your models here.
class Payment(models.Model):
    class Status(models.TextChoices):
        ON_HOLD = 'OH', 'On Hold'
        READY_TO_DEPOSIT = 'RTD', 'Ready to Deposit'
        DEPOSITED = 'D', 'Deposited'

    offer: models.OneToOneField(Offer, on_delete=models.PROTECT )
    status: models.CharField(max_length=3,
                             choices=Status.choices)
    deposit_due_date: models.DateField()
    updated_at: models.DateTimeField(auto_now=True)
    created_at: models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id
