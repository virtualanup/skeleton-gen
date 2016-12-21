from __future__ import unicode_literals

from django.db import models
from skeleton import parse, LoreParser, LorePredicate
import json

from django.core.urlresolvers import reverse

class SourceSentence(models.Model):
    """
    This represent individual sentence of the lore data
    """
    sentence = models.TextField()
    parsed = models.BooleanField(default=False)
    trips_parse = models.TextField(default="")
    word_map = models.TextField(default="")

    def __str__(self):
        return self.sentence

    def parse(self):
        """
        Try trips parse on the sentence
        """
        # If already parsed, simply return

        if self.parsed:
            return

        tparse, word_map = parse(self.sentence)
        self.trips_parse = json.dumps(tparse)
        self.word_map = json.dumps(word_map)

        self.parsed = True
        self.save()

    def get_trips_parse(self):
        if len(self.trips_parse) < 1:
            return None
        return json.loads(self.trips_parse)

    def get_word_map(self):
        if len(self.word_map) < 1:
            return None
        return json.loads(self.word_map)

    def get_predicate(self):
        a = LorePredicate("", "", self.sentence)
        a.parsed = self.get_trips_parse()
        a.role_dict = self.get_word_map()
        return a


class ProcessedSkeleton(models.Model):
    # Selected value of skeleton
    skeleton = models.TextField()

    sentence = models.ForeignKey(SourceSentence)
    # Save the exact skeleton extracted by trips
    trips_parse = models.TextField(default="")

    possible_entries = models.TextField(default="")
    surrounding_words = models.TextField(default="")

    TRIPS_GEN = 'a'
    MANUAL_SEL = 'b'
    SKELGEN_PROC = 'c'
    TYPE = (
        (TRIPS_GEN, 'TRIPS Generated'),
        (MANUAL_SEL, 'Manually Selected'),
        (SKELGEN_PROC, 'Processed by SkeletonGen'),
    )
    # How is the current skeleton processed?
    skeleton_type = models.CharField(
        max_length=1, choices=TYPE, default=TRIPS_GEN)

    def get_edit_url(self):
        return '<a href="{}" target="_blank">Edit</a>'.format(
            reverse(
                'skeleton_edit',
                kwargs={"skid": self.pk}
            )
        )
    get_edit_url.allow_tags = True

class Skeleton(models.Model):
    """
    This represent the final skeletons
    """
    skeleton = models.TextField()
