from os import listdir
from os import walk
from os.path import isfile, join

from django.core.management.base import BaseCommand, CommandError
from skeleton import LoreParser

from ...models import SourceSentence


class Command(BaseCommand):
    help = 'Parse the sentences using web based trips parser'

    def handle(self, *args, **options):
        for sentence in SourceSentence.objects.all():
            sentence.parse()
        print("Sentences parsed")
