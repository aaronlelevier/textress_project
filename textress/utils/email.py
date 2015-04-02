from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django.core.mail import (send_mail, EmailMessage, EmailMultiAlternatives,
    get_connection)


class Email(object):
    '''Base class for sending Email with HTML / Text.

    `to` and `bcc` must be a `list` or `tuple`
    '''
    def __init__(self, subject, from_email, to, text_content, html_content,
        bcc=None, *args, **kwargs):
        self.subject = subject
        self.from_email = from_email
        self.to = to
        self.text_content = text_content
        self.html_content = html_content
        self.bcc = bcc or []

    @property
    def connection(self):
        return get_connection(username=self.from_email,
            password=settings.EMAIL_HOST_PASSWORD)

    @property
    def msg(self):
        msg = EmailMultiAlternatives(self.subject, self.text_content, self.from_email,
            self.to, self.bcc, connection=self.connection)
        msg.attach_alternative(self.html_content, "text/html")
        return msg


### NEWSLETTER ###

def send(obj, from_email=settings.DEFAULT_EMAIL_SAYHELLO, to_email=None,
    subject_template_name='email/coming_soon_subject.txt',
    email_template_name='email/coming_soon_email.html',
    html_email_template_name='email/coming_soon_email.html',
    *args, **kwargs):

    # the object instance should have an email attr or explicity
    # state who this email is going to
    if not getattr(obj, 'email') and not to_email:
        raise NotImplementedError("Either the {} or to_email must contain an email.".format(obj))
    if not to_email:
        to_email = obj.email

    # Context
    c = {'obj': obj,
        'site_name': settings.SITE_NAME,
        'textress_phone': settings.TEXTRESS_PHONE_NUMBER,
        'textess_contact_email': from_email
    }
    c.update(kwargs)

    subject = render_to_string(subject_template_name, c)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    email = render_to_string(email_template_name, c)

    if html_email_template_name:
        html_email = render_to_string(html_email_template_name, c)
    else:
        html_email = None
    
    return send_mail(subject, email, from_email, [to_email], html_message=html_email)



def send_contact_email(nl):
    email = Email(
        subject = '{}, Thank you contacting Textress'.format(contact.name),
        from_email = settings.DEFAULT_EMAIL_SAYHELLO,
        to = [contact.email],
        text_content = """
            Name: {contact.name},
            Thank you for your contacting Textess. Please allow 1 business day for
            general business inquiries, and we will be in touch. If you need immediate 
            assistance, please contact us at the phone number below. Thank you.
            """.format(contact=contact),
        html_content = render_to_string('email/contact.html', {'contact': contact}),
        bcc = [settings.DEFAULT_EMAIL_ADMIN]
        )

    return email.msg.send()


### CONT: ###



def send_suspend_email(hotel):
    context = {
        'hotel': hotel.name,
        'url': "http://{url}cards/".format(url=settings.SITE_URL)
        }

    email = Email(
        subject = 'Textress account has been temporarily suspended',
        from_email = settings.DEFAULT_EMAIL_BILLING,
        to = [User.objects.get(id=hotel.admin_id).email],
        text_content = """
            Dear {hotel}, your account has been temporarily suspended 
            because payment failed. Please navigate to {url} and update 
            your payment preferences in order to reactivate your account. 
            Thank you, Textress Billing.
            """.format(**context),
        html_content = render_to_string('email/account_suspended.html', context),
        bcc = [settings.DEFAULT_EMAIL_ADMIN]
        )

    return email.msg.send()


def send_close_account_email(user):
    context = {
        'user': user
        }

    email = Email(
        subject = 'Request to close Textress account',
        from_email = settings.DEFAULT_EMAIL_BILLING,
        to = [user.email],
        text_content = """
            Dear {user},
            Your request to close your account has been submitted.
            Takes 24 hours to process request.
            Payment refund take 5-7 business days.
            Any questions, please contact: billing@textress.com
            PH # for questions, 775-419-4000
            """.format(**context),
        html_content = render_to_string('email/close_account_request.html', context),
        bcc = [settings.DEFAULT_EMAIL_ADMIN]
        )

    return email.msg.send()


def send_forgot_password_email(user, temp_password):
    context = {
        'user': user,
        'temp_password': temp_password,
        'url': "http://{}account/reset-password/".format(settings.SITE_URL)
        }

    email = Email(
        subject = 'Textress Account Support',
        from_email = settings.DEFAULT_EMAIL_SUPPORT,
        to = [user.email],
        text_content = """
            {user.username},
            Here is your temporary password: {temp_password}.
            Please follow this link to reset your password:
            {url}. Thank you.""".format(**context),
        html_content = render_to_string('email/password_reset.html', context)
        )

    return email.msg.send()


def send_contact_email(contact):
    email = Email(
        subject = '{}, Thank you contacting Textress'.format(contact.name),
        from_email = settings.DEFAULT_EMAIL_SAYHELLO,
        to = [contact.email],
        text_content = """
            Name: {contact.name},
            Thank you for your contacting Textess. Please allow 1 business day for
            general business inquiries, and we will be in touch. If you need immediate 
            assistance, please contact us at the phone number below. Thank you.
            """.format(contact=contact),
        html_content = render_to_string('email/contact.html', {'contact': contact}),
        bcc = [settings.DEFAULT_EMAIL_ADMIN]
        )

    return email.msg.send()


def send_purchase_conf_email(user, purchase, stripe_email):
    context = {
        'user': user,
        'stripe_email': stripe_email,
        'purchase': purchase,
        'SITE_URL': 'http://{}contact/'.format(settings.SITE_URL)
        }

    email = Email(
        subject = 'Textress Payment Receipt',
        from_email = settings.DEFAULT_EMAIL_SUPPORT,
        to = [stripe_email],
        text_content = """
            Name: {user.name}
            Email {stripe_email}
            Purchase Confirmation #: {purchase.code}
            Date: {purchase.purchase_date}.
            """.format(**context),
        html_content = render_to_string('email/purchase_conf.html', context),
        bcc = [settings.DEFAULT_EMAIL_ADMIN]
        )

    return email.msg.send()


