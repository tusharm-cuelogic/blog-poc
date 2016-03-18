
import random, sha, re, os, shutil
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.text import slugify
from blogpost.forms import *
from blogpost.models import *
from django.db.models import Q
from django.conf import settings
from django.template import Context, loader
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

import nltk
from nltk.tag import pos_tag, map_tag

def authenticated_only(user):
    return (user.is_authenticated())

def signup_view(request):

    if request.user.id:
        return HttpResponseRedirect(reverse('dashboard'))

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
    else:
        return HttpResponseRedirect(reverse('signup'))


@user_passes_test(authenticated_only, login_url="/")
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
                                                email=email,
                                                username=email)

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

def profile_view(request, userid=None):

    if userid is None:
        id = request.user.id
    else:
        id = userid

    userinfo = User.objects.get(id=id)
    userprofileinfo = get_object_or_404(UserProfile, user_id=id)

    if userprofileinfo.user_photo:
        pass
    else:
        userprofileinfo.user_photo = "default.png"

    return render(request, 'blogpost/profile.html',
                    {'userinfo': userinfo,
                    'userprofileinfo': userprofileinfo,
                    'userid': userid})


@user_passes_test(authenticated_only, login_url="/")
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


@user_passes_test(authenticated_only, login_url="/")
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
            return HttpResponseRedirect(reverse('posts'))
    else:
        form = PostForm()

    return render(request, 'blogpost/addblog.html', {'form': form})


@user_passes_test(authenticated_only, login_url="/")
def edit_blog_view(request, postid):

    if postid is not None:
        post = get_object_or_404(Post, id=postid)
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

            Post.objects.filter(id=postid).update(title=title,
                                                content=body,
                                                tags=tags,
                                                status=status,
                                                modified=datetime.now())

            success_message = "Blog updated successfully"

            messages.add_message(request, messages.INFO, success_message)
            return HttpResponseRedirect(reverse('posts'))

    else:
        postform = PostForm(initial=postdata)

    return render(request, 'blogpost/editblog.html', {'form': postform})


@user_passes_test(authenticated_only, login_url="/")
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

def posts_view(request):

    searchType = request.POST.get('search_type', None)
    searchText = request.POST.get('search_text', None)
    dateFrom = request.POST.get('from', None)
    dateTo = request.POST.get('to', None)

    allPost = searchQuery(request)

    user_search_obj = []
    date_search_obj = []
    user_blog_data_list = []

    if searchType:
        user_search_obj = [searchText, searchType]

    if dateFrom and dateTo:
        date_search_obj = [dateFrom, dateTo]

    paginator = Paginator(allPost, 10)
    page = request.GET.get('page')

    try:
        postdata = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        postdata = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        postdata = paginator.page(paginator.num_pages)

    if allPost:
        for posts in postdata:
            user_blog_data = {}
            try:
                user_blog_data['post_info'] = posts
                user_blog_data['user_obj'] = User.objects.get(id=posts.userid.id)
            except:
                return "Object does not exist"
            user_blog_data_list.append(user_blog_data)
        user_dict = {'blog_post': user_blog_data_list, 'pagination_data': postdata}
    else:
        user_dict = {}

    user_dict['search_value'] = user_search_obj
    user_dict['date_search_value'] = date_search_obj

    return render(request, 'blogpost/posts.html', user_dict)

def blog_detail_view(request, **kwargs):
    postid = kwargs['postid']
    post = get_object_or_404(Post, id=postid)

    sizes = [11, 12, 14, 16, 18, 20]

    blog_data = {}
    if post:
        try:
            blog_data['post'] = post
            blog_data['user_obj'] = User.objects.get(id=post.userid.id)
            blog_data['userprofile_obj'] = UserProfile.objects.get(user_id=post.userid.id)

            text = nltk.word_tokenize(post.content)
            posTagged = pos_tag(text)
            simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in posTagged]

            if blog_data['userprofile_obj'].user_photo:
                pass
            else:
                blog_data['userprofile_obj'].user_photo = "default.png"

            comment_list = commentList(postid)
            comment_count = Comment.objects.filter(postid_id=postid).count()

            if not comment_count:
                comment_count = 0
        except:
            return "Object does not exist"

        user_dict = {'blog_post': blog_data, 'comment_list': comment_list,
                    'comment_count': comment_count, 'simplifiedTags': simplifiedTags, 'sizes': sizes}

    return render(request, 'blogpost/blog.html', user_dict)


@user_passes_test(authenticated_only, login_url="/")
def my_blog_view(request):

    searchType = request.POST.get('search_type', None)
    searchText = request.POST.get('search_text', None)
    dateFrom = request.POST.get('from', None)
    dateTo = request.POST.get('to', None)

    allPost = myBlogSearchQuery(request)

    user_search_obj = []
    date_search_obj = []
    user_blog_data_list = []

    if searchType:
        user_search_obj = [searchText, searchType]

    if dateFrom and dateTo:
        date_search_obj = [dateFrom, dateTo]

    paginator = Paginator(allPost, 10)
    page = request.GET.get('page')

    try:
        postdata = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        postdata = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        postdata = paginator.page(paginator.num_pages)

    if allPost:
        for posts in postdata:
            user_blog_data = {}
            try:
                user_blog_data['post_info'] = posts
                user_blog_data['user_obj'] = User.objects.get(id=posts.userid.id)
            except:
                return "Object does not exist"
            user_blog_data_list.append(user_blog_data)
        user_dict = {'blog_post': user_blog_data_list, 'pagination_data': postdata}
    else:
        user_dict = {}

    user_dict['search_value'] = user_search_obj
    user_dict['date_search_value'] = date_search_obj
    user_dict['my_blog'] = 'my_blog'

    return render(request, 'blogpost/posts.html', user_dict)


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


