from django import forms
from captcha.fields import CaptchaField
from django.contrib.auth.models import User

attrs_dict = {'class': 'form-control', 'style': 'width:100%', 'required': 'required'}

class UserForm(forms.Form):
	"""
	Form for registering a new user account.

	Validates that the password is entered twice and matches,
	and that the email/username is not already taken.
	"""

	first_name = forms.CharField(max_length=30, label='First Name', strip=True,
								widget=forms.TextInput(attrs=attrs_dict),
								error_messages={'required': 'Please enter your first name'})
	last_name = forms.CharField(max_length=30,
								widget=forms.TextInput(attrs=attrs_dict), strip=True,
								error_messages={'required': 'Please enter your last name'})
	email = forms.EmailField(widget=forms.EmailInput(attrs=dict(attrs_dict,
							maxlength=200)),
							label='Email',
							strip=True,
							error_messages={'required': 'Please enter your email'})
	password = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict),
								label='Password', help_text='Minimum of 6 characters',
								error_messages={'required': 'Please enter your password'})
	confirmpassword = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict),
										label='Confirm Password',
										error_messages={'required': 'Please enter your confirm password'})
	captcha = CaptchaField()

	def clean_email(self):
		"""
		Validates that the email is not already in use.

		"""
		email = self.cleaned_data['email']
		if email != "":
			try:
				user = User.objects.get(email__exact=email)
			except User.DoesNotExist:
				return ""
			else:
				raise forms.ValidationError(u'The email "%s" is already taken. Please choose another.' % email)


	def clean_confirmpassword(self):
		"""
		Validates that the two password inputs match.

		"""
		password = self.cleaned_data['password']
		confirm_password = self.cleaned_data['confirmpassword']
		if password != confirm_password:
			raise forms.ValidationError(u'You must type the same password each time')
