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


### STRIPE MIXINS ###

class StripeMixin(object):
    
    def get_context_data(self, **kwargs):
        context = super(StripeMixin, self).get_context_data(**kwargs)
        context['publishable_key'] = settings.STRIPE_PUBLIC_KEY
        return context


### ACCT COST MIXINS ###

class AcctCostContextMixin(object):

    def get_context_data(self, **kwargs):
        context = super(AcctCostContextMixin, self).get_context_data(**kwargs)
        context['acct_cost'] = self.hotel.acct_cost
        return context


### HOTEL MIXINS ###

class HotelContextMixin(object):
    '''Add Hotel Obj to Context.'''
    
    def get_context_data(self, **kwargs):
        context = super(HotelContextMixin, self).get_context_data(**kwargs)
        context['hotel'] = self.hotel
        return context


class HotelUserMixin(HotelContextMixin):
    "User must have a Hotel attr."
    def dispatch(self, *args, **kwargs):
        try:
            self.hotel = self.request.user.profile.hotel
        except AttributeError:
            messages.warning(self.request, "No Hotel associated with this account.")

        # TODO: Redirect to an alert page that funds need to be added
        if self.hotel and not self.hotel.active:
            # raise Http404
            messages.warning(self.request, "The Hotel associated with this account is not active.")
            
        return super(HotelUserMixin, self).dispatch(*args, **kwargs)


class HotelAdminCheckMixin(HotelContextMixin):
    "Only the Admin for the Hotel can access this page when using this mixin"
    def dispatch(self, *args, **kwargs):
        admin_hotel = get_object_or_404(Hotel, admin_id=self.request.user.id)
        if admin_hotel != self.hotel:
            raise Http404
        return super(HotelAdminCheckMixin, self).dispatch(*args, **kwargs)


class AdminOnlyMixin(HotelContextMixin, GroupRequiredMixin, View):
    '''Only the Admin of the Hotel can access.'''
    
    group_required = "hotel_admin"
    
    def dispatch(self, request, *args, **kwargs):
        # Login Required
        if not request.user.is_authenticated():
            return redirect_to_login(request.get_full_path())

        self.hotel = self.request.user.profile.hotel
        
        # test only Admin allowed
        if request.user.id != self.hotel.admin_id:
            raise Http404
        
        return super(AdminOnlyMixin, self).dispatch(request, *args, **kwargs)


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