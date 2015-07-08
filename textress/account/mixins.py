### ACCT COST MIXINS ###

class AcctCostContextMixin(object):

    def get_context_data(self, **kwargs):
        context = super(AcctCostContextMixin, self).get_context_data(**kwargs)
        context['acct_cost'] = getattr(self.hotel, 'acct_cost', None)
        return context