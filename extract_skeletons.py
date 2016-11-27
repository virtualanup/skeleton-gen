import re
import xml.etree.ElementTree as ET
from tripsparser.tripsparser import parse
import argparse


class LorePredicate:
    patterns = {
        "many-or-some": re.compile("Many-or-some ([^ ]*) ([^ ]*) ([^ ]*) as ([^ ]*)\."),
        "a-action-y": re.compile("A ([^ ]*) may ([^ ]*) ([^ ]*)\."),
    }

    def __init__(self, source, predicate, sentence):
        self.source = source
        self.predicate = predicate
        self.sentence = sentence

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

    def get_skeletons(self):
        """
        Gets the skeleton for the current predicate
        """
        pat = self.match()
        if pat is not None:
            # parse the sentence and return the extracted predicates
            groups = self.patterns[pat].search(self.sentence).groups()
            if pat == "many-or-some":
                sentence1 = self.sentence.replace("Many-or-some", "Many")
                sentence2 = self.sentence.replace("Many-or-some", "Some")
                # taking both sentences into consideration won't generate more
                # skeletons
                return parse(sentence1)
            else:
                return parse(self.sentence)


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


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description='Parse sentences to create predicates')
    arg_parser.add_argument('-i', '--input', help='Input File', required=True)
    arg_parser.add_argument('-o', '--output', help='Output File', required=True)

    # input can be either individual sentences list or lore knowledge base
    arg_parser.add_argument('-f', '--input-format', help='Input File Format',
                        choices=['sentences', 'lore'], default='sentences')

    args = arg_parser.parse_args()

    sentence_input = (args.input_format == "sentences")

    parser = LoreParser()
    output = open(args.output, "w")
    count = 0
    for index, line in enumerate(open(args.input)):
        if sentence_input:
            predicate = LorePredicate("","",line.strip())
        else:
            predicate = parser.parse_sentence(line.strip())

        output.write(predicate.sentence + "\n")
        skeletons = predicate.get_skeletons()
        if skeletons:
            print(predicate.sentence)
            for s in skeletons:
                output.write("\t{}\n".format(s))
