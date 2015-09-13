import datetime
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings

from account.models import AcctStmt
from main.models import Hotel


def now():
    return timezone.now()


def this_month_start_dt():
    """Return the first day of the current month."""
    today = now()
    tzinfo = pytz.timezone(settings.TIME_ZONE)
    return datetime.datetime(day=1, month=today.month, year=today.year,
        tzinfo=tzinfo)


def last_month_end_dt():
    """Return the last day of the previouse month."""
    return this_month_start_dt() - datetime.timedelta(days=1)


class Command(BaseCommand):
    """

    :note:
        if prices in ``Pricing`` model are not loaded, 
        this command will cause an infinite loop.
    """
    help = "Update all Hotels' monthly Account Statements"

    def handle(self, *args, **options):
        this_month = this_month_start_dt()
        last_month = last_month_end_dt()

        for hotel in Hotel.objects.all():
            update_prev_month = False

            if hotel.created < this_month:
                try:
                    acct_stmt = AcctStmt.objects.get(
                        hotel=hotel,
                        month=last_month.month,
                        year=last_month.year
                    )
                except AcctStmt.DoesNotExist:
                    update_prev_month = True
                else:
                    if acct_stmt.modified < this_month:
                        update_prev_month = True

                if update_prev_month:
                    acct_stmt, created = AcctStmt.objects.get_or_create(
                        hotel=hotel,
                        month=last_month.month,
                        year=last_month.year
                    )

                    self.stdout.write("Hotel: {}; Account Statement: {} "
                        "successfully updated.".format(hotel, acct_stmt))