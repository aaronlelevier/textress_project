from django.core.management.base import BaseCommand

from account.tasks import charge_hotel_monthly_for_phone_numbers_all_hotels


class Command(BaseCommand):
    help = "Run phone number fees for all Hotels."

    def handle(self, *args, **options):
        charge_hotel_monthly_for_phone_numbers_all_hotels.delay()
