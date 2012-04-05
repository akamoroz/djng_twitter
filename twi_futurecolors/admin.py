from django.contrib import admin
from twi_futurecolors.models import Tweet, TwUser

__author__ = 'akamoroz'

class TweetAdmin(admin.ModelAdmin):
    pass

class TwUserAdmin(admin.ModelAdmin):
    pass

admin.site.register(Tweet, TweetAdmin)
admin.site.register(TwUser, TwUserAdmin)
