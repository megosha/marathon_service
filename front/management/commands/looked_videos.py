from django.core.management.base import BaseCommand
from front import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        payments = models.Payment.objects.filter(status='succeeded').distinct('account')
        videos = models.Video.objects.all()
        for payment in payments:
            payment.account.looked_videos.add(*videos)