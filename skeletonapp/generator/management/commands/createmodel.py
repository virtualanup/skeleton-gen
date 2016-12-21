from django.core.management.base import BaseCommand, CommandError
import gensim


class Command(BaseCommand):
    help = 'Creates Word2Vec Model'

    def add_arguments(self, arg_parser):

        arg_parser.add_argument(
            '-i', '--input', help='Input File', required=True)

        arg_parser.add_argument(
            '-o', '--output', help='Output file', required=True)

    def handle(self, *args, **options):
        print "Word2Vec Model Creator"

        # Create the word2vec model using gensim
        sentences = [s.split() for s in open(options['input'])]
        model = gensim.models.Word2Vec(sentences, size=50, window=5, min_count=1, workers=4)
        model.save(options['output'])
