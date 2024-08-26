from django import forms
from payments.models import Payment

class PaymentFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All')] + list(Payment.Status.choices),
        required=False,
        label='Status'
    )
