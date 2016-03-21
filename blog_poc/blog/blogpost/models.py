from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
	user = models.OneToOneField(User)
	contact_no = models.CharField(max_length=20, null=True)
	address = models.TextField()
	about_me = models.TextField()
	socialmedia_key = models.CharField(max_length=200, blank=True, null=True,)
	user_photo = models.FileField(upload_to='static/blog/user_profile_img',
									max_length=200,
									blank=True,
									null=True,)
	activation_key = models.CharField(max_length=40, blank=True, null=True,)
	key_generated = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.user.first_name+" "+self.user.last_name


class Post(models.Model):

	title = models.CharField(max_length=200)
	content = models.TextField()
	pub_date = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	slug = models.SlugField(max_length=200, blank=True, null=True,)
	tags = models.CharField(max_length=200)
	status = models.CharField(max_length=10)
	rating = models.IntegerField(blank=True, null=True,)
	userid = models.ForeignKey(User, on_delete=models.CASCADE)

	def __unicode__(self):
		return self.title


class Comment(models.Model):

	comment = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)
	userid = models.ForeignKey(User, on_delete=models.CASCADE)
	postid = models.ForeignKey(Post, on_delete=models.CASCADE)

	def __unicode__(self):
		return self.comment