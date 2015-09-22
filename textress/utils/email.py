from __future__ import absolute_import

from django.conf import settings
from django.utils import html
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from celery import shared_task


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

        if extra_context:
            c.update(extra_context)

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

    @property
    def msg(self):
        msg = EmailMultiAlternatives(self.subject, self.text_content, self.from_email,
            self.to, self.bcc)
        msg.attach_alternative(self.html_content, "text/html")
        return msg


### EMAILS

@shared_task
def send_account_charged_email(hotel, charge):
    hotel_admin = hotel.admin
    email = Email(
        to=hotel_admin.email,
        from_email=settings.DEFAULT_EMAIL_BILLING,
        subject='email/account_charged/subject.txt',
        html_content='email/account_charged/email.html',
        extra_context={
            'user': hotel_admin,
            'charge': charge,
            'hotel': hotel,
            'SITE': settings.SITE
            }
        )
    email.msg.send()


@shared_task
def send_auto_recharge_failed_email(hotel):
    hotel_admin = hotel.admin
    email = Email(
        to=hotel_admin.email,
        from_email=settings.DEFAULT_EMAIL_SUPPORT,
        subject='email/auto_recharge_failed/subject.txt',
        html_content='email/auto_recharge_failed/email.html',
        extra_context={
            'user':hotel_admin,
            'hotel': hotel,
            'SITE': settings.SITE
            }
        )
    email.msg.send()


@shared_task
def send_charge_failed_email(hotel, amount):
    hotel_admin = hotel.admin
    email = Email(
        to=hotel_admin.email,
        from_email=settings.DEFAULT_EMAIL_BILLING,
        subject='email/charge_failed/subject.txt',
        html_content='email/charge_failed/email.html',
        extra_context={
            'user':hotel_admin,
            'hotel': hotel,
            'SITE': settings.SITE
            }
        )
    email.msg.send()


@shared_task
def send_delete_unknown_number_failed_email(ph_num):
    """Email myself that a Twilio PH that wasn't registered to a 
    Hotel received an SMS, but I wasn't able to delete it, so I 
    need to delete it manually."""
    hotel_admin = hotel.admin
    email = Email(
        to=hotel_admin.email,
        from_email=settings.DEFAULT_EMAIL_BILLING,
        subject='email/delete_unknown_number_failed/subject.txt',
        html_content='email/delete_unknown_number_failed/email.html',
        extra_context={
            'ph_num': ph_num
            }
        )
    email.msg.send()
