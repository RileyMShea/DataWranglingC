#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
In this problem set you work with another type of infobox data, audit it,
clean it, come up with a data model, insert it into MongoDB and then run some
queries against your database. The set contains data about Arachnid class
animals.

Your task in this exercise is to parse the file, process only the fields that
are listed in the FIELDS dictionary as keys, and return a list of dictionaries
of cleaned values.

The following things should be done:
- keys of the dictionary changed according to the mapping in FIELDS dictionary
- trim out redundant description in parenthesis from the 'rdf-schema#label'
  field, like "(spider)"
- if 'name' is "NULL" or contains non-alphanumeric characters, set it to the
  same value as 'label'.
- if a value of a field is "NULL", convert it to None
- if there is a value in 'synonym', it should be converted to an array (list)
  by stripping the "{}" characters and splitting the string on "|". Rest of the
  cleanup is up to you, e.g. removing "*" prefixes etc. If there is a singular
  synonym, the value should still be formatted in a list.
- strip leading and ending whitespace from all fields, if there is any
- the output structure should be as follows:

[ { 'label': 'Argiope',
    'uri': 'http://dbpedia.org/resource/Argiope_(spider)',
    'description': 'The genus Argiope includes rather large and spectacular spiders that often ...',
    'name': 'Argiope',
    'synonym': ["One", "Two"],
    'classification': {
                      'family': 'Orb-weaver spider',
                      'class': 'Arachnid',
                      'phylum': 'Arthropod',
                      'order': 'Spider',
                      'kingdom': 'Animal',
                      'genus': None
                      }
  },
  { 'label': ... , }, ...
]

  * Note that the value associated with the classification key is a dictionary
    with taxonomic labels.
"""
import codecs
import csv
import json
from pprint import pprint
import re

DATAFILE = 'arachnid.csv'
FIELDS = {'rdf-schema#label': 'label',
          'URI': 'uri',
          'rdf-schema#comment': 'description',
          'synonym': 'synonym',
          'name': 'name',
          'family_label': 'family',
          'class_label': 'class',
          'phylum_label': 'phylum',
          'order_label': 'order',
          'kingdom_label': 'kingdom',
          'genus_label': 'genus'}


def process_file(filename, fields):
    process_fields = fields.keys()
    pprint(process_fields)
    data = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f, fieldnames=process_fields)
        #print(reader.fieldnames)
        #reader.fieldnames = map(lambda x: fields[x], reader.fieldnames)

        # for c, v in enumerate(reader.fieldnames):
        #     reader.fieldnames[c] = fields[v]
        for i in range(4):
            l = reader.__next__()
            # pprint(l)

        for line in reader:
            # line.keys = map(lambda x: line.keys())
            new_dict = dict()
            for k, v in line.items():
                if k:
                    new_dict[fields[k]] = v
            data.append(new_dict)
    with open("processed.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)

    return data


def parse_array(v):
    if (v[0] == "{") and (v[-1] == "}"):
        v = v.lstrip("{")
        v = v.rstrip("}")
        v_array = v.split("|")
        v_array = [i.strip() for i in v_array]
        return v_array
    return [v]


def ztest():
    data = process_file(DATAFILE, FIELDS)
    print("Your first entry:")
    #test_entry = dict(data[0])

    #pprint(dict(data[0]))
    pprint(json.dumps(dict(data[0])))

    first_entry = {
        "synonym": None,
        "name": "Argiope",
        "classification": {
            "kingdom": "Animal",
            "family": "Orb-weaver spider",
            "order": "Spider",
            "phylum": "Arthropod",
            "genus": None,
            "class": "Arachnid"
        },
        "uri": "http://dbpedia.org/resource/Argiope_(spider)",
        "label": "Argiope",
        "description": "The genus Argiope includes rather large and spectacular spiders that often have a strikingly coloured abdomen. These spiders are distributed throughout the world. Most countries in tropical or temperate climates host one or more species that are similar in appearance. The etymology of the name is from a Greek name meaning silver-faced."
    }


    #pprint(first_entry)

    #assert len(data) == 76, "length not 76"
    assert dict(data[0]) == first_entry
    # assert data[17]["name"] == "Ogdenia"
    # assert data[48]["label"] == "Hydrachnidiae"
    # assert data[14]["synonym"] == ["Cyrene Peckham & Peckham"]


if __name__ == "__main__":
    ztest()
