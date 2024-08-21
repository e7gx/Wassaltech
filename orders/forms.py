from django import forms
from .models import Order, Offer, categories

class OrderForm(forms.ModelForm):
    category = forms.ChoiceField(choices=categories)
    issue_description = forms.CharField(widget=forms.Textarea)
    image = forms.ImageField(widget=forms.FileInput(), required=False)
    video = forms.FileField(widget=forms.FileInput(), required=False)

    class Meta:
        model = Order
        fields = ['category', 'issue_description', 'image', 'video']

class OfferForm(forms.ModelForm):
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    description = forms.CharField(widget=forms.Textarea)
    proposed_service_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    appointment = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Offer
        fields = ['price', 'description', 'proposed_service_date', 'appointment']
