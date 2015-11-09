from django.core.management.base import BaseCommand

from concierge.tasks import archive_guests


class Command(BaseCommand):
    help = "Archive all Guests that are past their check-out date."

    def handle(self, *args, **options):
        archive_guests.delay()
