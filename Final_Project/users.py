#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pprint
import xml.etree.ElementTree as ET

"""
Your task is to explore the data a bit more.
The first task is a fun one - find out how many unique users
have contributed to the map in this particular area!

The function process_map should return a set of unique user IDs ("uid")
"""


def get_user(element):
    try:
        if type(element.attrib['user']) == type(str()):
            return element.attrib['user']
    except:
        pass


def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if type(get_user(element)) == type(str()):
            users.add(get_user(element))

    return users


def main():
    users = process_map('rochester_sample.osm')
    pprint.pprint(users)


if __name__ == "__main__":
    main()
