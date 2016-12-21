from __future__ import print_function    # (at top of module)
import re
import xml.etree.ElementTree as ET
from skeleton import parse, LorePredicate, LoreParser
import argparse
import gensim
from diesel import ontology

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
    else:
        print("Word2Vec model not loaded")

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

        print()
        print()
        print(line)
        print('Before word sense disambiguation')
        predicate.print_skeletons()
        print()

        if(word2vec_model):
            predicate.process_skeletons(word2vec_model, TRIPS_ONTOLOGY)
            print('After word sense disambiguation')
            predicate.print_skeletons()
            print()



        skeletons = predicate.get_skeletons()
        if skeletons:
            for s in skeletons:
                output.write("\t{}\n".format(s))
