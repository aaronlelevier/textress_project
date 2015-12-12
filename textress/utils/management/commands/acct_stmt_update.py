from django.core.management.base import BaseCommand

from account.tasks import get_or_create_acct_stmt_all_hotels
from utils.models import Dates


class Command(BaseCommand):
    """
    Daily job to update all Hotels' AcctStmt MTD.
    """
    help = "Update all Hotels' monthly Account Statements"

    def handle(self, *args, **options):
        dates = Dates()
        month = dates._month
        year = dates._year

        get_or_create_acct_stmt_all_hotels.delay(month, year)
