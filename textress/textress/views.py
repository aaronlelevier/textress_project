from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View, TemplateView

from braces.views import GroupRequiredMixin


### ERROR PAGES ###

def handler404(request):
    response = render_to_response('404.html', {},
        context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {},
        context_instance=RequestContext(request))
    response.status_code = 500
    return response


### ACCESS MIXINS ###

class AdminGroupView(GroupRequiredMixin, View):
    group_required = 'hotel_admin'
    

class ManagerGroupView(GroupRequiredMixin, View):
    group_required = ['hotel_admin', 'hotel_manager']


### INFO ###

class TermsView(TemplateView):
    template_name = 'terms_and_conditions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = "Textress"
        context['LLC'] = "Aronysidoro LLC."
        return context