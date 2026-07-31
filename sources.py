SOURCES = [
    {
        "name": "Fabrizio Romano",
        "rating": 100
    },
    {
        "name": "Club Official",
        "rating": 100
    },
    {
        "name": "David Ornstein",
        "rating": 95
    },
    {
        "name": "Florian Plettenberg",
        "rating": 90
    },
    {
        "name": "Unknown Source",
        "rating": 20
    }
]


def get_source_rating(source_name):
    for source in SOURCES:
        if source["name"] == source_name:
            return source["rating"]

    return 0