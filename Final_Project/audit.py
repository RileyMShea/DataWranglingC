#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pprint
import re
import xml.etree.ElementTree as ET

"""
Your task is to explore the data a bit more.
Before you process the data and add it into your database, you should check the
"k" value for each "<tag>" and see if there are any potential problems.

We have provided you with 3 regular expressions to check for certain patterns
in the tags. As we saw in the quiz earlier, we would like to change the data
model and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}
So, we have to see if we have such tags, and if we have any tags with
problematic characters.

Please complete the function 'key_type', such that we have a count of each of
four tag categories in a dictionary:
  "lower", for tags that contain only lowercase letters and are valid,
  "lower_colon", for otherwise valid tags with a colon in their names,
  "problemchars", for tags with problematic characters, and
  "other", for other tags that do not fall into the other three categories.
See the 'process_map' and 'test' functions for examples of the expected format.
"""


def key_type(element, keys):
    lower = re.compile(r'^([a-z]|_)*$')  # matches any string comprised of only lowercase letters or underscores
    lower_colon = re.compile(
        r'^([a-z]|_)*:([a-z]|_)*$')  # looks for strings of lowercase/underscores separated by colon

    problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

    if element.tag == "tag":
        tag_key = element.attrib['k']
        # tag_value = element.attrib['v']
        if re.search(lower, tag_key):
            keys['lower'] += 1
        elif re.search(lower_colon, tag_key):
            keys['lower_colon'] += 1
        elif re.search(problemchars, tag_key):
            keys['problemchars'] += 1
        else:
            keys['other'] += 1
    return keys


def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys


def main():
    keys = process_map('rochester_sample.osm')
    pprint.pprint(keys)


if __name__ == "__main__":
    try:
        main()
    finally:
        pass
