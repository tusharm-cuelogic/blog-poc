from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
	user = models.OneToOneField(User)
	contact_no = models.CharField(max_length=20, null=True)
	address = models.TextField()
	about_me = models.TextField()
	socialmedia_key = models.CharField(max_length=200)
	user_photo = models.FileField(upload_to=None, max_length=200,)
	activation_key = models.CharField(max_length=40)
	key_generated = models.DateTimeField(auto_now_add=True)


class Post(models.Model):

	title = models.CharField(max_length=200)
	content = models.TextField()
	pub_date = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	slug = models.SlugField(max_length=200)
	tags = models.CharField(max_length=200)
	status = models.CharField(max_length=10)
	rating = models.IntegerField()
	userid = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(models.Model):

	comment = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)
	userid = models.ForeignKey(User, on_delete=models.CASCADE)
	postid = models.ForeignKey(Post, on_delete=models.CASCADE)