import requests
import xml.etree.ElementTree as ET
from pyparsing import OneOrMore, nestedExpr
import ast
from diesel import lisp
import re


def parse(sentence):
    """
    Queries the web interface of TRIPS to parse the sentence. Returns the predicates
    extracted from the sentence
    """
    params = {
        "input": sentence,
        "extsformat": "svg",
        "tagsformat": "hidden",
        "treecontents": "phrase",
        "treeformat": "LinGO",
        "lfformat": "svg",
        "no-sense-words": "",
        "tag-type": "",
        "senses-only-for-penn-poss": "",
    }
    a = requests.get("http://trips.ihmc.us/parser/cgi/parse", params=params)
    root = ET.fromstring(a.text)
    utt = root.find("utt")
    terms = utt.find("terms")
    lisp_section = terms.find("lisp")
    lispcode = lisp_section.text

    # Load the predicates using diesel lisp parser
    predicates = lisp.extract_predicates(lispcode)
    # Along with the predicates, return the word match also. For example, in
    # A person may raise money, raise should have role ONT::collect. Return
    # mapping from ONT::COLLECT to W::RAISE also
    pattern = re.compile("\([:][*] ONT::([A-Za-z\-]*) W::([A-Za-z\-]*)\)")
    role_dict = {}
    for match in pattern.finditer(lispcode):
        role_dict[match.group(1).lower()] = match.group(2).lower()
    return predicates, role_dict
