from django.conf.urls import patterns, url
from blogpost.views import *

urlpatterns = patterns('',
		url(r'^signup/', signup_view, name='signup'),
		url(r'^change-password/', change_password_view, name='change-password'),
		url(r'^activate/(?P<activation_key>\w+)/$', activate_view),
		url(r'^profile/edit/$', edit_profile_view, name='edit'),
		url(r'^profile/(?P<userid>\d+)', profile_view, name='profile'),
		url(r'^profile/', profile_view, name='profile'),
		url(r'^upload-pic/', upload_pic, name='upload-pic'),
		url(r'^edit/(?P<postid>\d+)/$', edit_blog_view, name="addblog"),
		url(r'^posts/', posts_view, name='posts'),
		url(r'^my-blog/', my_blog_view, name='my-blog'),
		url(r'^(?P<slug>[\w-]+)-(?P<postid>\w+)/$', blog_detail_view, name='blog_detail'),
		url(r'^comment/delete/$', delete_comment_view, name="addcomment"),
		url(r'^comment/(?P<postid>\w+)/$', add_comment_view, name="addcomment"),
		url(r'^add/', add_blog_view, name="editblog"),
	)