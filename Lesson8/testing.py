def no_map():
    items = [1, 2, 3, 4, 5]
    squared = []
    for i in items:
        squared.append(i ** 2)
    from pprint import pprint
    pprint(squared)


def with_map():
    items = [1, 2, 3, 4, 5]
    squared = list(map(lambda x: x ** 2, items))
    from pprint import pprint
    pprint(squared)


with_map()


def make_pipeline():
    # complete the aggregation pipeline
    pipeline = [{"$match": {"user.time_zome": {"$eq": "Brasilia"},
                            "user.statuses_count": {"$gte": 100}}},
                {"$project": {"followers": "$user.followers_count",
                              "screen_name": "$user.screen_name",
                              "tweets": "$user.statuses_count"}},
                {"$sort": {"followers": -1}},
                {"$limit": 1}]

    return pipeline
