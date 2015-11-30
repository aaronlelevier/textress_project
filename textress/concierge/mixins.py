from django.core.urlresolvers import reverse

from utils import mixins


class GuestListContextMixin(mixins.BreadcrumbBaseMixin):

    def __init__(self):
        self.clip_icon = 'clip-users'
        self.url = reverse('concierge:guest_list')
        self.url_name = 'Guest List'