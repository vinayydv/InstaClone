# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from datetime import datetime
from myapp.forms import SignupForm, LoginForm
from django.contrib.auth.hashers import make_password, check_password
from .models import UserModel, SessionToken

# Create your views here.



def signup_view(request):
    today = datetime.now()
    if request.method == 'GET':
        form = SignupForm()
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']
            hashed_password = make_password(password)
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()
            return render(request, 'success.html')

    return render(request, 'index.html', {
        'today': today,
        'method': request.method,
        'form': form
    })


def login_view(request):
    response ={}
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {
            'form': form
        })
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = UserModel.objects.filter(username = username).first()

            if user:
                if check_password(password, user.password):
                    session = SessionToken(user = user)
                    session.create_token()
                    session.save()
                    response = redirect("/feed")
                    return response
                    print 'User is valid'
                else:
                    print 'User is invalid'
    response['form'] = form
    return render(request, 'login.html' , response)


def feed(request):
    return render(request, "feed.html ")

















