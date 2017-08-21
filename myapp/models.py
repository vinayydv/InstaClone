# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.db import models
from uuid import uuid4
from paralleldots import set_api_key, get_api_key
from paralleldots import similarity,emotion, sentiment

#api key for parallel dots sentiment analysis
set_api_key("rpMuzF79DEc91DyPeTe3Dgs1EZ3CYjDC2YRxRGyQQoo")


#usermodel to store user details in sign up.
class UserModel(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=120)
    username = models.CharField(max_length=120)
    password = models.CharField(max_length=240)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<UserModel : %s>"%(self.username)


#model to store session token details
class SessionToken(models.Model):
    user = models.ForeignKey(UserModel)
    session_token = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def create_token(self):
        self.session_token = str(uuid4())


#model to store a post details
class PostModel(models.Model):
    user = models.ForeignKey(UserModel)
    image = models.FileField(upload_to='user_images')
    image_url = models.CharField(max_length=255)
    caption = models.CharField(max_length=240)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    @property
    #shows the number of like on a post
    def like_count(self):
        return self.likemodel_set.count()

    @property
    #to implement sentiment analysis using parallel dots api
    def caption_review(self):
        r = sentiment(str(self.caption))
        print r
        if r['sentiment'] > 0.5:
            review = 'Positive'
        else:
            review = 'Negative'
        return review


    @property
    #to show comments ona post
    def comments(self):
        return CommentModel.objects.filter(post=self).order_by('-created_on')


#stores the details of user who liked the post
class LikeModel(models.Model):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


#stores details of comment
class CommentModel(models.Model):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    comment_text = models.CharField(max_length=555)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)