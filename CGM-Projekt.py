import sqlite3
connection = sqlite3.connect('scores_CGM.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXITS highscores (
        name TEXT,
        score INTEGER,
        FOREIGN KEY(spieler_id) REFERENCES spieler(id)
)''')

cursor.execute("INSERT INTO Spielstand (spieler_id, name, score) VALUES (1, Spieler1, 0)")
cursor.execute("INSERT INTO Spielstand (spieler_id, name, score) VALUES (2, Spieler2, 0)")
connection.commit()

