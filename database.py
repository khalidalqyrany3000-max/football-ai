import sqlite3

conn = sqlite3.connect("news.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,
    link TEXT UNIQUE,
    source TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully")