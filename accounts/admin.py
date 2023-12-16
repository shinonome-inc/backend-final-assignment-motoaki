from django.contrib import admin

from .models import Tweet, User

admin.site.register(User)
admin.site.register(Tweet)
