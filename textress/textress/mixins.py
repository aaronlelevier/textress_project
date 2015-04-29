from django.views.generic import View

from braces.views import GroupRequiredMixin


class AdminGroupView(GroupRequiredMixin, View):
    group_required = 'hotel_admin'
    

class ManagerGroupView(GroupRequiredMixin, View):
    group_required = ['hotel_admin', 'hotel_manager']