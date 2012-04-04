# Create your views here.
from django.views.generic import TemplateView

class BaseView(TemplateView):
    template_name = "base.html"