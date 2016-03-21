"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from blog.views import dashboard_view

urlpatterns = [
    url(r'^(?P<filename>(robots.txt)|(humans.txt))$', dashboard_view, name='dashboard'),
]

urlpatterns += i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^$', dashboard_view, name='dashboard'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': 'dashboard'}, name='logout'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
    url(r'^blog/', include('blogpost.urls', namespace='blogpost')),
)
