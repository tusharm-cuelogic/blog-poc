
import random, sha, re
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from blogpost.forms import UserForm
from blogpost.models import UserProfile
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader


def signup_view(request):

	if request.method == 'POST':
		form = UserForm(request.POST)

		if form.is_valid():

			# first_name = form.cleaned_data['first_name']
			# last_name = form.cleaned_data['last_name']
			# email = form.cleaned_data['email']
			# password = form.cleaned_data['password']

			first_name = request.POST.get('first_name', None)
			last_name = request.POST.get('last_name', None)
			email = request.POST.get('email', None)
			password = request.POST.get('password', None)
			
			
			new_user = User.objects.create_user(username=email, password=password, email=email)
				
			new_user.first_name = first_name
			new_user.last_name = last_name
			new_user.is_active = False
			new_user.save()
			
			# Generate a salted SHA1 hash to use as a key.
			activation_key = generate_activation_key(new_user)

			userprofile = UserProfile()
			userprofile.user_id = new_user.id
			userprofile.activation_key = activation_key
			userprofile.save()
				
			send_activation_email(new_user, activation_key)

			success_message = "Almost done! Please check your email '%s' and click on the verification link we just you" % new_user.email

			messages.add_message(request, messages.INFO, success_message)
			return HttpResponseRedirect(reverse('dashboard'))
	else:
		form = UserForm()

	return render(request, 'blogpost/signup.html', {'form': form})


def activate_view(request, activation_key):

	if activation_key:
		user_profile = ""
		try:
			user_profile = UserProfile.objects.get(activation_key=activation_key)
		except UserProfile.DoesNotExist:
			messages.add_message(request, messages.INFO, "Invalid email verificaion link")
			return HttpResponseRedirect(reverse('dashboard'))

		if user_profile.activation_key:
			user = user_profile.user
			#user = User.objects.get(id=user_profile.user_id)

			if not user.is_active:
				user.is_active = True
				user.save()

				success_message = "Congratulations, you have successfully verified your email '%s'. \n Please login to access your account." % user.email
				messages.add_message(request, messages.INFO, success_message)
				return HttpResponseRedirect(reverse('login'))
			else:
				success_message = "your email '%s' is already verified" % user.email
				messages.add_message(request, messages.INFO, success_message)
				return HttpResponseRedirect(reverse('dashboard'))
	return False


def generate_activation_key(new_user):
	salt = sha.new(str(random.random())).hexdigest()[:5]
	activation_key = sha.new(salt+new_user.email).hexdigest()
	return activation_key


def send_activation_email(new_user, activation_key):
	current_domain = settings.SITE_URL
	subject = "Activate your new account at %s" % current_domain
	message_template = loader.get_template('blogpost/activation_email.txt')
	message_context = Context({'site_url': 'http://%s/' % current_domain,
							'activation_key': activation_key})
	message = message_template.render(message_context)
	send_mail(subject, message, 'no-reply@gmail.com', [new_user.email])

