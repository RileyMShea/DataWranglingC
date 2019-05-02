#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Your task is to use the iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
Fill out the count_tags function. It should return a dictionary with the
tag name as the key and number of times this tag can be encountered in
the map as value.

Note that your code will be tested with a different data file than the 'example.osm'
"""
import xml.etree.ElementTree as ET  # using regular elementTree b/c in Python3 it defaults to fast(c-based)
import pprint
from collections import defaultdict
import re
import pprint
import pickle


def count_tags(osm_file):
    osm_file = open(osm_file, "r", encoding="utf8")
    tag_types = dict()
    for event, elem in ET.iterparse(osm_file):
        if elem.tag in tag_types.keys():
            tag_types[elem.tag] += 1
        elif elem.tag not in tag_types.keys():
            tag_types[elem.tag] = 1
    return tag_types


def main():
    try:
        with open('data.pickle', 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            tags = pickle.load(f)
            print('Loaded parsed data from file, skipping iterparse')
    except Exception as e:
        print(f"{e}\nPeforming iterative parse")
        tags = count_tags(osm_file='rochester_sample.osm')
        with open("tag_data.pickle", 'wb', ) as f:
            pickle.dump(tags, f, pickle.HIGHEST_PROTOCOL)

    pprint.pprint(tags)


if __name__ == "__main__":
    main()
