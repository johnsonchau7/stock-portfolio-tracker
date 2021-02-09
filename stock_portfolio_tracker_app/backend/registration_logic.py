from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

def register_authenticate_login_user(request):
    post_request = request.POST
    username = post_request['registration-username-2']
    password = post_request['registration-password-2']
    password_confirm = post_request['registration-passwordconfirmation-2']

    if password != password_confirm:
        return False
    elif User.objects.filter(username=username).exists():
        return False
    else:
        user = User.objects.create_user(username=username, password=password)
        user.save()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return True
        else:
            return False
