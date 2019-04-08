# %%
# -*- coding: utf-8 -*-


import json
import cchardet as chardet

from bs4 import BeautifulSoup


def read_osm_file(filename):
    with open(filename, "rb") as f:
        msg = f.read()
        result = chardet.detect(msg)
    return msg


def get_soup(file, tags):
    soup = BeautifulSoup(file, 'xml')
    return [{tag: soup.find_all(tag)} for tag in tags]


def get_dict_data(result_set_item):
    list_of_dicts = []
    for k, v in result_set_item:
        primary_tag = k
        result_set = v
    for entry in result_set:
        entry_data_dict = {}
        entry_data_dict['type'] = primary_tag
        for k, v in entry.attrs.items():
            entry_data_dict[k] = v
        for tag in entry.find_all('tag'):
            entry_data_dict[tag['k']] = tag['v']
        list_of_dicts.append(entry_data_dict)
    return list_of_dicts


def json_to_mongo(json_file, col):
    data = []
    with open(json_file) as f:
        for line in f:
            data.append(json.loads(line))
    return col.insert_many(data)


def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db


def main():
    file_name = "rochester_ny.osm"
    osm_file = read_osm_file(filename=file_name)
    tag_list = ['node', 'way']
    result_set_list = get_soup(file=osm_file, tags=tag_list)

    osm_dicts = [get_dict_data(res) for res in result_set_list.values()]

    with open("osm_dicts", 'w') as f:
        f.write(osm_dicts)
    # json_file = "twitter.json"
    # db = get_db("udacity")
    # col = db.twitter
    # json_to_mongo(json_file=json_file, col=col)

# %%
if __name__ == "__main__":
    main()


# %%
file_name = r"C:\Users\Riley\PycharmProjects\DataWrangling\Final_Project\rochester_ny.osm"
osm_file = read_osm_file(filename=file_name)

# %%
tag_list = ['node', 'way']
result_set_list = get_soup(file=osm_file, tags=tag_list)

# %%


osm_dicts = [get_dict_data(res.items()) for res in result_set_list]
# osm_dicts = [get_dict_data(res) for res in result_set_list.values()]

#%%
json_osm = json.dumps(osm_dicts)

#%%

with open('rochester_osm.json', 'w') as f:
    f.write(json_osm)

#%%
with open(r'C:\Users\Riley\PycharmProjects\DataWrangling\rochester_osm.json', 'r') as f:
    json_osm = f.read()

data = json.loads(json_osm)
#%%
db = get_db("udacity")
col = db.rochester_osm
for dl in osm_dicts:
    col.insert_many(dl)

#%%
json_file = "rochester_osm.json"

json_to_mongo(json_file=json_file, col=col)
# %%
from pymongo import MongoClient

client = MongoClient('localhost:27017')
db = client["udacity"]
osm_col = db["rochester_osm"]

# %%
from pprint import pprint

pipeline = [
    {
        '$project': {
            'arrayofkeyvalue': {
                '$objectToArray': '$$ROOT'
            }
        }
    }, {
        '$unwind': {
            'path': '$arrayofkeyvalue'
        }
    }, {
        '$group': {
            '_id': None,
            'allkeys': {
                '$addToSet': '$arrayofkeyvalue.k'
            }
        }
    }
]

unique_osm_keys = list(osm_col.aggregate(pipeline=pipeline))

pprint(list(osm_col.aggregate(pipeline=pipeline)))

# %%



