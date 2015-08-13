from django.conf import settings
from django.utils import html
from django.template.loader import render_to_string

from django.core.mail import EmailMultiAlternatives


class Email(object):
    '''Base class for sending Email with HTML / Text.

    `to` and `bcc` must be a `list`

    If `text_content` is None, use `html.strip_tags` to populate it.
    '''
    def __init__(self, subject, to, html_content, text_content=None,
        obj=None, extra_context=None, from_email=settings.DEFAULT_FROM_EMAIL,
        bcc=[settings.DEFAULT_EMAIL_NOREPLY], *args, **kwargs):

        # Context
        c = {'obj': obj,
            'site_name': settings.SITE_NAME,
            'textress_phone': settings.TEXTRESS_PHONE_NUMBER,
            'textess_contact_email': from_email
        }
        
        c = self._update_context(c, extra_context)

        self.subject = render_to_string(subject, c)
        self.from_email = from_email
        self.to = [to]
        self.bcc = bcc or []

        self.html_content = render_to_string(html_content, c)

        self.text_content = self._get_text_content(text_content, html_content, c)

    def _get_text_content(self, text_content, html_content, c):
        if text_content:
             return render_to_string(self.text_content, c)
        else:
            return html.strip_tags(render_to_string(html_content, c))

    def _update_context(self, c, extra_context):
        if isinstance(extra_context, dict):
            c.update(extra_context)
        elif extra_context:
            raise TypeError("extra_context must be a dict, but it is a {}".format(type(extra_context)))
        return c

    @property
    def msg(self):
        msg = EmailMultiAlternatives(self.subject, self.text_content, self.from_email,
            self.to, self.bcc)
        msg.attach_alternative(self.html_content, "text/html")
        return msg