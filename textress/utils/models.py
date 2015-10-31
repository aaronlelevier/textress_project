import datetime

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _

import pytz


class Dates(object):

    tzinfo = pytz.timezone(settings.TIME_ZONE)

    @property
    def _now(self):
        return timezone.now()

    @property
    def _today(self):
        return self._now.date()

    @property
    def _year(self):
        return self._now.year

    @property
    def _month(self):
        return self._now.month

    def first_of_month(self, month=None, year=None):    
        """
        Return a timezone aware ``first_of_month`` datetime object. If no 
        ``month`` or ``year`` are given, return for the current month.
        """
        if not all([month, year]):
            month = self._today.month
            year = self._today.year

        return datetime.datetime(day=1, year=year, month=month,
            tzinfo=self.tzinfo).date()

    def last_month_end(self, date=None):
        "Return the last month's ending date as a `date`."
        date = date or self._today
        return self.first_of_month(month=date.month,
            year=date.year) - datetime.timedelta(days=1)


class TimeStampBaseModel(Dates, models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseQuerySet(models.query.QuerySet):

    def current(self):
        return self.filter(hidden=False)

    def archived(self):
        return self.filter(hidden=True)


class BaseManager(models.Manager):

    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db)

    def current(self):
        return self.get_queryset().current()

    def archived(self):
        return self.get_queryset().archived()


class BaseModel(models.Model):
    """Base model to keep track of Model edits and hide Model objects
    if necessary."""
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    hidden = models.BooleanField(_("Hidden"), blank=True, default=False)

    objects = BaseManager()

    class Meta:
        abstract = True

    def __str__(self):
        return "id: {self.id}; class: {self.__class__.__name__}; deleted: \
{self.deleted}".format(self=self)

    def delete(self, override=None, *args, **kwargs):
        "Only delete explicitly."
        if not override:
            return self.hide()
        else:
            return super(BaseModel, self).delete(*args, **kwargs)

    def hide(self):
        self.hidden = True 
        self.save()
        return self


class Tester(BaseModel):
    """
    Concrete model used to test ``BaseModel``
    """
    pass
