import feedparser
import sqlite3
from ai_writer import rewrite_news


sources = [
    {
        "name": "Football Italia",
        "url": "https://www.football-italia.net/feed/",
        "rating": 80
    },
    {
        "name": "BBC Sport Football",
        "url": "https://feeds.bbci.co.uk/sport/football/rss.xml",
        "rating": 90
    },
    {
        "name": "Sky Sports Football",
        "url": "https://www.skysports.com/rss/12040",
        "rating": 90
    },
    {
        "name": "ESPN Football",
        "url": "https://www.espn.com/espn/rss/soccer/news",
        "rating": 85
    }
]


keywords = [
    "transfer",
    "signed",
    "signs",
    "agreement",
    "deal",
    "medical",
    "contract",
    "joins",
    "bid",
    "interest"
]


conn = sqlite3.connect("news.db")
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    link TEXT UNIQUE,
    source TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    news_title TEXT,
    post_text TEXT UNIQUE,
    status TEXT DEFAULT 'ready'
)
""")


conn.commit()


print("⚽ Football AI Started 🚀")


for source in sources:

    print("\nChecking source:", source["name"])
    print("Trust rating:", source["rating"])


    if source["rating"] < 80:
        print("Source rejected")
        continue


    feed = feedparser.parse(source["url"])


    for item in feed.entries[:10]:

        title = item.title
        link = item.link


        important = any(
            word in title.lower()
            for word in keywords
        )


        if not important:
            print("Ignored:", title)
            continue



        cursor.execute(
            "SELECT * FROM news WHERE link = ?",
            (link,)
        )


        if cursor.fetchone():

            print("Already exists:", title)
            continue



        cursor.execute(
            """
            INSERT INTO news
            (title, link, source)
            VALUES (?, ?, ?)
            """,
            (
                title,
                link,
                source["name"]
            )
        )

        conn.commit()


        print("\n📰 New News:")
        print(title)



        post = rewrite_news(title)


        print("\n🤖 AI Post:")
        print(post)



        cursor.execute(
            "SELECT * FROM posts WHERE post_text = ?",
            (post,)
        )


        if cursor.fetchone():

            print("Duplicate post")
            continue



        cursor.execute(
            """
            INSERT INTO posts
            (news_title, post_text)
            VALUES (?, ?)
            """,
            (
                title,
                post
            )
        )

        conn.commit()


        print("✅ Saved")



conn.close()


print("\nFinished ✅")