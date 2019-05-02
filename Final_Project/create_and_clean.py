#!/usr/bin/env python
# coding: utf-8

import json
from pprint import pprint
from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.mongo_client import database
from tqdm import tnrange, tqdm


def get_suffix_mapping():
    """get a mapping for street suffixes by scraping table from USPS"""
    headers = {'User-agent': 'Mozilla/5.0'}
    r = requests.get(r"https://pe.usps.com/text/pub28/28apc_002.htm", headers=headers)

    soup = BeautifulSoup(r.content, 'lxml')

    postal_table = soup.find('table', {'id': 'ep533076'})

    df = pd.read_html(str(postal_table), header=0)[0]
    df.columns = ['Primary', 'Common', 'Standard']

    keys = df.iloc[:, 1:3]

    return keys.to_dict(orient='records')


def tqdm_ipython_test():
    """testing tdqm works in jupyter lab"""
    for i in tnrange(3, desc='1st loop'):
        for j in tqdm(range(100), desc='2nd loop'):
            sleep(0.01)


def read_osm_file(filename: str):
    """reads in osm file to be processed"""
    with open(filename, "r", encoding='UTF-8') as f:
        msg = f.read()
    return msg


def get_soup(file, tags):
    """generate some resultsets for the tags from the xml """
    soup = BeautifulSoup(file, 'xml')
    return [{tag: soup.find_all(tag)} for tag in tqdm(tags)]


def get_dict_data(result_set_item):
    """generate dictionaries from the resultsets"""
    list_of_dicts = []
    for k, v in result_set_item:
        primary_tag = k
        result_set = v
    for entry in result_set:
        entry_data_dict = dict()
        entry_data_dict['type'] = primary_tag
        for k, v in entry.attrs.items():
            entry_data_dict[k] = v
        for tag in entry.find_all('tag'):
            entry_data_dict[tag['k']] = tag['v']
        list_of_dicts.append(entry_data_dict)
    return list_of_dicts


def json_to_mongo(col: database.Collection, json_file: str = "rochester_osm.json"):
    """create new mongodb collection from json file"""
    with open(json_file) as f:
        data = json.load(f)
    for node_dict in data:
        col.insert_many(node_dict)


def get_col(db_name="udacity", collection="rochester_osm"):
    """create and return a mongodb db/collection connection object"""
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    col = db[collection]
    return col


