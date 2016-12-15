from __future__ import print_function

import re


class LoreParser:
    pattern = re.compile("\(:s([^(]*)(.*)\"(.*)\"")

    def __init__(self):
        pass

    def parse_sentence(self, sentence):
        """
        returns source information, sentence and predicate
        """
        parts = self.pattern.search(sentence)
        return LorePredicate(*parts.groups())
