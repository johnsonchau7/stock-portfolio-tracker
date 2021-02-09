from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

def logout_user(request):
    logout(request)
    return True
