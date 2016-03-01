from django import forms
from blogpost.models import User

attrs_dict = {'class': 'required'}


class UserForm(forms.Form):

"""
Form for registering a new user account.

Validates that the password is entered twice and matches,
and that the email/username is not already taken.

"""

first_name = forms.CharField(max_length=30, label='First Name', strip=True)
last_name = forms.CharField(max_length=30,
  widget=forms.TextInput(attrs=attrs_dict),
  label='Last Name', 
  error_messages={'required': 'Please enter your last name'},
  strip=True)
email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
  maxlength=200)),
label='Email',
strip=True)
password = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict),
  label='Password', help_text='Minimum of 6 characters')
confirm_password = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict),
  label=u'Password (again, to catch typos)')

def clean_username(self):
  """
  Validates that the username is not already in use.

  """
  if self.clean_data.get('username', None):
    try:
      user = User.objects.get(username__exact=self.clean_data['username'])
    except User.DoesNotExist:
      return self.clean_data['username']
      raise forms.ValidationError(u'The username "%s" is already taken. Please choose another.' % self.clean_data['username'])

      def clean_confirm_password(self):
        """
        Validates that the two password inputs match.

        """
        if self.clean_data.get('password1', None) and self.clean_data.get('password2', None) and \
        self.clean_data['password1'] == self.clean_data['password2']:
        return self.clean_data['password2']
        raise forms.ValidationError(u'You must type the same password each time')