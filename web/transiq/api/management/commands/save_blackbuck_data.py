from django.core.management.base import BaseCommand

from api.blackbuck import fetch_blackbuck_data


class Command(BaseCommand):
    args = 'Arguments not needed'
    help = 'Django admin command to save blackbuck data'

    def handle(self, *args, **options):
        fetch_blackbuck_data(clean=True)
