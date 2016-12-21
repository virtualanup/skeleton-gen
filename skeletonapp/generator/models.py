from __future__ import unicode_literals

from django.db import models
from skeleton import parse
import json

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
        tparse, word_map = parse(self.sentence)
        if parse:
            self.trips_parse = json.dumps(tparse)
            self.word_map = json.dumps(word_map)

        self.parsed = True
        self.save()

