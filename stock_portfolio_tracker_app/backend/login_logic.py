from django.contrib.auth import authenticate, login

# backend logic for login
def authenticate_login_user(request):
    post_request = request.POST
    username = post_request['login-username-2']
    password = post_request['login-password-2']

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return True
    else:
        return False
