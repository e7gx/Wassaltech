from django import forms
from django.core.validators import MinValueValidator

from .models import Payment

class PaymentForm(forms.ModelForm):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        model = Payment
        fields = ['amount']