from django.conf.urls import patterns, include, url
from django.contrib import admin
from blogpost.views import signup_view, activate_view

urlpatterns = patterns('',
		url(r'^signup/', signup_view, name='signup'),
		(r'^activate/(?P<activation_key>\w+)/$', activate_view),
	)