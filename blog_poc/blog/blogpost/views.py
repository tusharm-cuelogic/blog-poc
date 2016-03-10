
import random, sha, re, os, shutil
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.utils.text import slugify
from blogpost.forms import *
from blogpost.models import *
from django.conf import settings
from django.template import Context, loader
from datetime import datetime
from django.http import HttpResponseRedirect


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

def edit_profile_view(request):

    id = request.user.id

    if id is not None:
        userprofileinfo = get_object_or_404(UserProfile, user_id=id)
    else:
        userprofileinfo = None

    userprofiledata = {'first_name': request.user.first_name,
                        'last_name': request.user.last_name,
                        'email': request.user.email,
                        'contactno': userprofileinfo.contact_no,
                        'address': userprofileinfo.address,
                        'aboutme': userprofileinfo.about_me}

    if request.method == 'POST':
        userprofileform = UserProfileForm(request.user, request.POST)

        if userprofileform.is_valid:

            first_name = request.POST.get('first_name', None)
            last_name = request.POST.get('last_name', None)
            email = request.POST.get('email', None)
            contact_no = request.POST.get('contactno', None)
            address = request.POST.get('address', None)
            aboutme = request.POST.get('aboutme', None)

            User.objects.filter(id=id).update(first_name=first_name,
                                                last_name=last_name,
                                                email=email)

            UserProfile.objects.filter(user_id=id).update(contact_no=contact_no,
                                                            address=address,
                                                            about_me=aboutme)

            success_message = "Profile updated successfully"

            messages.add_message(request, messages.INFO, success_message)
            return HttpResponseRedirect(reverse('profile'))
    else:
        userprofileform = UserProfileForm(request.user, initial=userprofiledata)

    return render(request, 'blogpost/edit_profile.html',
                {'userprofileform': userprofileform})

def profile_view(request):
    id = request.GET.get('id', None)

    if id is None:
        userprofileinfo = get_object_or_404(UserProfile, user_id=request.user.id)
        return render(request, 'blogpost/profile.html',
                        {'userprofileinfo': userprofileinfo})


def change_password_view(request):

    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        users = request.user
        users.set_password(request.POST.get('password', None))
        if form.is_valid():
            user_data = {
                'password': users.password,
            }
            user_data = User.objects.filter(pk=request.user.id).update(**user_data)
            update_session_auth_hash(request, form.user)

            success_message = "Password changed successfully"

            messages.add_message(request, messages.INFO, success_message)
            return HttpResponseRedirect(reverse('profile'))
    else:
        form = ChangePasswordForm(user=request.user)

    return render(request, 'blogpost/change-password.html', {'form': form})


def add_blog_view(request):

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():

            user = User.objects.get(id=request.user.id)
            title = request.POST.get('title', None)
            body = request.POST.get('body', None)
            tags = request.POST.get('tags', None)
            status = request.POST.get('status', None)

            blog_post = Post()
            blog_post.title = title
            blog_post.content = body
            blog_post.tags = tags
            blog_post.status = status
            blog_post.rating = 0
            blog_post.slug = slugify(title)
            blog_post.userid = user
            blog_post.save()

            success_message = "Blog added successfully"

            messages.add_message(request, messages.INFO, success_message)
            return HttpResponseRedirect(reverse('dashboard'))
    else:
        form = PostForm()

    return render(request, 'blogpost/addblog.html', {'form': form})


def edit_blog_view(request):
    id = request.GET.get('id', None)

    if id is not None:
        post = get_object_or_404(Post, id=id)
    else:
        post = None

    postdata = {'title': post.title,
                'body': post.content,
                'tags': post.tags,
                'status': post.status}

    if request.method == 'POST':
        postform = PostForm(request.POST)

        if postform.is_valid:

            title = request.POST.get('title', None)
            body = request.POST.get('body', None)
            tags = request.POST.get('tags', None)
            status = request.POST.get('status', None)

            Post.objects.filter(id=id).update(title=title,
                                                content=body,
                                                tags=tags,
                                                status=status,
                                                modified=datetime.now())

            success_message = "Blog updated successfully"

            messages.add_message(request, messages.INFO, success_message)
            return HttpResponseRedirect(reverse('dashboard'))

    else:
        postform = PostForm(initial=postdata)

    return render(request, 'blogpost/editblog.html', {'form': postform})


def generate_activation_key(new_user):
    salt = sha.new(str(random.random())).hexdigest()[:5]
    activation_key = sha.new(salt + new_user.email).hexdigest()
    return activation_key


def send_activation_email(new_user, activation_key):
    current_domain = settings.SITE_URL
    subject = "Activate your new account at %s" % current_domain
    message_template = loader.get_template('blogpost/activation_email.txt')
    message_context = Context({'site_url': 'http://%s/' % current_domain,
                            'activation_key': activation_key})
    message = message_template.render(message_context)
    send_mail(subject, message, 'no-reply@gmail.com', [new_user.email])

def upload_pic(request):
    if request.method == 'POST':
        form = UploadUserPicForm(request.POST, request.FILES)
        files = request.FILES.get('user_pic', None)
        if files:
            path = default_storage.save(settings.USER_IMAGE_PATH + str(files.name), 
                                        ContentFile(files.read()))
            tmp_file_path = os.path.join(settings.USER_IMAGE_PATH, path)
            photo = files.name
            UserProfile.objects.filter(user_id=request.user.id).update(user_photo=photo)
        else:
            success_message = "Something has went wrong, please try again."
            messages.add_message(request, messages.INFO, success_message)
            return HttpResponseRedirect(reverse('profile'))
    else:
        form = UploadUserPicForm()
    return HttpResponseRedirect(reverse('profile'))
