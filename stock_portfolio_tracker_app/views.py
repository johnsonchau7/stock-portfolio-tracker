from django.shortcuts import render

# Create your views here.

def login(request):
    return render(request, 'login/login.html')

def register(request):
    return render(request, 'registration/register.html')

def stockpage(request):
    return render(request, 'stockpage/stockpage.html')
