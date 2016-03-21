from django import forms
from captcha.fields import CaptchaField
from django.contrib.auth.models import User
import datetime


attrs_dict = {'class': 'form-control', 'style': 'width:100%', 'required': 'required'}
attrs_profile_dict = {'class': 'form-control', 'style': 'width:100%'}

class UserForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the password is entered twice and matches,
    and that the email/username is not already taken.
    """
    first_name = forms.CharField(max_length=30, label='First Name', strip=True,
                                widget=forms.TextInput(attrs=dict(attrs_dict,
                                                        placeholder='First Name')),
                                error_messages={'required': 'Please enter your first name'})
    last_name = forms.CharField(max_length=30,
                                widget=forms.TextInput(attrs=dict(attrs_dict,
                                                        placeholder='Last Name')),
                                strip=True,
                                error_messages={'required': 'Please enter your last name'})
    email = forms.EmailField(widget=forms.EmailInput(attrs=dict(attrs_dict,
                            maxlength=200, placeholder='Email')),
                            label='Email',
                            strip=True,
                            error_messages={'required': 'Please enter your email'})
    password = forms.CharField(widget=forms.PasswordInput(attrs=dict(attrs_dict,
                                                            placeholder='Password')),
                                label='Password', help_text='Minimum of 6 characters',
                                error_messages={'required': 'Please enter your password'})
    confirmpassword = forms.CharField(widget=forms.PasswordInput(attrs=dict(attrs_dict,
                                                                placeholder='Confirm Password')),
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

class UserProfileForm(forms.Form):
    """
    Form for User Profile
    """
    first_name = forms.CharField(max_length=30, label='First Name', strip=True,
                                widget=forms.TextInput(attrs=dict(attrs_dict,
                                                        placeholder='First Name')),
                                error_messages={'required': 'Please enter your first name'})
    last_name = forms.CharField(max_length=30,
                                widget=forms.TextInput(attrs=dict(attrs_dict,
                                                        placeholder='Last Name')),
                                strip=True,
                                error_messages={'required': 'Please enter your last name'})
    email = forms.EmailField(widget=forms.EmailInput(attrs=dict(attrs_dict,
                            maxlength=200, placeholder='Email')),
                            label='Email',
                            strip=True,
                            error_messages={'required': 'Please enter your email'})

    contactno = forms.IntegerField(label='Contact No.',
                                    widget=forms.TextInput(attrs=dict(attrs_profile_dict,
                                                        placeholder='Contact No')))
    address = forms.CharField(label='Address',
                            widget=forms.Textarea, required=False)
    aboutme = forms.CharField(label='About Me',
                                widget=forms.Textarea,
                                required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserProfileForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.user.id).count():
            raise forms.ValidationError(u'Email address already exist!.')
        return email


class ChangePasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs=dict(
                attrs_dict,
                placeholder='Password',
            )
        ),
        label='Password',
        error_messages={'required': 'Please enter your new Password'}
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs=dict(
                attrs_dict,
                placeholder='Confirm Password',
            )
        ),
        label='Confirm Password',
        error_messages={'required': 'Please enter your confirm password'}
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_confirm_password(self):
        """
        Validates the password & confirm password.

        """
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data

class UploadUserPicForm(forms.Form):
    """
    Form for accessing the userprofile table fields.

    Validates the user details before saving it to DB.
    """
    photo = forms.FileField(
        widget=forms.FileField,
        label='Upload Field',
        )

class PostForm(forms.Form):

    CHOICES = [('publish', 'Publish'), ('draft', 'Draft')]

    title = forms.CharField(label='Title',
                            widget=forms.TextInput(attrs=dict(attrs_dict,
                            placeholder='Title')), error_messages={'required': 'Please enter title'})
    body = forms.CharField(label='Body',
                            widget=forms.Textarea(attrs=dict(attrs_dict)), error_messages={'required': 'Please enter body'})
    tags = forms.CharField(label='Tags',
                            widget=forms.DateInput(attrs=dict(attrs_dict,
                            placeholder='Tags')), error_messages={'required': 'Please enter tags'})
    status = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(attrs=dict({'required': 'required', 'class':'radiobutton'})), error_messages={'required': 'Please select status'})