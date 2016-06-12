"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
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


def audit(osmfile):
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
        # print name
        nth = nth_re.search(name)
        name = num_line_mapping[nth.group(0)] + " Line"
        # print name
        return name
    
    elif name == "York & Durham Line" or name == "York/Durham Line":
        # print name
        name = "York-Durham Line"
        # print name
        return name

    else:
        original_name = name
        for key in mapping.keys():
            # only replace when mapping key match (e.g. "St.") is found at end of name
            type_fix_name = re.sub(r'\s' + key + r'$', " " + mapping[key], name)
            nesw = nesw_re.search(type_fix_name)
            if nesw:
                for key in street_mapping.keys():
                    # do not update correct names like St. Clair Avenue West
                    dir_fix_name = re.sub(r'\s' + key + nesw.group(0), " " + street_mapping[key] + nesw.group(0), type_fix_name)
                    if dir_fix_name != type_fix_name:
                        # print original_name + "=>" + type_fix_name + "=>" + dir_fix_name
                        return dir_fix_name
            if type_fix_name != original_name:
                # print original_name + "=>" + type_fix_name
                return type_fix_name
    # check if avenue, road, street, etc. are capitalized
    last_word = original_name.rsplit(None, 1)[-1]
    if last_word.islower():
        original_name = re.sub(last_word, last_word.title(), original_name)
    return original_name

        # if dir_fix_name:
        #     if type_fix_name != dir_fix_name:
        #             break

    # if name[-2:] in mapping:
    #     print "before: " + name
    #     name = name[:-2] + mapping[name[-2:]]
    #     print "after: " + name
    # elif name[-3:] in mapping:
    #     name = name[:-3] + mapping[name[-3:]]
    #     print name
    # elif name[-4:] in mapping:
    #     name = name[:-4] + mapping[name[-4:]]
    #     print name
    # elif name[-5:] in mapping:
    #     name = name[:-5] + mapping[name[-5:]]
    #     print name
    # elif name[-6:] in mapping:
    #     name = name[:-6] + mapping[name[-6:]]
    #     print name
    # elif name[-7:] in mapping:
    #     name = name[:-7] + mapping[name[-7:]]
    #     print name

    # name = mapping[name]
    # return name

# st_types = audit(OSMFILE)
# pprint.pprint(dict(st_types))

# for st_type, ways in st_types.iteritems(): # key, value pairs are {'Ave': set(['N. Lincoln Ave', 'North Lincoln Ave']),
#     for name in ways:
#         better_name = update_name(name)
#         print name, "=>", better_name