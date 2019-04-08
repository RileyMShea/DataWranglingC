#!/usr/bin/env python
from pymongo import MongoClient


def make_pipeline():
    # complete the aggregation pipeline
    pipeline = [{"$match": {"user.time_zone": "Brasilia",
                            "user.statuses_count": {"$gte": 100}}},
                {"$project": {"followers": "$user.followers_count",
                              "screen_name": "$user.screen_name",
                              "tweets": "$user.statuses_count"}},
                {"$sort": {"followers": -1}},
                {"$limit": 1}]

    pipeline2 = [
        {
            '$match': {
                'user.time_zone': 'Brasilia',
                'user.statuses_count': {
                    '$gte': 100
                }
            }
        }, {
            '$project': {
                'followers': '$user.followers_count',
                'screen_name': '$user.screen_name',
                'tweets': '$user.statuses_count'
            }
        }, {
            '$sort': {
                'followers': -1
            }
        }, {
            '$limit': 5
        }
    ]
    return pipeline


def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db


def aggregate(db, pipeline):
    return [doc for doc in db.tweets.aggregate(pipeline)]


if __name__ == '__main__':
    db = get_db('twitter')
    pipeline = make_pipeline()
    result = aggregate(db, pipeline)
    import pprint

    pprint.pprint(result)
    # assert len(result) == 1
    # assert result[0]["followers"] == 17209

[
    {
        '$match': {
            'user.time_zone': 'Brasilia',
            'user.statuses_count': {
                '$gte': 100
            }
        }
    }, {
    '$project': {
        'followers': '$user.followers_count',
        'screen_name': '$user.screen_name',
        'tweets': '$user.statuses_count'
    }
}, {
    '$sort': {
        'followers': -1
    }
}, {
    '$limit': 5
}
]
