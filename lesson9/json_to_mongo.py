import json

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
    json_file = "twitter.json"
    db = get_db("udacity")
    col = db.twitter
    json_to_mongo(json_file=json_file, col=col)


if __name__ == "__main__":
    main()
