# Create your views here.
import logging
from urllib2 import URLError
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic import TemplateView
import twitter
from twi_futurecolors.models import TwUser, Tweet

class BaseView(TemplateView):
    template_name = "base.html"

def search_mentions(request, username):
    user,created = TwUser.objects.get_or_create(user=username)
    #if created:
    try:
        user.check_updates()
    except (twitter.TwitterError, URLError), e:
        logging.getLogger(__name__).error(str(e))
    tweets = Tweet.objects.filter(mentions=user)
    return render_to_response('app.html', {'user': user,'tweets':tweets},
        context_instance=RequestContext(request))
