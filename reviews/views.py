from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def reviews(request):
    return HttpResponse("Hello, World!")
