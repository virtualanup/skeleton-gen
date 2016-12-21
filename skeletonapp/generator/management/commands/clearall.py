from django.core.management.base import BaseCommand, CommandError
from ...models import SourceSentence, ProcessedSkeleton, Skeleton
import gensim


class Command(BaseCommand):
    help = 'Clear everything'

    def handle(self, *args, **options):
        ProcessedSkeleton.objects.all().delete()
        SourceSentence.objects.all().delete()
        Skeleton.objects.all().delete()
        print("Database cleared")
