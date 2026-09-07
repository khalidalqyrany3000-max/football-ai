from dotenv import load_dotenv
load_dotenv()

import os
import sqlite3
import feedparser

from ai_writer import analyze_news
from imaaage_generator import generate_image
from social_publisher import publish


# ============================================================
# SOURCES
# ============================================================

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


# ============================================================
# SETTINGS
# ============================================================

MAX_ARTICLES_PER_SOURCE = 10
MIN_SOURCE_RATING = 80
IMAGE_DIRECTORY = "generated_images"
PROCESS_ONE_ARTICLE = True


# ============================================================
# DATABASE
# ============================================================

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
    status TEXT DEFAULT 'ready',
    image_path TEXT,
    image_url TEXT,
    facebook_published INTEGER DEFAULT 0,
    instagram_published INTEGER DEFAULT 0
)
""")

conn.commit()


# ============================================================
# START
# ============================================================

print()
print("====================================")
print("⚽ Football AI Started 🚀")
print("====================================")

os.makedirs(IMAGE_DIRECTORY, exist_ok=True)


# ============================================================
# PROCESS SOURCES
# ============================================================

for source in sources:

    print()
    print("====================================")
    print("Checking source:", source["name"])
    print("Trust rating:", source["rating"])

    if source["rating"] < MIN_SOURCE_RATING:
        print("Source rejected")
        continue

    try:
        feed = feedparser.parse(source["url"])
    except Exception as error:
        print("❌ RSS error:", error)
        continue

    if not feed.entries:
        print("⚠️ No entries found.")
        continue

    print("Articles found:", len(feed.entries))


    # ========================================================
    # ARTICLES
    # ========================================================

    for item in feed.entries[:MAX_ARTICLES_PER_SOURCE]:

        title = str(getattr(item, "title", "")).strip()
        link = str(getattr(item, "link", "")).strip()

        if not title or not link:
            continue


        # ----------------------------------------------------
        # DUPLICATE CHECK
        # ----------------------------------------------------

        cursor.execute(
            "SELECT id FROM news WHERE link = ?",
            (link,)
        )

        if cursor.fetchone():
            print("Already exists:", title)
            continue


        # ----------------------------------------------------
        # SAVE NEWS
        # ----------------------------------------------------

        cursor.execute(
            "INSERT INTO news (title, link, source) VALUES (?, ?, ?)",
            (title, link, source["name"])
        )
        conn.commit()

        print()
        print("📰 New News:", title)


        # ----------------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------------

        try:
            result = analyze_news(title)
        except Exception as error:
            print("❌ AI Error:", error)
            continue


        # ----------------------------------------------------
        # FOOTBALL CHECK
        # ----------------------------------------------------

        if not result["is_football"]:
            print("Ignored: Not football")
            continue


        # ----------------------------------------------------
        # IMPORTANCE CHECK
        # ----------------------------------------------------

        if not result["is_important"]:
            print("Ignored: Not important")
            continue


        # ----------------------------------------------------
        # POST CHECK
        # ----------------------------------------------------

        post = result["post"].strip()

        if not post:
            print("Ignored: Empty post")
            continue

        print()
        print("🤖 AI Post:")
        print(post)


        # ----------------------------------------------------
        # DUPLICATE POST
        # ----------------------------------------------------

        cursor.execute(
            "SELECT id FROM posts WHERE post_text = ?",
            (post,)
        )

        if cursor.fetchone():
            print("Duplicate post")
            continue


        # ----------------------------------------------------
        # IMAGE PATH
        # ----------------------------------------------------

        safe_name = "".join(
            c if c.isalnum() else "_"
            for c in title
        )
        safe_name = safe_name[:80].strip("_")

        image_path = os.path.join(
            IMAGE_DIRECTORY,
            f"{safe_name}.jpg"
        )


        # ----------------------------------------------------
        # GENERATE IMAGE
        # ----------------------------------------------------

        try:
            generate_image(
                headline=post,
                design_type=result.get("category", "general"),
                output_path=image_path,
                team_a=result.get("primary_team", "UNKNOWN"),
                team_b=result.get("secondary_team", "UNKNOWN"),
                visual_type=result.get("visual_type", "generic"),
                visual_subject=result.get("visual_subject", "")
            )
        except Exception as error:
            print("❌ Image generation failed:", error)
            continue


        # ----------------------------------------------------
        # PUBLISH
        # ----------------------------------------------------

        print()
        print("📢 Publishing to Meta...")

        publish_results = publish(
            image_path=image_path,
            caption=post
        )

        facebook_ok = publish_results.get("facebook") is not None
        instagram_ok = publish_results.get("instagram") is not None
        image_url = publish_results.get("image_url", "")


        # ----------------------------------------------------
        # SAVE POST
        # ----------------------------------------------------

        if facebook_ok or instagram_ok:
            status = "published"
        else:
            status = "ready"

        cursor.execute(
            """
            INSERT INTO posts
            (news_title, post_text, status, image_path, image_url, facebook_published, instagram_published)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                post,
                status,
                image_path,
                image_url,
                1 if facebook_ok else 0,
                1 if instagram_ok else 0
            )
        )
        conn.commit()

        print()
        print("====================================")
        print("✅ Facebook:", "نجح" if facebook_ok else "فشل")
        print("✅ Instagram:", "نجح" if instagram_ok else "فشل")
        print("Status:", status)
        print("====================================")


        # ----------------------------------------------------
        # DONE — ONE ARTICLE ONLY
        # ----------------------------------------------------

        conn.close()

        print()
        print("====================================")
        print("Football AI Finished ✅")
        print("====================================")

        exit()


# ============================================================
# CLOSE
# ============================================================

conn.close()

print()
print("====================================")
print("No new articles found ✅")
print("====================================")