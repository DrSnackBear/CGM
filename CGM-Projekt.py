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

cursor.execute("INSERT INTO spieler (spieler_id, name, fähigkeit, gold VALUES (1, Georg, Bogenschießer, 3)")
cursor.execute("INSERT INTO spieler (spieler_id, name, fähigkeit, gold VALUES (2, Melina, Magierin, 4)")
cursor.execute("INSERT INTO spieler (spieler_id, name, fähigkeit, gold VALUES (3, Christin, Schwertkämpferin, 5)")
connection.commit()