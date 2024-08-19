from django import forms
from django.contrib.auth.models import User
from .models import Account, Freelancer
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm

class CustomerLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

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
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'phone_number', 'address']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Account.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address'],
                user_type='Customer',
            )
        return user



class FreelancerSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'أدخل كلمة المرور'}))
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'أدخل رقم الهاتف'}))
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'أدخل العنوان'}))
    certificate_id = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'أدخل رقم الشهادة'}))
    certificate_image = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full max-w-xs'}))
    avatar = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full max-w-xs'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'phone_number', 'address', 'certificate_id', 'certificate_image', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'أدخل اسم المستخدم'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'أدخل الاسم الأول'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'أدخل اسم العائلة'}),
            'email': forms.EmailInput(attrs={'placeholder': 'أدخل البريد الإلكتروني'}),
        }


    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Account.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address'],
                user_type='Freelancer'
            )
            Freelancer.objects.create(
                user=user,
                certificate_id=self.cleaned_data['certificate_id'],
                certificate_image=self.cleaned_data['certificate_image'],
                avatar=self.cleaned_data['avatar']
            )
        return user
