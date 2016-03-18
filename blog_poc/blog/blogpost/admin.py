from django.contrib import admin

from .models import Post, UserProfile, Comment

class PostAdmin(admin.ModelAdmin):
    fields = ['title', 'content', 'slug', 'tags', 'status', 'userid']
    list_filter = ['pub_date']
    search_fields = ['title']

admin.site.register(Post, PostAdmin)
admin.site.register(UserProfile)
admin.site.register(Comment)