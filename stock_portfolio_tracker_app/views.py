from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .backend.login_logic import authenticate_login_user
from .backend.registration_logic import register_authenticate_login_user
from .backend.stockpage_logic import logout_user, add_stock_handler

# frontend logic for login
def login(request):
    if request.user.is_authenticated:
        return redirect('stockpage')

    if request.method == "POST":
        if request.POST["login-loginbutton-1"] == "login":
            result = authenticate_login_user(request)

            if result == True:
                return HttpResponseRedirect("stockpage/")
            else:
                return render(request, 'login/login.html', {})

    return render(request, 'login/login.html')

# frontend logic for registration
def register(request):
    if request.user.is_authenticated:
        return redirect('stockpage')

    if request.method == "POST":
        if request.POST["registration-registerbutton-1"] == "register":
            result = register_authenticate_login_user(request)

            if result == True:
                return HttpResponseRedirect("stockpage/")
            else:
                return render(request, 'registration/register.html', {})

    return render(request, 'registration/register.html')

# frontend logic for stockpage
@login_required(login_url='/')
def stockpage(request):
    if request.method == "POST":
        post_request = request.POST

        if "stockpage-logoutbutton-1" in post_request:
            result = logout_user(request)

            if result == True:
                return redirect('login')

        elif "stockpage-addstockbutton-1" in post_request:
            result = add_stock_handler(request)

    return render(request, 'stockpage/stockpage.html')
