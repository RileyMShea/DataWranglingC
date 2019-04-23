import json
from pymongo.results import InsertManyResult
from pymongo.database import Database
from typing import List
from pymongo.collection import Collection
from io import TextIOWrapper
from timeit import timeit


def json_to_mongo(json_file: str, col: Collection) -> List[InsertManyResult]:
    # makes a fresh collection from a json file
    with open(json_file, 'r') as f:  # type: TextIOWrapper
        data = json.load(f)  # type: List[list, list]
    col.drop()
    return [col.insert_many(x) for x in data]


def get_db(db_name: str) -> Database:
    # creates a mongodb Database object
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')  # type: MongoClient
    db = client[db_name]  # type: Database
    return db


def main():
    json_file = "rochester_osm.json"
    db = get_db("udacity")  # type: Database
    col = db.test_col  # type: Collection
    result = json_to_mongo(json_file=json_file, col=col)
    total = sum(len(x.inserted_ids) for x in result)
    print(f"{total} records inserted from {json_file}")
if __name__ == "__main__":
    print(timeit(main, number=1))
