from django.contrib import admin
from twi_futurecolors.models import Tweet, TwMention

__author__ = 'akamoroz'

class TweetAdmin(admin.ModelAdmin):
    pass

class TwMentionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Tweet, TweetAdmin)
admin.site.register(TwMention, TwMentionAdmin)
