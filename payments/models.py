from datetime import timedelta, datetime
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from orders.models import Offer


class Payment(models.Model):
    class Status(models.TextChoices):
        PROCESSING = 'Processing', 'Processing'
        PROCESSED = 'Processed', 'Processed'
        DEPOSITED = 'Deposited', 'Deposited'

    offer = models.OneToOneField(Offer, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.00)
    currency = models.CharField(max_length=3, default='SAR')
    status = models.CharField(max_length=10, choices=Status.choices, default='Processing')
    payment_date = models.DateTimeField(auto_now_add=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                        validators=[MinValueValidator(0)])
    # Refund policies
    FULL_REFUND_HOURS = 24
    HALF_REFUND_HOURS = 12
    # Processing time policy
    # It is set to 0 hours now for demonstration reasons, but it should be 2 weeks or more depending on the policy
    PROCESSING_HOURS = 0

    deposit_date = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'Payment to {self.offer.freelancer.user.username} from {self.offer.order.customer.user.username} for offer {self.offer.id} - {self.amount} {self.currency}'

    def customer_cancel_refund(self) -> None:
        """
        Calculate and process the refund amount for a customer cancellation based on the time until the appointment.

        If the cancellation occurs:
        - At least `FULL_REFUND_HOURS` before the appointment, a full refund is given.
        - At least `HALF_REFUND_HOURS` before the appointment, a half refund is given.

        The refund amount is updated, and the current amount is adjusted accordingly.

        Returns:
            None
        """
        full_refund = timedelta(hours=self.FULL_REFUND_HOURS)
        half_refund = timedelta(hours=self.HALF_REFUND_HOURS)
        appointment_datetime = datetime.combine(self.offer.appointment, datetime.min.time())
        now = datetime.now()
        time_until_visit = appointment_datetime - now

        if time_until_visit >= full_refund:
            self.refund_amount = self.amount
            self.amount = 0
        elif time_until_visit >= half_refund:
            self.refund_amount = self.amount / 2
            self.amount = self.amount / 2
        self.save()

    def freelancer_cancel_payment(self) -> None:
        """
        Cancels the payment by a freelancer.

        This method refunds the full amount to the freelancer by setting
        `refund_amount` to the current `amount` and then setting `amount` to 0.
        The changes are saved to the database.

        Returns:
            None
        """
        self.refund_amount = self.amount
        self.amount = 0
        self.save()

    @staticmethod
    def process_payments() -> None:
        """
        Update the status of payments that are in PROCESSING status
        and have been in that status longer than PROCESSING_HOURS.

        This method filters the Payment objects to find those that:
        1. Have a status of PROCESSING.
        2. Have a payment_date that is less than or equal to the current time minus the PROCESSING_HOURS.

        It then updates the status of these payments to PROCESSED in a single database query.

        Returns:
            None
        """
        Payment.objects.filter(
            Q(status=Payment.Status.PROCESSING) &
            Q(payment_date__lte=datetime.now() - timedelta(hours=Payment.PROCESSING_HOURS))
        ).update(status=Payment.Status.PROCESSED)

    @staticmethod
    def deposit_payments() -> None:
        """
        Update the status of payments that have been processed by setting them to deposited.

        This method filters Payment objects that are in the PROCESSED status and updates their status to DEPOSITED.
        It also sets the `deposit_date` to the current date and time for all affected records.

        Returns:
            None
        """
        Payment.objects.filter(status=Payment.Status.PROCESSED).update(status=Payment.Status.DEPOSITED,
                                                                       deposit_date=datetime.now())

    class Meta:
        ordering = ['-payment_date']
