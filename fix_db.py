import sqlite3

conn = sqlite3.connect('news.db')
cursor = conn.cursor()

# حذف كل المنشورات التي ليس لها مسار صورة
cursor.execute("DELETE FROM posts WHERE image_path IS NULL OR image_path = ''")
conn.commit()

print("✅ تم حذف جميع المنشورات التي ليس لها صورة")

# عرض المنشورات المتبقية
cursor.execute("SELECT id, news_title, image_path FROM posts WHERE status='ready'")
rows = cursor.fetchall()
if rows:
    print("\n📰 المنشورات المتبقية:")
    for row in rows:
        print(f"ID: {row[0]}, Title: {row[1]}, Image: {row[2]}")
else:
    print("\n📭 لا يوجد منشورات جاهزة. شغّل main.py أولاً.")

conn.close()