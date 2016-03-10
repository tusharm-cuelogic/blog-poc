from django.conf.urls import patterns, url
from blogpost.views import signup_view, activate_view

urlpatterns = patterns('',
		url(r'^signup/', signup_view, name='signup'),
		url(r'^activate/(?P<activation_key>\w+)/$', activate_view),
	)