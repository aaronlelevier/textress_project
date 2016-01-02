from django.core.management.base import BaseCommand

from account.tasks import acct_stmt_update_prev_all_hotels


class Command(BaseCommand):
    """
    This checks that all 'Hotels' have a "final end of month" AcctStmt.

    :note:
        if prices in ``Pricing`` model are not loaded, 
        this command will cause an infinite loop.
    """
    help = "Update all Hotels' 'End of Month' Account Statements"

    def handle(self, *args, **options):
        acct_stmt_update_prev_all_hotels.delay()
