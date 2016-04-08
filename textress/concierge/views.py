from django.conf import settings
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from braces.views import (LoginRequiredMixin, SetHeadlineMixin, CsrfExemptMixin,
    StaticContextMixin)
from twilio import twiml
from ws4redis.publisher import RedisPublisher

from concierge.models import Message, Guest, Trigger
from concierge.helpers import process_incoming_message, convert_to_json_and_publish_to_redis
from concierge.forms import GuestForm
from concierge.mixins import GuestListContextMixin
from concierge.permissions import IsManagerOrAdmin
from concierge.tasks import check_twilio_messages_to_merge, trigger_send_message
from main.mixins import HotelUserMixin
from utils import DeleteButtonMixin


class ReceiveSMSView(CsrfExemptMixin, TemplateView):
    '''
    Main SMS Receiving endpoint for url to be configured on Twilio.
    '''
    template_name = 'blank.html'

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ReceiveSMSView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, 'blank.html', content_type="text/xml")

    def post(self, request, *args, **kwargs):
        # must return this to confirm SMS received for Twilio API
        resp = twiml.Response()
        # if a msg is returned, attach and reply to Guest
        msg, reply = process_incoming_message(data=request.POST)
        # Incoming Message from Guest
        convert_to_json_and_publish_to_redis(msg)
        # Auto-reply Logic
        if reply and reply.message:
            resp.message(reply.message)
            # delay 5 seconds, query Twilio for this Guest, and find any 
            # missing SMS for Today, and merge them into the DB            
            check_twilio_messages_to_merge.apply_async(
                (msg.guest,),
                countdown=5
            )

        return HttpResponse(str(resp), content_type='text/xml')


class SendWelcomeView(LoginRequiredMixin, SetHeadlineMixin, StaticContextMixin,
    HotelUserMixin, TemplateView):
    '''
    Angular View
    ------------
    Bulk send welcome messages.
    '''
    headline = "Send Welcome"
    template_name = "concierge/send_welcome.html"
    static_context = {'headline_small': 'Send to up to 10 guests.'}

    def get_context_data(self, **kwargs):
        context = super(SendWelcomeView, self).get_context_data(**kwargs)
        context['welcome_message'] = Trigger.objects.get_welcome_message(hotel=self.hotel)
        return context


###############
# GUEST VIEWS #
###############

class GuestBaseView(LoginRequiredMixin, SetHeadlineMixin, HotelUserMixin, View):
    headline = "Guest View"
    model = Guest


class GuestListView(GuestBaseView, ListView):
    '''
    Angular View
    ------------
    Lists all Guests w/ links for Detail, Update, Delete.
    '''
    headline = "Guest List"


class GuestDetailView(GuestBaseView, GuestListContextMixin, DetailView):
    '''
    Angular View
    ------------
    Guest Message View to Send/Receive SMS from.
    '''
    def get(self, request, *args, **kwargs):
        """All Messages should be marked as 'read=True' when the User 
        goes to the Guests' DetailView."""
        # initialize chat connection
        RedisPublisher(facility='foobar', broadcast=True)
        # mark all messages as 'read'
        self.object = self.get_object()
        Message.objects.filter(guest=self.object, read=False).update(read=True)
        check_twilio_messages_to_merge(self.object)

        return super(GuestDetailView, self).get(request, *args, **kwargs)

    def get_headline(self):
        return u"{} Detail".format(self.object)

    def get_context_data(self, **kwargs):
        context = super(GuestDetailView, self).get_context_data(**kwargs)
        context.update(groups=Group.objects.all())
        return context

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(GuestDetailView, self).dispatch(*args, **kwargs)


class GuestCreateView(GuestBaseView, GuestListContextMixin, CreateView):
    
    headline = "Add a Guest"
    template_name = 'cpanel/form.html'
    model = Guest
    form_class = GuestForm
    success_url = reverse_lazy('concierge:guest_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.hotel = self.hotel
        self.object.save()
        trigger_send_message(self.object.id, "check_in")
        return super(GuestCreateView, self).form_valid(form)


class GuestUpdateView(GuestBaseView, GuestListContextMixin, UpdateView):

    headline = "Update Guest"
    template_name = 'cpanel/form.html'
    model = Guest
    form_class = GuestForm

    def get_form_kwargs(self):
        "Set Guest as a form attr."
        kwargs = super(GuestUpdateView, self).get_form_kwargs()
        kwargs['guest'] = self.object
        return kwargs  


class GuestDeleteView(GuestBaseView, DeleteButtonMixin, TemplateView):
    '''
    Hide only. Don't `delete` any guest records b/c don't want to
    delete the related `Messages`.
    '''
    headline = "Delete Guest"
    template_name = 'cpanel/form.html'

    def get_context_data(self, **kwargs):
        context = super(GuestDeleteView, self).get_context_data(**kwargs)
        self.object = Guest.objects.get(pk=kwargs['pk'])
        context['addit_info'] = "<div><h1 class='lead'>Are you sure that you want to delete \
        <strong>{}</strong>?</h1></div>".format(self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = Guest.objects.get(pk=kwargs['pk'])
        trigger_send_message(self.object.id, "check_out")
        self.object.delete()
        return HttpResponseRedirect(reverse('concierge:guest_list'))


class ReplyView(LoginRequiredMixin, IsManagerOrAdmin, SetHeadlineMixin, StaticContextMixin,
    HotelUserMixin, TemplateView):
    """
    :Angular View: Handle all Reply create/edit/delete UI.
    """
    headline = "Auto Replies"
    template_name = "concierge/replies.html"
    static_context = {'headline_small': '& Automatic Messaging'}
