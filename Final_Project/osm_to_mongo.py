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

# Loading The osm file
file_name = r"C:\Users\Riley\PycharmProjects\DataWrangling\Final_Project\rochester_ny.osm"
osm_file = read_osm_file(filename=file_name)

# %%
# Loading the osm file into beautiful soup and grabbing all node and way tags
tag_list = ['node', 'way']
result_set_list = get_soup(file=osm_file, tags=tag_list)

# %%

# make list of dictionaries containing the attribute and tag data for the result set
osm_dicts = [get_dict_data(res.items()) for res in result_set_list]
# osm_dicts = [get_dict_data(res) for res in result_set_list.values()]

# %%
# dump this dict data to a json file so that parsing doesn't need to be re-run
json_osm = json.dumps(osm_dicts)

# %%
# write the json to file
with open('rochester_osm.json', 'w') as f:
    f.write(json_osm)

# %%
# read the json file we just read to verify it's working
with open(r'C:\Users\Riley\PycharmProjects\DataWrangling\rochester_osm.json', 'r') as f:
    json_osm = f.read()

data = json.loads(json_osm)
# %%
#connect to the database/collection we'll be storing the osm data in
db = get_db("udacity")
col = db.rochester_osm
for dl in osm_dicts:
    col.insert_many(dl)

# %%
# use function we defined to upload our json data to the collection
json_file = "rochester_osm.json"

json_to_mongo(json_file=json_file, col=col)
# %%
#setup connection for data exploration and cleaning

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
address_fields = [x for x in unique_osm_keys[0]['allkeys'] if str(x).startswith('addr')]
pprint(sorted(address_fields))

# %%

return_field = {'_id': False,
                'addr:postcode': True}

addres_code_list = list(osm_col.find({'addr:postcode': {'$exists': True}}, {'addr:postcode': 1, '_id': 0}))
pprint(addres_code_list)

# %%
unique_zip_codes = set([x['addr:postcode'] for x in addres_code_list])
pprint(unique_zip_codes)

# %%

testersss = list(osm_col.find({'addr:postcode': "1445033"}, {'_id': 0}))

# %%
testersss = list(osm_col.find({'addr:postcode': "West Main Street"}))

myquery = {'id': "1609006999"}
newvalues = [{"$set": {"addr:postcode": "14614"}},
             {"$set": {"addr:street": "West Main Street"}}]

for value in newvalues:
    update_s = osm_col.update_one(myquery, value)
    pprint(update_s.raw_result)
    pprint(update_s.upserted_id)

# %%

pprint(list(osm_col.find({'id': '1609006999'})))
# %%
zips_to_fix = [x for x in unique_zip_codes if len(x) > 5 and str(x)[0:5].isdigit()]

# %%

for value in zips_to_fix:
    myquery = {"addr:postcode": value}
    value = {"$set": {"addr:postcode": str(value[0:5])}}
    update_s = osm_col.update_one(myquery, value)
    pprint(update_s.raw_result)
    pprint(update_s.upserted_id)
    pprint(update_s.acknowledged)
    pprint(update_s.matched_count)

# %%
updated_address_code_list = list(osm_col.find({'addr:postcode': {'$exists': True}}, {'addr:postcode': 1, '_id': 0}))
set([x['addr:postcode'] for x in updated_address_code_list])
