from __future__ import print_function    # (at top of module)
import re
import xml.etree.ElementTree as ET
from tripsparser.tripsparser import parse
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

    def parse(self):
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
                    sum(wl[1] for wl in weight_list[:2]) / len(weight_list) if len(weight_list) > 0 else 0,
                    ','.join([wl[0]+": "+str(wl[1]) for wl in weight_list])
                )
            )
        for a,b,c in avg_weight:
            print(a, " -> ", c)
        return max(avg_weight, key=lambda x: x[1])[0]

    def process_skeletons(self, model, ontology):
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


            print()
            print("Sentence is ", self.sentence)
            print(headword, " is the head word")

            new_head = self.get_best_interpretation(headword, surrounding_words, model, ontology)

            print(new_head," is the new selected head word")
            print(surrounding_words, " are surrounding words")
            new_sk = "({} {})".format(new_head, " ".join(skeleton[1:-1].split()[1:]))
            print("Original skeleton : ", skeleton)
            print("New skeleton : ", new_sk)
            print()
            new_skeletons.append(new_sk)

        self.parsed = new_skeletons


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

    arg_parser.add_argument(
        '-o', '--output', help='Output File', required=True)

    arg_parser.add_argument(
        '-w', '--word2vec', help='Prebuilt Word2Vec for word sense disambiguation', required=False)

    arg_parser.add_argument(
        '-t', '--tripsdir', help='TRIPS Ontology Directory', required=False)


    # input can be either individual sentences list or lore knowledge base
    arg_parser.add_argument('-f', '--input-format', help='Input File Format',
                            choices=['sentences', 'lore'], default='sentences')

    args = arg_parser.parse_args()

    word2vec_model = None
    TRIPS_ONTOLOGY = None
    if(args.word2vec):
        if args.tripsdir is None:
            # If word2vec model is provided, trips directory must be provided
            print("ERROR : TRIPS directory must be provided")
            exit()

        print("Loading trips ontology")
        TRIPS_ONTOLOGY = ontology.load_ontology(args.tripsdir)
        print("TRIPS ontology Loaded")

        print("Loading word2vec data")
        word2vec_model = gensim.models.Word2Vec.load_word2vec_format(
            args.word2vec, binary=True)
        print("Word2vec data loaded")

    sentence_input = (args.input_format == "sentences")

    parser = LoreParser()
    output = open(args.output, "w")
    count = 0
    for index, line in enumerate(open(args.input)):
        if sentence_input:
            predicate = LorePredicate("", "", line.strip())
        else:
            predicate = parser.parse_sentence(line.strip())

        output.write(predicate.sentence + "\n")
        predicate.parse()

        if not predicate.parsed:
            print("Malformed sentence ", line," skipped")
            # Malformed sentence might fail to be parsed
            continue


        if(word2vec_model):
            predicate.process_skeletons(word2vec_model, TRIPS_ONTOLOGY)

        skeletons = predicate.get_skeletons()
        if skeletons:
            for s in skeletons:
                output.write("\t{}\n".format(s))
