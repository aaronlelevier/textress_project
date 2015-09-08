class AcctCostContextMixin(object):

    def get_context_data(self, **kwargs):
        context = super(AcctCostContextMixin, self).get_context_data(**kwargs)
        context['acct_cost'] = getattr(self.hotel, 'acct_cost', None)
        return context


def alert_messages(messages, alerts=None):
    """Return a `list` of Alert messages in HTML when Users need to do 
    something before their Account is fully functional.

    :messages: a ``list`` of ``dict's`` of messages to display.

    - keys: type, info, icon, strong_message, message
    """

    alerts = alerts or []

    html_message = """
        <div class="alert alert-warning">
            <a href="{link}" class="no_decoration">
                <i class="{icon}"></i>
                <strong>{strong_message}</strong> {message}
            </a>
            <button data-dismiss="alert" class="close">
                &times;
            </button>
        </div>
        """
    icon_dict = {
        'success': 'fa fa-check-circle'
        'info': 'fa fa-info-circle'
        'warning': 'fa fa-exclamation-triangle'
        'danger': 'fa fa-times-circle'
    }

    # set the icon based on the alert type
    [m['link'] = icon_dict['type'] for m in messages]
    
    for message in messages:
        alerts.append(html_message.format(**message))

    return alerts
