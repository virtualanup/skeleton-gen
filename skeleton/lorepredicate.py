from __future__ import print_function
import re
import xml.etree.ElementTree as ET
from .tripsparser import parse
import argparse
import gensim
from diesel import ontology


class LorePredicate:
    patterns = {
        "many-or-some": re.compile("Many-or-some ([^ ]*) ([^ ]*) ([^ ]*) as ([^ ]*)\."),
        "a-action-y": re.compile("A ([^ ]*) may ([^ ]*) ([^ ]*)\."),
    }

    def __init__(self, source, predicate, sentence):
        self.source = source
        self.predicate = predicate
        self.sentence = sentence
        self.parsed = None
        self.role_dict = dict()

    def str(self):
        return self.sentence

    def match(self):
        """
        matches the current sentence with one of the pattern
        """
        for name, pat in self.patterns.items():
            if pat.match(self.sentence):
                return name
        return None

    def parse(self, match=True):
        """
        Gets the skeleton for the current predicate
        if match is true, only takes sentence that match predetermined patterns
        """
        if not match:
            self.parsed, self.role_dict = parse(self.sentence)
            return

        pat = self.match()
        if pat is not None:
            # parse the sentence and return the extracted predicates
            groups = self.patterns[pat].search(self.sentence).groups()
            if pat == "many-or-some":
                sentence1 = self.sentence.replace("Many-or-some", "Many")
                sentence2 = self.sentence.replace("Many-or-some", "Some")
                # taking both sentences into consideration won't generate more
                # skeletons
                self.parsed, self.role_dict = parse(sentence1)
            else:
                self.parsed, self.role_dict = parse(self.sentence)

    def get_skeletons(self):
        return self.parsed

    def get_best_interpretation(self, headword, surrounding_words, model, ontology):
        """
        Get the best sense for the word in the context
        """
        # First of all, get all possible interpretations
        possible_interp = ontology.get_word(headword)
        weightage = []
        avg_weight = []
        for interp in possible_interp:
            weight_list = []
            for word in interp.words:
                if word != headword:
                    weight = 0
                    for role in surrounding_words:
                        if role in model and word in model:
                            similarity = model.similarity(role, word)
                            #print(role, word, similarity)
                            weight += similarity
                    weight_list.append((word, weight))
            weight_list = sorted(weight_list, key=lambda x: x[1])[-4:]
            avg_weight.append(
                (
                    interp.name,
                    sum(wl[1] for wl in weight_list[:2]) /
                    len(weight_list) if len(weight_list) > 0 else 0,
                    ','.join([wl[0] + ": " + str(wl[1]) for wl in weight_list])
                )
            )
        # for a, b, c in avg_weight:
        #     print(a, " -> ", c)
        if len(avg_weight) > 0:
            return max(avg_weight, key=lambda x: x[1])[0]
        return None

    def process_skeletons(self, model, ontology, verbose=False):
        new_skeletons = []
        # print(self.role_dict)
        if not self.parsed:
            print("No parse available")
            return
        for skeleton in self.parsed:
            # Get the ontology for the roles
            words = [word for word in skeleton[
                1:-1].split() if not word.startswith(":")]
            headrole = words[0]
            if headrole not in self.role_dict:
                # Main role is not in dictionary. Add the skeleton as it is
                # for eg. sa_tell won't be associated with any word in sentence
                # print(headrole," not found")
                new_skeletons.append(skeleton)
                continue
            headword = self.role_dict[headrole]
            # Find surrounding words
            surrounding_words = [self.role_dict[role]
                                 for role in words if role in self.role_dict]
            # Remove head word
            surrounding_words.remove(headword)

            new_head = self.get_best_interpretation(
                headword, surrounding_words, model, ontology)

            if not new_head:
                new_head = headword

            new_sk = "({} {})".format(
                new_head, " ".join(skeleton[1:-1].split()[1:]))

            if verbose:
                print()
                print("Sentence is ", self.sentence)
                print(headword, " is the head word")
                print(new_head, " is the new selected head word")
                print(surrounding_words, " are surrounding words")
                print("Original skeleton : ", skeleton)
                print("New skeleton : ", new_sk)
                print()

            new_skeletons.append(new_sk)

        self.parsed = new_skeletons
