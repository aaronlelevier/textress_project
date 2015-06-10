class DeleteButtonMixin(object):
    "Color and Text for a Delete Button to display to User."

    def get_context_data(self, **kwargs):
        context = super(DeleteButtonMixin, self).get_context_data(**kwargs)
        context['btn_color'] = 'danger'
        context['btn_text'] = 'Delete'
        return context  