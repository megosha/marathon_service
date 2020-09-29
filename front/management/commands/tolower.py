from django.core.management.base import BaseCommand
from front import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = models.User.objects.all().exclude(is_superuser=True)
        for user in users:
            lower_data = (user.email).strip().lower()
            user.email = lower_data
            user.username = lower_data
            user.save()