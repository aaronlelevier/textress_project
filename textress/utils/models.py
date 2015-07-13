from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _


class TimeStampBaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created']


class AbstractBaseQuerySet(models.query.QuerySet):
    
    def current(self):
        # TODO: create logic on current for must be within the c/i  - c/o dates
        #   or make a daily job to archive c/o guests to ``hidden=True``
        return self.filter(hidden=False)

    def archived(self):
        return self.filter(hidden=True)


class AbstractBaseManager(models.Manager):

    def get_queryset(self):
        return AbstractBaseQuerySet(self.model, self._db)

    def current(self):
        return self.get_queryset().current()

    def archived(self):
        return self.get_queryset().archived()


class AbstractBase(TimeStampBaseModel):
    """Base model to keep track of Model edits and hide Model objects
    if necessary."""
    hidden = models.BooleanField(_("Hide"), blank=True, default=False)

    objects = AbstractBaseManager()

    class Meta:
        abstract = True

    def hide(self):
        self.hidden = True 
        self.save()
        return self