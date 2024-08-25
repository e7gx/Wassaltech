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
    price = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.TextInput(attrs={'placeholder': 'ادخل السعر','style': 'color: black;'}), label='السعر')
    description = forms.CharField(widget=forms.Textarea(attrs={'style': 'color: black;', 'placeholder': 'ادخل وصف العرض'}), label='وصف العرض')
    proposed_service_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'style': 'color: black;', 'placeholder': 'ادخل تاريخ الخدمة المقترح'}), label='تاريخ الخدمة المقترح')
    appointment = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'style': 'color: black;', 'placeholder': 'ادخل تاريخ الموعد'}), label='تاريخ الموعد')

    class Meta:
        model = Offer
        fields = ['price', 'description', 'proposed_service_date', 'appointment']
