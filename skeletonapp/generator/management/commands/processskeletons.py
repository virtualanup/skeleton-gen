from django.core.management.base import BaseCommand, CommandError
from skeleton import LoreParser
from diesel import ontology
from django.conf import settings
import json
from django.db.models import Q
import gensim
from ...models import SourceSentence, ProcessedSkeleton


class Command(BaseCommand):
    help = 'Process the skeletons'

    def handle(self, *args, **options):
        print "Skeleton Processor"
        # Load the word2vec model
        print "Loading word2vec from ", settings.WORD2VEC_PATH
        word2vec_model = gensim.models.Word2Vec.load_word2vec_format(
            settings.WORD2VEC_PATH, binary=True)
        print "Word2Vec model loaded"

        print "Load trips ontology from ", settings.TRIPS_PATH
        TRIPS_ONTOLOGY = ontology.load_ontology(settings.TRIPS_PATH)
        print "TRIPS Ontology loaded"

        # Now, process each of the skeletons
        # First of all, remove all the automatically generated skeletons
        # from the database (but keep the manually selected ones)
        ProcessedSkeleton.objects.filter(
            ~Q(skeleton_type=ProcessedSkeleton.MANUAL_SEL)).delete()

        # Iterate through each of the
        for sentence in SourceSentence.objects.all():
            predicate = sentence.get_predicate()

            oldparses = predicate.parsed[:]

            predicate.process_skeletons(word2vec_model, TRIPS_ONTOLOGY)

            newparses = predicate.parsed

            for old, new in zip(oldparses, newparses):
                skeleton, created = ProcessedSkeleton.objects.get_or_create(sentence=sentence,
                        trips_parse=old)
                if created:
                    # Don't touch manually edited entries
                    skeleton.skeleton = new
                    print(" Information about it ")
                    print(predicate.misc_info)

                    if old in predicate.misc_info:
                        skeleton.possible_entries = json.dumps(predicate.misc_info[old]['ph'])
                    else:
                        pass
                    if new != old:
                        print sentence.sentence
                        print old ," -> ", new
                        skeleton.skeleton_type = ProcessedSkeleton.SKELGEN_PROC

                skeleton.save()
