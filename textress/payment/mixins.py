from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth, messages

from braces.views import LoginRequiredMixin, GroupRequiredMixin

from payment.models import Card
from main.models import Hotel
from utils import dj_messages


### STRIPE MIXINS ###

class StripeMixin(object):
    
    def get_context_data(self, **kwargs):
        context = super(StripeMixin, self).get_context_data(**kwargs)
        context['publishable_key'] = settings.STRIPE_PUBLIC_KEY
        return context


### CARD MIXINS ###

class HotelCardOnlyMixin(object):
    '''Make sure that the Card belongs to the Hotel.'''

    def dispatch(self, request, *args, **kwargs):
        self.hotel = self.request.user.profile.hotel

        self.short_pk = kwargs['pk']

        if self.short_pk not in (
            Card.objects.filter(customer=self.hotel.customer)
                        .values_list('short_pk', flat=True)):
            raise Http404

        return super(HotelCardOnlyMixin, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        try:
            return Card.objects.get(short_pk=self.short_pk)
        except ObjectDoesNotExist:
            raise Http404