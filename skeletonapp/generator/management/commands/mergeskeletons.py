from __future__ import print_function

from django.core.management.base import BaseCommand, CommandError
from ...models import SourceSentence, ProcessedSkeleton, Skeleton

from django.conf import settings
import argparse
from diesel.score import parse_s_predicate, Predicate
from diesel import ontology
import diesel.weights
from collections import defaultdict
import re

class ParentPredicate(Predicate):

    @staticmethod
    def name():
        return "SiblingPredicate"

    def node_dist(self, this, other):
        """override this method to use a different node distance"""
        if this == other or this.is_parent_of(other) or other.is_parent_of(this):
            return 1
        return 0


    # Original constructor and _score filter out roles if they are not in
    # weights list. Overload them to prevent that
    def __init__(self, root, links, weights=diesel.weights.default_weights()):
        """root is the root node, links is a list of edge,node pairs"""
        self.root = root
        # make a list of everythign that has a weight. For example, [:agent ONT::PERSON] , etc
        self.links = [l for l in links]

        # just change the keys to lowercase
        self.weights = {a.lower(): b for a, b in weights.items()}


    def _score(self, my_links, other_links):
        """
        greedily matches self links and other links in order
        """
        best = {}
        descriptions = []
        for edge, node in my_links:
            scores = []
            if len(other_links) == 0:
                break
            for index, link in enumerate(other_links):
                if edge == link[0]:
                    # How far away are the nodes? node_dist returns node distance
                    res = self.node_dist(node, link[1])
                    desc = "({} {}) => ({} {}): {}".format(edge, node.name, link[0], link[1].name, res)
                    scores.append((res, index, desc, link[0]))
            if len(scores) > 0:
                # Mathched something
                best_link = max(scores, key=lambda x: x[0])
                res, index, desc, edge = best_link
                if edge not in best:
                    best[edge] = []
                best[edge].append(res)
                del other_links[index]
                descriptions.append(desc)
        return self.link_collect(best, my_links, other_links), descriptions


def get_original_skeleton(predicate):
    return "({} {})".format(predicate.root.name, " ".join(
        ["{}: {}".format(x, y.name) for x, y in predicate.links]
    ))


def reduce_skeletons(skeletons, ontology):
    """
    Iterate over the skeleton trying to reduce the number in each round
    """
    previous_skeletons = []  # skeletons in earlier round
    current_skeletons = []  # skeletons currently generated

    for skeleton in skeletons:
        current_skeletons.append((skeleton, parse_s_predicate(
            skeleton, ontology, ParentPredicate))
        )

    while(True):
        marked = defaultdict(lambda: False)
        previous_skeletons = current_skeletons
        current_skeletons = []

        for index, (skeleton, predicate) in enumerate(previous_skeletons):
            # No need to process marked skeletons. They are already taken
            # into consideration
            if marked[index]:
                continue

            sp_pair = (skeleton, predicate)
            # print("Processing :", skeleton)
            if len(predicate.links) == 0:
                # no non-core types
                # Add them as they are
                for s, p in current_skeletons:
                    if s == skeleton:
                        break
                else:
                    current_skeletons.append(sp_pair)
                continue

            # try to match every remaining skeleton with this skeleton
            generalized_predicate = predicate
            generalized_sentence = ""
            for match_index, (s_skeleton, s_predicate) in enumerate(previous_skeletons[index:]):
                actual_index = index + match_index

                # no core types
                if len(predicate.links) == 0:
                    continue
                # Get the score
                score = predicate.score(s_predicate)
                # print(score[0])
                if score[0] == 1:
                    # print(skeleton, " and ", s_skeleton, " are same")
                    # Score[1] is a list of matches
                    # in format (role1 value1) => (role2 value2)
                    root = ""
                    generalized_sentence = ""
                    general_match = []
                    # print("Score1 is ", score[1])
                    for match in score[1]:
                        #= re.search("\(([^ ]*) ([^ ]*)\) =>")
                        role1, value1, role2, value2 = re.search(
                            "\(([^ ]*) ([^ ]*)\) => \(([^ ]*) ([^ ]*)\)", match).groups()
                        if role1 == "_root":
                            root = value1
                            continue
                        # role1 and role2 must be same...check which one is parent in
                        # value1 and value2
                        val1_ont = ontology.get(value1)
                        val2_ont = ontology.get(value2)
                        if val1_ont.is_parent_of(val2_ont):
                            general_match.append((role1, value1))
                            # print(value1, " is parent of ", value2)
                        else:
                            general_match.append((role2, value2))
                            # print(value1, " is either child or equal to ", value2)

                    generalized_sentence = "({} {})".format(root, " ".join(
                        ":{} {}".format(x,y) for x,y in general_match
                        ))
                    # print("GENERAL SENTENCE ", generalized_sentence)
                    generalized_predicate = parse_s_predicate(generalized_sentence, ontology, ParentPredicate)
                    marked[actual_index] = True
                    # Extract the more generalized skeleton from the two
                    # skeletons

            current_skeletons.append((generalized_sentence, generalized_predicate))

        if len(previous_skeletons) == len(current_skeletons):
            break
    return current_skeletons

class Command(BaseCommand):
    help = 'Merge the skeletons'

    def handle(self, *args, **options):
        # Delete all rows first

        print("Load trips ontology from ", settings.TRIPS_PATH)
        TRIPS_ONTOLOGY = ontology.load_ontology(settings.TRIPS_PATH)
        print("TRIPS Ontology loaded")

        Skeleton.objects.all().delete()
        print("Deleted previous entries")

        print("Merging all skeletons...")
        skeleton_list = []
        for sk in ProcessedSkeleton.objects.all():
            skeleton_list.append(sk.skeleton)
        print(len(skeleton_list)," skeletons loaded")


        reduced = reduce_skeletons(skeleton_list, TRIPS_ONTOLOGY)

        print("Reduced to ", len(reduced))

        for s,p in reduced:
            Skeleton.objects.get_or_create(skeleton=s)
        print("Skeletons written in database")
