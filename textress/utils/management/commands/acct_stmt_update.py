from django.core.management.base import BaseCommand

from account.models import AcctStmt
from main.models import Hotel


class Command(BaseCommand):
    help = "Update all Hotels' monthly Account Statements"

    def handle(self, *args, **options):
        for hotel in Hotel.objects.all():
            # TODO: need a filter here for "active" hotels only?
            acct_stmt, created = AcctStmt.objects.get_or_create(hotel=hotel)

            self.stdout.write("Hotel: {}; Account Statement: {} "
                "successfully updated.".format(hotel, acct_stmt))