# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from datetime import datetime
from myapp.forms import SignupForm, LoginForm, PostForm, LikeForm, CommentForm
from django.contrib.auth.hashers import make_password, check_password
from imgurpython import ImgurClient
from .models import UserModel, SessionToken, PostModel, LikeModel, CommentModel
from djpro.settings import BASE_DIR
from paralleldots import set_api_key, get_api_key
from paralleldots import similarity, emotion, sentiment
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.template import Context, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
import smtplib

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
            fromaddr = "srkvkr12@gmail.com"
            toaddr = email
            message = "Sign up completed successfully"
            password = 'vinay@17'
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.starttls()
            server.login(fromaddr, password)
            server.sendmail(fromaddr, toaddr, message)
            server.quit()
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
            email = user.email
            print email

            if user:
                if check_password(password, user.password):
                    session = SessionToken(user = user)
                    session.create_token()
                    session.save()
                    response = redirect("/feed")
                    response.set_cookie(key="session_token", value=session.session_token)
                    print 'User is valid'

                    return response
                else:
                    print 'User is  invalid'
    response['form'] = form
    return render(request, 'login.html' , response)


def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            return session.user
    else:
        return None


def post_view(request):
    user = check_validation(request)
    set_api_key("rpMuzF79DEc91DyPeTe3Dgs1EZ3CYjDC2YRxRGyQQoo")
    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()


                path = str(BASE_DIR + '\\' + post.image.url)

                client = ImgurClient('4824a0a73eb0084', '66b335766fb74c12d90df2aed8e977f7c1a50992')
                post.image_url = client.upload_from_path(path,anon=True)['link']
                post.save()
                print 'Post is created successfully'
                return redirect('/feed/')
            else:
                print 'Post could not be created'

        else:
            form = PostForm()
        return render(request, 'post.html', {'form' : form})
    else:
        return redirect('/login/')


def feed(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('-created_on')[:1]#.filter(user=user)

        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feed.html', {'posts': posts})
    else:
        return redirect('/login/')


def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
                fromaddr = "srkvkr12@gmail.com"
                toaddr = user.email
                message = "You have liked the post successfully"
                password = 'vinay@17'
                server = smtplib.SMTP('smtp.gmail.com:587')
                server.starttls()
                server.login(fromaddr, password)
                server.sendmail(fromaddr, toaddr, message)
                server.quit()
                print 'like row has been successfully created in database'
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')


def feed_view(request):
    user = check_validation(request)
    if user:

        posts = PostModel.objects.get(pk = user).order_by('created_on')

        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feed.html', {'posts': posts})
    else:

        return redirect('/login/')


def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')

            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            print 'The comment has been posted.'
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')
