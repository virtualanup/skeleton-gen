"""
test_goldset.py
Test gold dataset for accuracy and precision
"""

from __future__ import print_function    # (at top of module)

from skeleton import parse, LorePredicate, LoreParser
import gensim
from diesel import ontology

# Change the following configurations
gold_dataset = "data/input/predmap.txt"
trips_path = "../flaming-tyrion/lexicon/data/"
word2vec_path = "data/input/googlenews.bin"

skels_list = []
for line in map(lambda x: x.strip(), filter(lambda x: len(x) > 0, open(gold_dataset))):
    if(line.startswith("(")):
        if(len(skels_list) > 0):
            skels_list[-1][1].append(line)
    else:
        skels_list.append([line, []])

print("Gold predicates loaded")

word2vec_model = None
TRIPS_ONTOLOGY = None

TRIPS_ONTOLOGY = ontology.load_ontology(trips_path)
print("TRIPS ontology loaded")

word2vec_model = gensim.models.Word2Vec.load_word2vec_format(
word2vec_path, binary=True)
print("Word2Vec data loaded")


# Process the skeletons
count = 0
ttc = 0
tsc = 0
total = 0
for sentence, orig_skeletons in skels_list:
    # Process the skeleton using our skeleton generator. Compare the generated skeletons
    # with the gold predicate
    predicate = LorePredicate("", "", sentence)
    try:
        predicate.parse(False)
    except KeyboardInterrupt:
        exit(0)

    except:
        print("Failed to parse sentence ", sentence)
        continue

    if not predicate.parsed:
        print("Sentence ", sentence, " not parsed")
        continue
    else:
        # print(predicate.parsed)
        pass

    # Before processing, get the parse by TRIPS parser
    trips_skeleton = set(predicate.parsed)

    # process the skeletons

    predicate.process_skeletons(word2vec_model, TRIPS_ONTOLOGY)

    generated_skeletons = set(predicate.parsed)

    orig_skeletons = set(orig_skeletons)

    # Compare the original and generated skeletons
    trips_correct = len(orig_skeletons & trips_skeleton)
    skeleton_correct = len(orig_skeletons & generated_skeletons)

    ttc += trips_correct
    tsc += skeleton_correct
    total += len(orig_skeletons)

    # if len(generated_skeletons & orig_skeletons) > 0:
    #     print(generated_skeletons & orig_skeletons)
    # else:
    #     print("No match found")
    #     print(orig_skeletons)
    #     print()
    #     print(generated_skeletons)

    # print()
    # print()

    print(trips_correct," and ", skeleton_correct)

    count += 1
    if(count > 10):
        break

print("Summary : ")
print("Total skeletons : ", total)
print("Skeletons corretly predicted by trips ", ttc)
print("Skeletons corretly predicted by skeleton ", tsc)
