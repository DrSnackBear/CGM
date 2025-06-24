import sqlite3
connection = sqlite3.connect('SpielCGM.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXITS spieler
        name TEXT,
        score INTEGER,
)''')
