# Jump and Run mit Datenbank
**Git-Projekt von Georg, Christin & Melina**

In unserem kleinen Jump-and-Run-Spiel haben wir verschiedene Funktionen eingebaut – unter anderem eine Datenbank (`scores_CGM.db`), die Highscores, gesammelte Münzen und Namen speichert. Die finale Version findet man in der Datei `CGM-Projekt.py`.

## Was macht das Spiel?
Ziel ist es, das Quadrat zu steuern und dabei möglichst weit zu kommen. Es gibt Hindernisse (Dreiecke), über die man springen kann (Leertaste) oder unter denen man durchrutscht (Strg-Taste). Währenddessen sammelt man Münzen ein.
Am Anfang wird nach einem Namen gefragt – dieser wird zusammen mit deinem Score und den Münzen in die Datenbank eingetragen. Wenn man nochmal spielst und besser ist als vorher, wird der alte Highscore automatisch überschrieben.
Nach jeder Runde sieht man die **Top 5 Spieler** (egal wer), also die besten Scores, die je erreicht wurden.
Mit `r` kann man eine neue Runde starten, mit `q` das Spiel beenden.

## Voraussetzungen
- Python 3
- pygame (`pip install pygame`)
- sqlite3 (ist bei Python standardmäßig dabei)

## Aufteilung
- Georg:
- Melina:
- Christin: Namen_eingeben, Highscoreliste, distanzeinfügen
