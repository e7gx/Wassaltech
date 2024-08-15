from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from .forms import CustomerLoginForm, FreelancerLoginForm, CustomerSignUpForm, FreelancerSignUpForm

def customer_login(request):
    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if hasattr(user, 'account') and user.account.user_type == 'Customer':
                    login(request, user)
                    return redirect('customer_dashboard')  # Redirect to customer dashboard
                else:
                    messages.error(request, 'Invalid credentials for customer account.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerLoginForm()
    return render(request, 'accounts/customer_login.html', {'form': form})


def customer_signup(request: HttpRequest):
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return HttpResponse('Account created successfully')
        else:
            messages.error(request, 'Account creation failed. Please correct the errors below.')
    else:
        form = CustomerSignUpForm()

    return render(request, 'accounts/customer_signup.html', {'form': form})


#! freelancer Views
def freelancer_login(request):
    if request.method == 'POST':
        form = FreelancerLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if hasattr(user, 'account') and user.account.user_type == 'Freelancer':
                    login(request, user)
                    return HttpResponse(" Redirect to freelancer dashboard ")  # Redirect to freelancer dashboard
                else:
                    messages.error(request, 'Invalid credentials for freelancer account.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FreelancerLoginForm()

    return render(request, 'accounts/freelancer_login.html', {'form': form})


def freelancer_signup(request: HttpRequest):
    if request.method == 'POST':
        form = FreelancerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return HttpResponse('Account created successfully freelancer_signup')
        else:
            messages.error(request, 'Account creation failed. Please correct the errors below.')
    else:
        form = FreelancerSignUpForm()

    return render(request, 'accounts/freelancer_signup.html', {'form': form})
