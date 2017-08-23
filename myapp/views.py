# -*- coding: utf-8 -*-


'''
           **IMPORTANT**


           To send mail
           The mail functionality will only funtion if the admin is logged into the browser with the email and password assigned below
           in line 66 and line 69
           and in line 191 and 194
           Also google app security must be turned off before continuing this
'''


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

#view for signing up the new user
def signup_view(request):
    today = datetime.now()
    '''
    Check if method is GET or POST    
    '''
    if request.method == 'GET':
        form = SignupForm()
    if request.method == "POST":
        form = SignupForm(request.POST)

        '''
        If form is valid get data from form
        '''

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']
            #password changed into cryptogrphic form
            hashed_password = make_password(password)
            '''
            Save new user
            '''
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()

            '''
            To send mail 
            **IMPORTANT**
            The follwing lines will only funtion if the admin is logged into the browser with the email and password assigned below
            Also google app security must be turned off before continuing this            
            '''

            #**************REMOVE FOLLOWING COMMENTS TO SEND MAIL AFTER ENTERING YOUR MAIL ID AND PASSWORD CORRECTLY
            '''

            fromaddr = "abc@gmail.com"
            toaddr = email
            message = "Sign up completed successfully"
            password = 'password'
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.starttls()
            server.login(fromaddr, password)
            server.sendmail(fromaddr, toaddr, message)
            server.quit()
            '''
            return render(request, 'success.html')

    return render(request, 'index.html', {
        'today': today,
        'method': request.method,
        'form': form
    })



#view for login
def login_view(request):
    response ={}

    '''
    Check if the request is GET or POST
    '''


    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {
            'form': form
        })
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():

            '''
            GET form data
            '''

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = UserModel.objects.filter(username = username).first()
            email = user.email
            print email

            if user:
                '''
                If user is valid chack for matching username and password in database
                '''
                if check_password(password, user.password):
                    '''
                    If user is valid validate session
                    '''
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



#view for checking validation
def check_validation(request):
    '''
    Check if their is any session token set in the cookie
    '''
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            '''
            If valid session is found then return the respective user
            '''
            return session.user
    else:
        return None


#view for defining posts
def post_view(request):
    '''
    Check is user is valid by checking valid session
    '''
    user = check_validation(request)
    '''
    api for parallel dots sentiment analysis
    '''
    set_api_key("rpMuzF79DEc91DyPeTe3Dgs1EZ3CYjDC2YRxRGyQQoo")
    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                '''
                If form is valid then get form data
                '''
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()

                #set path for local image storage
                path = str(BASE_DIR + '\\' + post.image.url)

                '''
                Set client by providing ingur token id
                '''
                client = ImgurClient('4824a0a73eb0084', '66b335766fb74c12d90df2aed8e977f7c1a50992')
                #push image to the url
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


#view for feeds
def feed(request):
    '''
    Check if user has valid seeion or not
    '''

    user = check_validation(request)
    if user:
        '''
        If user is valid then get posts from post model
        '''
        posts = PostModel.objects.all().order_by('-created_on')[:3]#.filter(user=user)

        '''
        check if a post is liked by the logged in user or not. If not than show the like button if liked then show the unlike button
        '''
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feed.html', {'posts': posts})
    else:
        return redirect('/login/')


#function to like a post
def like_view(request):
    '''
    Check of a user is valid or not by checking valid session
    '''
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)

                '''
                         To send mail 
                         **IMPORTANT**
                         The follwing lines will only funtion if the admin is logged into the browser with the email and password assigned below
                         Also google app security must be turned off before continuing this   
                                  
                '''
                #**************REMOVE FOLLOWING COMMENTS TO SEND MAIL AFTER ENTERING YOUR MAIL ID AND PASSWORD CORRECTLY
                '''
                fromaddr = "abc@gmail.com"
                toaddr = user.email
                message = "You have liked the post successfully"
                password = 'password'
                server = smtplib.SMTP('smtp.gmail.com:587')
                server.starttls()
                server.login(fromaddr, password)
                server.sendmail(fromaddr, toaddr, message)
                server.quit()
                '''
                print 'like row has been successfully created in database'
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')

'''
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
'''


#view for comment on a post
def comment_view(request):
    '''
    Check if the user is valid or not by cheking existing session_token
    if user is valid and request is POST
    then get comment text from form
    save comment in comment model
    :param request:
    :return:
    '''
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


#view to invalidating session and logging out the user
def logout(request):
    user = check_validation(request)
    if user:
        token = SessionToken.objects.filter(user = user)
        token.delete()
        return redirect('login')
    else:
        return redirect('login')
