from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            userObj = form.cleaned_data
            username = userObj['username']
            email = userObj['email']
            password1 = userObj['password']
            password2 = userObj['password2']

            if password1 == password2:

                if not (User.objects.filter(username= username).exists()
                        or User.objects.filter(email = email).exists()):
                    User.objects.create_user(username, email, password1)
                    user = authenticate(username = username, password = password1)
                    login(request, user)
                    return HttpResponseRedirect('/block')

                else:
                    messages.error(request,'Look like a username with that email '\
                                            'or password already exists!')
                    return HttpResponseRedirect('account/register')
            else:
                messages.error(request, 'Registration failed! Your password does not match.')
                return HttpResponseRedirect('account/register')

    elif request.method == 'GET':
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form':form})

