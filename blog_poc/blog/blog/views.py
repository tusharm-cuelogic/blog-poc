from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from blogpost.models import *
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect

def dashboard_view(request):

	allPost = Post.objects.filter(status='publish').order_by('-pub_date')[:5]
	user_blog_data_list = []
	if allPost:
		for posts in allPost:
			user_blog_data = {}
			try:
				user_blog_data['post_info'] = posts
				user_blog_data['user_obj'] = User.objects.get(id=posts.userid.id)
			except:
				return "Object does not exist"
			user_blog_data_list.append(user_blog_data)
		user_dict = {'blog_post': user_blog_data_list}
	else:
		user_dict = {}
	return render(request, 'dashboard.html', user_dict)