def searchQuery(request):
    searchType = request.POST.get('search_type', None)
    searchText = request.POST.get('search_text', None)

    if searchType:

        if not searchType == "author" and not searchType == "date":
            searchField = str(searchType) + str('__icontains')
            allPost = Post.objects.filter(status='publish', **{searchField: searchText}).order_by('-pub_date')

        elif searchType == "date":
            dateFrom = request.POST.get('from', None) + " 00:00:00"
            dateTo = request.POST.get('to', None) + " 23:59:00"

            if dateFrom and dateTo:
                allPost = Post.objects.filter(pub_date__range=[dateFrom, dateTo]).order_by('-pub_date')
        else:
            allUserData = User.objects.filter(Q(first_name__contains=searchText) | Q(last_name__contains=searchText), is_active=1)
            user_ids = []
            for user in allUserData:
                user_ids.append(user.id)
            allPost = Post.objects.filter(status='publish', userid_id__in=user_ids).order_by('-pub_date')
    else:
        allPost = Post.objects.filter(status='publish').order_by('-pub_date')

    return allPost


def myBlogSearchQuery(request):
    searchType = request.POST.get('search_type', None)
    searchText = request.POST.get('search_text', None)

    if searchType:

        if not searchType == "date":
            searchField = str(searchType) + str('__icontains')
            allPost = Post.objects.filter(status='publish', **{searchField: searchText, 'userid_id': request.user.id}).order_by('-pub_date')

        elif searchType == "date":
            dateFrom = request.POST.get('from', None) + " 00:00:00"
            dateTo = request.POST.get('to', None) + " 23:59:00"

            if dateFrom and dateTo:
                allPost = Post.objects.filter(pub_date__range=[dateFrom, dateTo], userid_id=request.user.id).order_by('-pub_date')
    else:
        allPost = Post.objects.filter(status='publish', userid_id=request.user.id).order_by('-pub_date')

    return allPost

@csrf_exempt
def add_comment_view(request, postid):

    comment = request.POST.get("comment")
    comment_info = {}
    if postid and comment:
        comment_data = Comment()
        comment_data.comment = comment
        comment_data.postid_id = postid
        comment_data.userid_id = request.user.id
        comment_data.save()

        comment_obj = Comment.objects.get(id=comment_data.id)

        if comment_obj:
            comment_info['comments'] = comment_obj
            comment_info['user_obj'] = User.objects.get(id=comment_obj.userid_id)
            comment_info['userprofile_obj'] = UserProfile.objects.get(user_id=comment_obj.userid_id)

        send_comment_email(request, comment_obj)

    if request.is_ajax():
        html = render_to_string('blogpost/comment.html', {'comment_info': comment_info})
    return HttpResponse(html)

def commentList(postid):
    comment_obj = Comment.objects.filter(postid_id=postid).order_by('-timestamp')

    comment_list = []
    if comment_obj:
        for comments in comment_obj:
            comment_data = {}
            comment_data['comment_info'] = comments
            comment_data['comment_user_obj'] = User.objects.get(id=comments.userid_id)
            comment_data['comment_userprofile_obj'] = UserProfile.objects.get(user_id=comments.userid_id)

            if comment_data['comment_userprofile_obj'].user_photo:
                pass
            else:
                comment_data['comment_userprofile_obj'].user_photo = "default2.png"

            comment_list.append(comment_data)
    return comment_list

def send_comment_email(request, comment_info):
    current_domain = settings.SITE_URL
    subject = "got a comment on your blog"
    message_template = loader.get_template('blogpost/comment_email.txt')

    post = Post.objects.get(id=comment_info.postid_id)
    user_data = User.objects.get(id=post.userid_id)

    if post.userid_id != request.user.id:
        message_context = Context({'site_url': 'http://%s/' % current_domain,
                                'author_first_name': user_data.first_name,
                                'author_last_name': user_data.last_name,
                                'first_name': request.user.first_name,
                                'last_name': request.user.last_name,
                                'blog_url': '%s/blog/%s-%s' % (current_domain, post.slug, post.id),
                                'title': post.title,
                                'comment': comment_info.comment})

        message = message_template.render(message_context)
        send_mail(subject, message, 'no-reply@gmail.com', [user_data.email])


@csrf_exempt
def delete_comment_view(request):

    commentid = request.POST.get("commentid")

    if commentid:
        comment = get_object_or_404(Comment, id=commentid)
        comment.delete()
        comment_response = "success"
    else:
        comment_response = "error"

    return HttpResponse(comment_response)
