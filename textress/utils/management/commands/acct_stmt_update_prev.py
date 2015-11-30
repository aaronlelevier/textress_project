import datetime
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings

from account.models import Dates, AcctStmt
from main.models import Hotel


class Command(BaseCommand):
    """
    This is an extra check that all 'Hotels' have a 
    "final end of month" AcctStmt.

    :note:
        if prices in ``Pricing`` model are not loaded, 
        this command will cause an infinite loop.
    """
    help = "Update all Hotels' monthly Account Statements"

    def handle(self, *args, **options):
        dates = Dates()
        this_month = dates.first_of_month()
        last_month = dates.last_month_end(first_of_month)

        for hotel in Hotel.objects.all():
            update_prev_month = False

            if hotel.created < first_of_month:
                try:
                    acct_stmt = AcctStmt.objects.get(
                        hotel=hotel,
                        month=last_month.month,
                        year=last_month.year
                    )
                except AcctStmt.DoesNotExist:
                    update_prev_month = True
                else:
                    if acct_stmt.modified < first_of_month:
                        update_prev_month = True

                if update_prev_month:
                    acct_stmt, created = AcctStmt.objects.get_or_create(
                        hotel=hotel,
                        month=last_month.month,
                        year=last_month.year
                    )

                    self.stdout.write("Hotel: {}; Account Statement: {} "
                        "successfully updated.".format(hotel, acct_stmt))