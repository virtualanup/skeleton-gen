"""
Merge skeletons based on ontology
"""
import argparse


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description='Merge common skeletons that have similar ontology and role combinaions')
    arg_parser.add_argument('-i', '--input', help='Input File', required=True)
    arg_parser.add_argument(
        '-o', '--output', help='Output File', required=True)

    args = arg_parser.parse_args()

    skeletons = filter(lambda x: x.startswith(
        "("), map(lambda x: x.strip(), open(args.input)))
    print(list(skeletons))
