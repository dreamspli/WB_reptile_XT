import sqlite3

# 连接到 SQLite 数据库
conn = sqlite3.connect('seen_ids.db')

# 创建游标对象
cur = conn.cursor()

# 查询数据
cur.execute("SELECT * FROM seen_ids")
rows = cur.fetchall()

for row in rows:
    print(row)

# 关闭连接
conn.close()
