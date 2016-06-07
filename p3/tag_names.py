import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict

def count_tags(filename):
    tags = defaultdict(int)
    tree = ET.parse(filename)
    root = tree.getroot()
    for element in root.iter():
        tags[element.tag] += 1
    return tags

print count_tags('toronto_canada.osm')