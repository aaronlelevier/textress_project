from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from utils.create import _get_groups_and_perms


class Command(BaseCommand):
    help = "Create initial Groups and Superuser for live site."

    def handle(self, *args, **options):
        # Hotel Groups
        _get_groups_and_perms()
        
        # Superuser
        user = User.objects.create_user(
            settings.SUPERUSER_USERNAME,
            settings.SUPERUSER_EMAIL,
            settings.SUPERUSER_PASSWORD
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
