# Skeleton
Sentence skeleton extraction from the Lore knowledge base to improve TRIPS parser.

To load sentences and generate skeletons:

    python extract_skeletons.py -i data/input/money_sentence_subset -o data/output/money_sentence_predicates

To merge common skeletons:

    python merge_skeletons.py -i data/output/money_sentence_predicates -o data/output/merged_money_sentence_predicates
