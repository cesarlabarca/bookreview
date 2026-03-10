import sqlite3

db = "library.db"

conn= sqlite3.connect(db)
cursor=conn.cursor()

cursor.execute("select * from activity")
rows = cursor.fetchall()

for row in rows:
  print(row)

conn.close()