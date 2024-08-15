from django import forms
from django.contrib.auth.models import User
from .models import Account, Freelancer
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm

class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
    )

    class Meta:
        model = User
        fields = "__all__"


class FreelancerLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
    )

    class Meta:
        model = User
        fields = "__all__"


class CustomerSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Address'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=False)
            user.set_password(self.cleaned_data['password'])
            if commit:
                user.save()

            account = Account.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address'],
                user_type='Customer', 
            )
            return user



from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from .models import Freelancer

class FreelancerSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    certificate_id = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Certificate ID'}))
    certificate_expiration = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    certificate_image = forms.ImageField(required=True) 
    avatar = forms.ImageField(required=True) 

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'phone_number', 'address', 'certificate_id', 'certificate_expiration', 'certificate_image', 'avatar']

    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=False)
            user.set_password(self.cleaned_data['password'])
            if commit:
                user.save()

            freelancer = Freelancer.objects.create(
                user=user,
                certificate_id=self.cleaned_data['certificate_id'],
                certificate_expiration=self.cleaned_data['certificate_expiration'],
                certificate_image=self.cleaned_data['certificate_image'],
                avatar=self.cleaned_data['avatar'],
            )
            return user
