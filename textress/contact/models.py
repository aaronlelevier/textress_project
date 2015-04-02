from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _


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
