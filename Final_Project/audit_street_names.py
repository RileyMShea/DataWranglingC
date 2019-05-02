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
import xml.etree.ElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "rochester_sample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)  # match the final word

expected = ["Street",
            "Avenue",
            "Boulevard",
            "Drive",
            "Court",
            "Place",
            "Square",
            "Lane",
            "Road",
            "Trail",
            "Parkway",
            "Commons"]

# UPDATE THIS VARIABLE
mapping = {"Avenu": "Avenue",
           "Ave.": "Avenue",
           "ave": "Avenue",
           "Ave": "Avenue",
           "Boulelvard": "Boulevard",
           "Blvd": "Boulevard",
           "Cir": "Circle",
           "N": "North",
           "Rd.": "Road",
           "Rd": "Road",
           "Stree": "Street",
           "St.": "Street",
           "St": "Street",
           "S": "South",
           "Dr": "Drive",
           "Dr.": "Drive"
           }
#
# mapping_dict = {['ave',
#                  'Ave',
#                  'Avenu', ]: 'Avenue',
#                 ['Blvd',
#                  'Boulelvard']: 'Boulevard',
#                ['Cir']: "Circle",
#                ['Ct']: "Court",
#                 ['Dr']: 'Drive',
#                 }
#
# tester = ['Apartment',
#           'ave',
#           'Ave',
#           'Avenu',
#           'Avenue',
#           'Bend',
#           'Blvd',
#           'Boulelvard',
#           'Boulevard',
#           'Bridge',
#           'Center',
#           'Cir',
#           'Circle',
#           'Court',
#           'Crescent',
#           'Ct',
#           'Dr',
#           'Drive',
#           'Drop',
#           'East',
#           'Green',
#           'Highway',
#           'Hill',
#           'Homes',
#           'Landing',
#           'Lane',
#           'line',
#           'Manor',
#           'Market',
#           'Meadows',
#           'North',
#           'Oaks',
#           'Park',
#           'Parkway',
#           'Passage',
#           'Place',
#           'PW',
#           'Race',
#           'Rd',
#           'Rise',
#           'Road',
#           'Run',
#           'South',
#           'Spruce',
#           'Square',
#           'St',
#           'Stree',
#           'Street',
#           'Trail',
#           'Villas',
#           'Way',
#           'West',
#           'Woods']
#

# affix = {"Avenue":
#
# }


# prefix_mapping =


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r", encoding="utf8")
    street_types = defaultdict(set)
    try:
        osm_parse_obj = ET.iterparse(osm_file, events=("start",))
        for event, elem in osm_parse_obj:
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if is_street_name(tag):
                        audit_street_type(street_types, tag.attrib['v'])
    except Exception as e:
        print(e)
    osm_file.close()
    return street_types


def update_name(name, mapping):
    for k, v in mapping.items():
        # my_regex = r'\S'+re.escape(k)+r'\n'
        my_regex = re.compile(f'{k}' r'[^\w\.]', re.IGNORECASE)
        my_regex = re.compile(f'{k}' r'$', re.IGNORECASE)
        if re.search(my_regex, name):
            name = name.replace(k, v)
            # break
    return name


def main():
    st_types = audit(OSMFILE)
    # assert len(st_types) == 3
    # pprint.pprint(sorted(list(dict(st_types).keys())))

    with open('street_identifiers.txt', 'w', encoding="utf8") as f:
        for key in dict(st_types).keys():
            f.write(key)

    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping=mapping)
            print(f"{name}=>{better_name}")


if __name__ == '__main__':
    main()
