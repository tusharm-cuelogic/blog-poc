from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect

def dashboard_view(request):

	return render(request, 'dashboard.html')
