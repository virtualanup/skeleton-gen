import requests
import xml.etree.ElementTree as ET
from pyparsing import OneOrMore, nestedExpr
import ast
from diesel import lisp

def parse(sentence):
    """
    Queries the web interface of TRIPS to parse the sentence. Returns the predicates
    extracted from the sentence
    """
    params = {
            "input":sentence,
            "extsformat":"svg",
            "tagsformat":"hidden",
            "treecontents":"phrase",
            "treeformat":"LinGO",
            "lfformat":"svg",
            "no-sense-words":"",
            "tag-type":"",
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
    return predicates
