from os import listdir
from os import walk
from os.path import isfile, join

from django.core.management.base import BaseCommand, CommandError
from skeleton import LoreParser

from ...models import SourceSentence


class Command(BaseCommand):
    help = 'Load lore sentences'

    def add_arguments(self, arg_parser):

        arg_parser.add_argument(
            '-i', '--input', help='Input File', required=True)

        arg_parser.add_argument('-f', '--input-format', help='Input File Format',
                                choices=['sentences', 'lore'], default='sentences')

    def handle(self, *args, **options):
        filename = options['input']

        sentence_input = (options['input_format'] == "sentences")

        count = 0
        for line in open(filename):
            line = line.strip()
            sentence = line
            if not sentence_input:
                # Convert the lore syntax to sentence
                parser = LoreParser()
                predicate = parser.parse_sentence(line)
                sentence = predicate.sentence

            # Process the sentence
            if sentence[0] == '"' and sentence[-1] == '"':
                # Remove the quotes
                sentence = sentence[1:-1]

            sentence = sentence.replace("Many-or-some", "Many")

            s, created = SourceSentence.objects.get_or_create(sentence=sentence)
            if created:
                count += 1
                s.parse()
        print count," new sentences added"
