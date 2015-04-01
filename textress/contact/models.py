from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

class Newsletter(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(_("Email"), max_length=100)

    def __str__(self):
        return self.email
