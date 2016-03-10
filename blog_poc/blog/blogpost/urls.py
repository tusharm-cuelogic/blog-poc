from django.conf.urls import patterns, url
from blogpost.views import *

urlpatterns = patterns('',
		url(r'^signup/', signup_view, name='signup'),
		url(r'^change-password/', change_password_view, name='change-password'),
		url(r'^activate/(?P<activation_key>\w+)/$', activate_view),
		url(r'^profile/edit/$', edit_profile_view, name='edit'),
		url(r'^profile/', profile_view, name='profile'),
		url(r'^add/', add_blog_view, name="editblog"),
		url(r'^edit/', edit_blog_view, name="addblog"),
		url(r'^upload-pic/', upload_pic, name='upload-pic'),
		url(r'^posts/', posts_view, name='posts'),
	)