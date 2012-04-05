from django.conf.urls import patterns, include, url
from twi_futurecolors.views import BaseView

__author__ = 'akamoroz'


urlpatterns = patterns('',
                        (r'^tag/$', BaseView.as_view()),
                        (r'^(?P<username>\w+)/$', 'twi_futurecolors.views.search_mentions'),
                       )
