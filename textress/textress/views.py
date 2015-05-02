from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View, TemplateView

from braces.views import GroupRequiredMixin


### ERROR PAGES ###

def handler404(request):
    response = render_to_response('error/404.html', {},
        context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('error/500.html', {},
        context_instance=RequestContext(request))
    response.status_code = 500
    return response