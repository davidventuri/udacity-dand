import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
from num2words import num2words

OSMFILE = "toronto_canada.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
num_line_street_re = re.compile(r'\d0?(st|nd|rd|th|)\s(Line)$', re.IGNORECASE) # spell lines ten and under
nth_re = re.compile(r'\d\d?(st|nd|rd|th|)', re.IGNORECASE)
nesw_re = re.compile(r'\s(North|East|South|West)$') # don't need because works in update name


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Circle", "Crescent", "Gate", "Terrace", "Grove", "Way"]

mapping = { "St": "Street",
            "St.": "Street",
            "STREET": "Street",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "Dr.": "Drive",
            "Dr": "Drive",
            "Rd": "Road",
            "Rd.": "Road",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "Ehs": "EHS",
            "Trl": "Trail",
            "Cir": "Circle",
            "Cir.": "Circle",
            "Ct": "Court",
            "Ct.": "Court",
            "Crt": "Court",
            "Crt.": "Court",
            "By-pass": "Bypass",
            "N.": "North",
            "N": "North",
            "E.": "East",
            "E": "East",
            "S.": "South",
            "S": "South",
            "W.": "West",
            "W": "West"
            }

street_mapping = {
            "St": "Street",
            "St.": "Street",
            "ST": "Street",
            "STREET": "Street",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "Rd.": "Road",
            "Dr.": "Drive",
            "Dr": "Drive",
            "Rd": "Road",
            "Rd.": "Road",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "Ehs": "EHS",
            "Trl": "Trail",
            "Cir": "Circle",
            "Cir.": "Circle",
            "Ct": "Court",
            "Ct.": "Court",
            "Crt": "Court",
            "Crt.": "Court",
            "By-pass": "Bypass"
                }

num_line_mapping = { "1st": "First",
                     "2nd": "Second",
                     "3rd": "Third",
                     "4th": "Fourth",
                     "5th": "Fifth",
                     "6th": "Sixth",
                     "7th": "Seventh",
                     "8th": "Eighth",
                     "9th": "Ninth",
                     "10th": "Tenth"
                    }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit_street(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name):
    if num_line_street_re.match(name):
        nth = nth_re.search(name)
        name = num_line_mapping[nth.group(0)] + " Line"
        return name
    
    elif name == "York & Durham Line" or name == "York/Durham Line":
        name = "York-Durham Line"
        return name

    else:
        original_name = name
        for key in mapping.keys():
            # Only replace when mapping key match (e.g. "St.") is found at end of name
            type_fix_name = re.sub(r'\s' + re.escape(key) + r'$', ' ' + mapping[key], original_name)
            nesw = nesw_re.search(type_fix_name)
            if nesw is not None:
                for key in street_mapping.keys():
                    # Do not update correct names like St. Clair Avenue West
                    dir_fix_name = re.sub(r'\s' + re.escape(key) + re.escape(nesw.group(0)), " " + street_mapping[key] + nesw.group(0), type_fix_name)
                    if dir_fix_name != type_fix_name:
                        print original_name + "=>" + type_fix_name + "=>" + dir_fix_name
                        return dir_fix_name
            if type_fix_name != original_name:
                print original_name + "=>" + type_fix_name
                return type_fix_name
    # Check if avenue, road, street, etc. are capitalized
    last_word = original_name.rsplit(None, 1)[-1]
    if last_word.islower():
        original_name = re.sub(last_word, last_word.title(), original_name)
    return original_name


################# POSTAL CODE AUDIT

# POSTCODE = re.compile(r'[A-z]\d[A-z]\s?\d[A-z]\d')
# def audit_postcode(osmfile):
#     post_file = open(osmfile, "r")
#     for event, elem in ET.iterparse(post_file, events=("start",)):
        # if elem.tag == "node" or elem.tag == "way":
        #     for tag in elem.iter("tag"):
        #         if tag.attrib['k'] == 'addr:postcode':
        #             post_code = re.sub(" ", "", tag.attrib['v'].strip())
        #             m = POSTCODE.match(post_code)
        #             if m is None:
        #                 print post_code      
#     post_file.close()

# audit_postcode(OSMFILE)

################# STREET NAME AUDIT

# st_types = audit_street(OSMFILE)
# pprint.pprint(dict(st_types))

# for st_type, ways in st_types.iteritems(): # key, value pairs are {'Ave': set(['N. Lincoln Ave', 'North Lincoln Ave']),
#     for name in ways:
#         better_name = update_name(name)
#         print name, "=>", better_name