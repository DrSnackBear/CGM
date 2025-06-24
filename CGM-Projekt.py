import sqlite3
connection = sqlite3.connect('SpielCGM.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXITS spieler
        name TEXT,
        score INTEGER,
)''')

cursor.execute("INSERT INTO spieler (spieler_id, name, fähigkeit, gold VALUES (1, Georg, Bogenschießer, 3)")
cursor.execute("INSERT INTO spieler (spieler_id, name, fähigkeit, gold VALUES (2, Melina, Magierin, 4)")
cursor.execute("INSERT INTO spieler (spieler_id, name, fähigkeit, gold VALUES (3, Christin, Schwertkämpferin, 5)")
connection.commit()