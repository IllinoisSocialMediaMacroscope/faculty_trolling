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
            password = userObj['password']

            if not (User.objects.filter(username= username).exists()
                    or User.objects.filter(email = email).exists()):
                User.objects.create_user(username, email, password)
                user = authenticate(username = username, password = password)
                login(request, user)
                return HttpResponseRedirect('/block')

            else:
                message = 'Look like a username with that email '\
                                        'or password already exists!'
                return render(request, 'register.html', {'form': form,
                                                         'message':message})

    elif request.method == 'GET':
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form':form})

