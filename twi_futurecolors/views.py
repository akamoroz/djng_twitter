# Create your views here.
from django.views.generic import TemplateView
from twi_futurecolors.models import TwMention

class BaseView(TemplateView):
    template_name = "base.html"

def search_mentions(request, username):
    user,created = TwMention.objects.get_or_create(user=username)
    #if created:
    user.check_updates()
    return
