
import random, sha, re
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from blogpost.forms import UserForm
from blogpost.models import UserProfile
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader

# Create your views here.

def signup_view(request):

	if request.method == 'POST':
		form = UserForm(request.POST)

		if form.is_valid():

			first_name = request.POST.get('first_name', None)
			last_name = request.POST.get('last_name', None)
			email = request.POST.get('email', None)
			password = request.POST.get('password', None)
			confirm_password = request.POST.get('confirmpassword', None)

			email_error = ""
			password_error = ""
			email_error = clean_email(request, email)
			password_error = check_confirm_password(request, password, confirm_password)

			if email_error == "" and password_error == "":
				new_user = User.objects.create_user(username=email,
													password=password,
													email=email)
				new_user.is_active = False
				new_user.first_name = first_name
				new_user.last_name = last_name
			
				# Generate a salted SHA1 hash to use as a key.
				salt = sha.new(str(random.random())).hexdigest()[:5]
				activation_key = sha.new(salt+new_user.email).hexdigest()

				new_user.activation_key = activation_key
				new_user.save()

				current_domain = settings.SITE_URL
				subject = "Activate your new account at %s" % current_domain
				message_template = loader.get_template('blogpost/activation_email.txt')
				message_context = Context({'site_url': 'http://%s/' % current_domain,
										'activation_key': activation_key})
				message = message_template.render(message_context)
				send_mail(subject, message, 'no-reply@gmail.com', [new_user.email])

				success_message = "Registration successful! An email will be sent to the '%s' with an activation link to click to make the account active" % new_user.email

				messages.add_message(request, messages.INFO, success_message)
				return HttpResponseRedirect(reverse('dashboard'))
	else:
		form = UserForm()

	return render(request, 'blogpost/signup.html', {'form': form})


def activate_view(request, activation_key):
	activation_key = activation_key.lower()

	if re.match('[a-f0-9]{40}', activation_key):
		user_profile = ""
		try:
			user_profile = UserProfile.objects.get(activation_key=activation_key)
		except UserProfile.DoesNotExist:
			 return False
		if not user_profile.activation_key_expired():
			
			user = user_profile.user
			user.is_active = True
			user.save()
			return user
	return False


def clean_email(request, email):
	"""
	Validates that the email is not already in use.

	"""
	if email != "":
		try:
			user = User.objects.get(email__exact=email)
		except User.DoesNotExist:
			return ""
		else:
			messages.add_message(request, messages.INFO, 'The email "%s" is already taken. Please choose another.' % email)
			return "error"


def check_confirm_password(request, password, confirm_password):
	"""
	Validates that the two password inputs match.

	"""
	if password != confirm_password:
		messages.add_message(request, messages.INFO, 'You must type the same password each time')
		return "error"
	else:
		return ""
