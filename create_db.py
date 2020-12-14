import sqlite3 as sql

connect = sql.connect('catalogue.db')
cnt = connect.cursor()

cnt.execute("DROP TABLE IF EXISTS users")
cnt.execute("DROP TABLE IF EXISTS  books")
cnt.execute("DROP TABLE IF EXISTS  images")

cnt.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
cnt.execute("CREATE TABLE books(idx INTEGER PRIMARY KEY, bookInfo TEXT)")
cnt.execute("CREATE TABLE images(url TEXT, indx INTEGER, FOREIGN KEY (indx) REFERENCES books(idx))")
cnt.execute("INSERT INTO users VALUES(1, 'admin', 'password')")

connect.commit()
connect.close()