def main():
    """currently set to use sample extract, for full implementation see jupyter notebook version of this file"""
    pprint("Processing dataset.. ")

    file_name = r"rochester_sample.osm"  # change name if using full extract

    base = file_name.split('.')[0]
    osm_file = read_osm_file(filename=file_name)
    tag_list = ['node', 'way']
    result_set_list = get_soup(file=osm_file, tags=tag_list)
    osm_dicts = [get_dict_data(res.items()) for res in result_set_list]
    json_osm = json.dumps(osm_dicts)
    with open(f"{base}.json", 'w') as f:
        f.write(json_osm)
    from importlib import import_module

    j2m = import_module('json_to_mongo')
    j2m.main(json_file=f"{base}.json")

    # setup connection for data exploration and cleaning
    osm_col = get_col(collection=base)  # type: MongoClient

    # ### Query total document count

    # In[134]:

    total_docs = osm_col.count_documents({})
    pprint(total_docs)

    # ### Get count of each key in collection

    # In[135]:

    key_counts_dict = dict()
    for entry in tqdm(osm_col.find(), total=total_docs):
        for k in entry.keys():
            key_counts_dict.setdefault(k, 0)
            key_counts_dict[k] += 1

    # In[136]:

    [print(f"{k}, {v} ") for k, v in key_counts_dict.items() if ':city' in k]

    # In[137]:

    # itemgetter used with sorted to allow sorting by key values
    from operator import itemgetter

    pprint(sorted(key_counts_dict.items(), key=itemgetter(1), reverse=True))

    # ### Get a list of fields that begin with address

    # In[138]:

    address_fields = {k: v for (k, v) in key_counts_dict.items() if 'addr' in k}
    pprint(sorted(address_fields.items(), key=itemgetter(1), reverse=True))

    # In[139]:

    # Get a list of distinct streets
    distinct_streets = osm_col.distinct('addr:street')

    # In[140]:

    change_needed = list()

    mapping_dict = get_suffix_mapping()
    distinct_suffix = set(x.split()[-1] for x in distinct_streets)

    # In[164]:

    pprint(mapping_dict[0:5])

    # In[142]:

    for suffix in distinct_suffix:
        for mapping in mapping_dict:
            if mapping['Common'] == suffix.upper():
                print(f"Changing {suffix} to {mapping['Standard']}")
                continue

    # In[143]:

    modified_count = 0
    for entry in tqdm(distinct_streets):
        suffix = entry.split()[0]
        for mapping in mapping_dict:
            if mapping['Common'] == suffix.upper():
                # print(f"Changing {suffix} to {mapping['Standard']}")
                # print(entry.replace(suffix, mapping['Standard']))
                result = osm_col.update_many({'addr:street': entry},
                                             {"$set": {'addr:street': entry.replace(suffix, mapping['Standard'])}})
                modified_count += result.modified_count
                continue
    print(f"{modified_count} address suffixes updated")

    # In[144]:

    # Get a list of distinct street types
    pprint(set(x.split()[-1] for x in distinct_streets if x.split()[-1].isalpha()))

    # In[145]:

    # Get a list of distinct street types
    pprint(set(x.split()[-1] for x in distinct_streets))

    # ### find all address codes in collection

    # In[146]:

    unique_zip_codes = osm_col.distinct('addr:postcode')
    pprint(unique_zip_codes)

    # In[147]:

    update_dict = {'modified': 0,
                   'deleted': 0,
                   'good': 0}
    for zip in tqdm(unique_zip_codes):
        if zip[0:5].isdigit() and len(zip) > 5:
            result = osm_col.update_many({'addr:postcode': zip}, {"$set": {'addr:postcode': zip[0:5]}})
            update_dict['modified'] += result.modified_count
        elif not zip.isdigit() and len(zip) != 5:
            result = osm_col.delete_many({'addr:postcode': zip})
            update_dict['deleted'] += result.deleted_count
        elif zip.isdigit() and len(zip) == 5:
            update_dict['good'] += 1

    pprint(update_dict)

    # In[148]:

    #
    updated_address_code_list = list(osm_col.find({'addr:postcode': {'$exists': True}}, {'addr:postcode': 1, '_id': 0}))
    set([x['addr:postcode'] for x in updated_address_code_list])

    # [Rochester Zip codes](https://www.zip-codes.com/city/ny-rochester.asp)
    # > After running our function we can see that all the unique zip codes in the database are valid Rochester Zip codes

    # In[149]:

    pprint(list(osm_col.aggregate([
        {
            '$group': {
                '_id': '$addr:postcode',
                'count': {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                'count': -1
            }
        }
    ]))[:10])

    # # User Counts

    # In[150]:

    def get_single_users(col: Collection):
        user_counts_dict = list(col.aggregate([
            {
                '$sortByCount': '$user'
            }, {
                '$sort': {
                    'count': 1
                }
            }
        ]))
        single_doc_user = list()
        for entry in user_counts_dict:
            if entry['count'] == 1:
                single_doc_user.append(entry['_id'])
            else:
                break
        pprint(single_doc_user[0:5])
        pprint(f"{len(single_doc_user)} users with only one post out of {len(user_counts_dict)}")
        # return single_doc_user

    get_single_users(osm_col)

    # In[151]:

    user_df = pd.DataFrame.from_dict(list(osm_col.aggregate([{
        '$sortByCount': '$user'
    }])))
    user_df['percent'] = user_df['count'] / user_df['count'].sum()

    # In[152]:

    # Percent of entries that came from top two users
    user_df[0:2]['percent'].sum() * 100

    # In[153]:

    # Combined top 10 users contribution
    user_df[0:10]['percent'].sum() * 100

    # In[154]:

    # Combined perecent of users who individually contribute less then 1% of the entries in the database
    user_df[user_df.percent <= .01].percent.sum() * 100

    # In[155]:

    user_df._id

    # In[156]:

    def top_ten_amenities(col: Collection):
        top_amenities = list(col.aggregate([
            {
                '$match': {
                    'type': 'way'
                }
            }, {
                '$sortByCount': '$amenity'
            }
        ]))
        return top_amenities

    top_ten_amenities(col=osm_col)[0:10]

    # In[157]:

    df = pd.DataFrame.from_dict(top_ten_amenities(osm_col))
    pprint(df[0:10])

    # In[158]:

    df['percent'] = df['count'] / df['count'].sum()

    # ``` table
    # _id|count|percent\r\n|49953|0.951069055461417\r\nparking|1828|0.034803800239894905\r\nrestaurant|127|0.0024179883098832894\r\nschool|85|0.001618338632599052\r\nfuel|56|0.0010661995697123165\r\n
    # ```

    # In[159]:

    df[1:].describe()

    # In[160]:

    df.shape[0]

    # In[161]:

    # Biggest Religion
    religion = list(osm_col.aggregate([
        {
            '$match': {
                'amenity': {
                    '$eq': 'place_of_worship'
                }
            }
        }, {
            '$group': {
                '_id': '$religion',
                'count': {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                'count': -1
            }
        }
    ]))
    pprint(religion)

    # In[162]:

    # Most popular cuisine in restaurants
    cuisine = list(osm_col.aggregate([
        {
            '$match': {
                'amenity': {
                    '$eq': 'restaurant'
                }
            }
        }, {
            '$group': {
                '_id': '$cuisine',
                'count': {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                'count': -1
            }
        }
    ]))
    pprint(cuisine[0:10])

    # In[163]:

    # City counts
    city_counts = list(osm_col.aggregate([
        {
            '$group': {
                '_id': '$addr:city',
                'count': {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                'count': -1
            }
        }
    ]))
    print('\n'.join('{_id!s:<20}{count}'.format(**x) for x in city_counts))


if __name__ == '__main__':
    main()
# ### Initial MongoDB collection creation
# - Insert all records from json file
# - Create compound unique index on 'id' and 'type' fields

# read the json file we just read to verify it's working
