from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.text import slugify
from django.core.urlresolvers import reverse

from utils.create import random_lorem


### BASE ###

class TimestampBase(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        

### CONTACT / EMAIL ###

class Contact(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(_("Name"), max_length=100)
    email = models.EmailField(_("Email"), max_length=100)
    subject = models.CharField(_("Subject"), max_length=255, blank=True)
    message = models.TextField(_("Message"), max_length=2000)

    def __str__(self):
        return "{} : {}".format(self.name, self.email)


class Newsletter(models.Model):
    '''
    All `Newsletter` signups are `unique`

    All signups b/4 alpha launch are going to get something additional. 
    I will determine this by the date of signup.
    '''

    created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(_("Email"), max_length=100, unique=True)

    def __str__(self):
        return self.email


### FAQ's ###

class Topic(TimestampBase):
    name = models.CharField(_("Name"), max_length=100)
    fa_icon = models.CharField(_("FA Icon Name"), max_length=50, blank=True)
    slug = models.SlugField(_("Slug"), max_length=100, blank=True)
    order = models.IntegerField(_("Relative Order"), blank=True, default=0,
        help_text="To be able to manually order Topics.")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class QA(TimestampBase):
    topic = models.ForeignKey(Topic, related_name='qas')
    question = models.CharField(_("Question"), max_length=255, blank=True)
    answer = models.TextField(_("Answer"), max_length=1000, blank=True)
    order = models.IntegerField(_("Relative Order"), blank=True, default=0,
        help_text="To be able to manually order QA's.")

    class Meta:
        verbose_name = 'QA'
        ordering = ('topic', 'order',)

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        if not self.question:
            self.question = random_lorem(5)
        if not self.answer:
            self.answer = random_lorem(20)
        return super().save(*args, **kwargs)

