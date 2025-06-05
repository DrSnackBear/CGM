import sqlite3
connection = sqlite3.connect('SpielCGM.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXITS spieler
        id INTEGER PRIMARY KEY,
        spieler_id INTEGER,
        name TEXT,
        fähigkeit TEXT,
        gold INTEGER,
        FOREIGN KEY(spieler_id) REFERNCES spieler(id)
)''')
