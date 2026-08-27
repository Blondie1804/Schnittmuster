# Schnittmuster-Katalog

Ein Verzeichnis deiner 794 Schnitte. Die Schnittmuster selbst bleiben, wo sie sind –
in `OneDrive\DIY\Schnittmuster`. Diese Seite enthält sie nicht, sie zeigt nur darauf.

## Einrichten

**Erst richtig entpacken.** Rechtsklick auf `Schnittmuster-Katalog.zip` →
*„Alle extrahieren…"* → Ordner wählen. Es reicht **nicht**, das ZIP im Explorer nur
zu öffnen und `index.html` daraus anzuklicken – dann packt Windows nur diese eine
Datei aus, die Schnittliste fehlt, und die Seite findet nichts. (Falls das passiert,
sagt sie es dir inzwischen deutlich.)

1. Den entpackten Ordner dorthin legen, wo du ihn wiederfindest – z. B.
   `OneDrive\DIY\Schnittmuster-Katalog`. **Nicht** in den Schnittmuster-Ordner selbst.
2. `index.html` per Doppelklick öffnen. Fertig – kein Server, kein Internet nötig.

Neben `index.html` müssen liegen: `daten.js`, `uebersicht.js` und die Ordner
`bilder` und `schriften`.

Falls du den Schnittmuster-Ordner später verschiebst: in `scan.py` ganz oben
die Zeile `BASIS = ...` anpassen.

## Eigene Schnitte anlegen

Nicht jeder Schnitt liegt als PDF im OneDrive. Über **+ Schnitt** oben legst du
selbst welche an:

- **📄 Papierschnitt** – der Bogen liegt bei dir zu Hause. Trag unter
  *„Papierbögen liegen in"* ein, wo (Box 3, Ordner blau …), dann findest du ihn wieder.
- **💛 Wunschliste** – möchtest du noch kaufen. Statt *Herkunft* fragt die Seite hier
  *„Wo gibt es ihn?"* mit Shop und Preis.

Beide werden ganz normal mitgesucht und mitgefiltert. Auf der Karte erkennst du sie
am farbigen Band oben links. Löschen kannst du sie im Detailfenster unten rechts –
gescannte Schnitte lassen sich nicht löschen, die kommen ja aus dem Ordner.

Links in der Filterleiste gibt es dafür die Gruppe **Bestand**: Digital, Papier,
Wunschliste.

## Schon ausgedruckt?

Bei digitalen Schnitten gibt es im Detailfenster den Haken
**🖨 Schon ausgedruckt und zusammengeklebt**. Ist er gesetzt, trägt die Karte ein
grünes Band – du siehst also auf einen Blick, wo du direkt losnähen kannst und wo
erst der Copyshop wartet.

Links unter *Status* filterst du auf **🖨 Ausgedruckt da**.

## Die Dateien zum Anklicken

| Datei | wofür |
|---|---|
| `index.html` | **Deine Datenbank.** Suchen, filtern, Schnitte pflegen. |
| `1 Neu einlesen.bat` | Nach neuen Schnitten suchen. Deine Eingaben bleiben erhalten. |
| `2 Uebersichten einlesen.bat` | Deine Excel-Übersichten neu auswerten. |
| `3 Teilen-Seite bauen.bat` | Erzeugt `teilen.html` für Freundinnen. |

## Suchen

Tippe wie du sprichst:

- `T-Shirt mit Puffärmeln`
- `Kleid Jersey`
- `oversize pulli`
- `Lybstes` (Designer)
- `Tasche Reißverschluss`

Über dem Suchfeld steht, was die Seite verstanden hat. Alles, was sie nicht als
Merkmal kennt, sucht sie als Text in Namen und Notizen.

Links kannst du zusätzlich filtern. Die Zahlen zeigen, wie viele Treffer je Merkmal
übrig bleiben.

## Warum manche Suchen wenig finden

Der Katalog speist sich aus zwei Quellen: den Dateinamen im OneDrive-Ordner und
deinen sechs Excel-Übersichten. Zusammen ergibt das:

| Merkmal | erfasst | woher |
|---|---|---|
| Was für ein Teil | 91 % | Dateiname |
| Größen | 43 % | Dateiname + Übersicht |
| Stoff | 30 % | Übersicht |
| Stoffverbrauch | 34 % | Übersicht |
| Vorschaubild | 26 % | Übersicht |
| Designer | 27 % | Dateiname |
| Details | 8 % | Dateiname |
| **Ausschnitt** | **6 %** | Dateiname |
| **Ärmelform** | **5 %** | Dateiname |

Ärmelform und Ausschnitt stehen fast nie im Dateinamen und standen auch nicht in
den Übersichten – die stecken im Foto oder im PDF. Deshalb findet
`T-Shirt mit Puffärmeln` anfangs nur wenige Treffer.

Genau dafür ist der Balken über den Ergebnissen da: *„Bei 155 weiteren Schnitten passt
alles andere, aber Ärmel ist noch nicht erfasst."* Ein Klick zeigt sie dir.

## Was aus deinen Excel-Übersichten kam

Aus den sechs Dateien in `_Übersicht` sind **277 Schnitte** angereichert worden:
Größe, Stoffart, Stoffverbrauch und bei 210 davon auch das Vorschaubild.

Die Zuordnung läuft über den Namen und ist nicht immer eindeutig – deine Excel-Zeile
heißt "Pully Caby", der Ordner "pulli caby nähanleitung schnitt made-by-oranges".
Meistens passt das, manchmal nicht:

- **11 Zuordnungen sind unsicher.** Diese Schnitte zeigen im Detailfenster einen
  farbigen Hinweis. Bitte kurz prüfen, ob Größe und Bild wirklich zu dem Schnitt gehören.
- **34 Excel-Zeilen konnte ich gar nicht zuordnen** – z. B. "Bluse Penny" oder
  "Costa Rica". Die stehen vermutlich unter einem anderen Namen im Ordner.

Beides steht in `uebersicht-pruefen.txt`. Korrigieren kannst du alles direkt in der
Seite; deine Eingabe gewinnt immer gegen die automatische Übernahme.

Die Vorschaubilder sind die Produktfotos der Designer. Sie liegen im Ordner `bilder/`
und bleiben in deiner örtlichen Ansicht – in die Teilen-Seite kommen sie **nicht**.

## Nachpflegen

Klick auf eine Karte. Merkmale setzt du per Klick auf die Chips, Pfötchen für die
Bewertung (1 bis 5), dazu Felder für Stoffverbrauch, Anpassungen, Kaufdaten und Notizen.

Zwei Knöpfe unten:
- **Speichern** – zurück zur Übersicht
- **Speichern & nächster ungepflegter** – bleibt im Fluss, ideal für eine Serie

Gepflegte Einträge bekommen ein ✓. Oben rechts blendet **„Nur ungepflegte"** die
fertigen aus.

Realistisch sind rund 20 Sekunden pro Schnitt. Du musst nicht alle 794 machen –
pfleg die, die du wirklich suchst. Der Rest wird über die Textsuche trotzdem gefunden.

## Sichern und Zurückladen (wichtig)

Deine Eingaben und deine selbst angelegten Schnitte liegen im Browserspeicher.
Der überlebt einen Rechnerwechsel oder geleerte Browserdaten **nicht**.

Klick regelmäßig oben auf **Sichern**. Das lädt `schnittmuster-pflegedaten.json`
herunter – leg die Datei in diesen Ordner. Sie enthält beides: die Angaben zu
gescannten Schnitten und deine Papier-/Wunschliste-Einträge.

Mit **Laden** holst du eine solche Datei wieder zurück – nach einem Browserwechsel,
auf einem zweiten Rechner oder wenn mal etwas schiefging. Achtung: Das *ersetzt*,
was gerade im Browser steht; die Seite fragt vorher nach.

## Hell und Dunkel

Der Mond/Sonne-Knopf oben rechts schaltet um. Ohne Auswahl richtet sich die Seite
nach deiner Windows-Einstellung.

## Teilen mit Freundinnen

1. In der Seite auf **Sichern** klicken
2. `schnittmuster-pflegedaten.json` aus dem Download-Ordner hierher legen
3. `3 Teilen-Seite bauen.bat` doppelklicken → erzeugt `teilen.html`

Diese eine Datei kannst du verschicken. Sie enthält:

✅ Namen, Merkmale, Designer, Größen, Schwierigkeit, Stoffart, Stoffverbrauch
✅ deine Erfahrungen: genäht, Bewertung, Anpassungen, Notizen
✅ Shop-Link, wo du ihn eingetragen hast
✅ deine Papierschnitte und deine Wunschliste – gekennzeichnet, damit Freundinnen
   sehen, was du hast und was du dir wünschst

❌ **keine** Schnittmuster-Dateien
❌ **keine** Dateipfade oder Dateinamen
❌ **keine** Kaufpreise, Kaufdaten oder Ablageorte
❌ **keine** Vorschaubilder (das sind Fotos der Designer)
❌ **keine** Angabe, wo deine Papierbögen liegen

## Zum Rechtlichen

Der Katalog sind deine eigenen Daten – Namen, Merkmale, deine Meinung. Den darfst du
teilen wie eine Buchempfehlungsliste.

Die Schnittmuster selbst sind urheberrechtlich geschützt. Sie zu kopieren wäre eine
Privatkopie und in Ordnung; sie zugänglich zu machen wäre es nicht. Die Grenze
verläuft nicht bei „ich verkaufe nichts", sondern bei „andere kommen dran".

Zwei Dinge, die du vermeiden solltest:

1. **Keine OneDrive-Freigabelinks vom Typ „Jeder mit dem Link"** auf den
   Schnittmuster-Ordner. Das ist der eine Klick, der aus Privatkopie
   Veröffentlichung macht – auch ohne Absicht und ohne Geld.
2. **Keine Produktfotos der Designer** in die geteilte Version. Das ist schon so
   eingerichtet: Die Bilder aus deinen Übersichten bleiben örtlich. Deine eigenen
   Fotos deiner genähten Teile wären dagegen unproblematisch.

Wenn du magst, trag bei den Schnitten den Shop-Link ein. Dann wird die geteilte Seite
für die Designer eher Werbung als Ärger.

*(Kein Rechtsrat – aber das ist die Linie, an der sich das üblicherweise entscheidet.)*

## Übersichten erneut einlesen

Wenn du in den Excel-Dateien etwas ergänzt: `2 Uebersichten einlesen.bat`.

Ein Stolperstein: Die Dateien müssen **örtlich verfügbar** sein. Bei dir waren sie
reine OneDrive-Platzhalter (18–96 MB, aber nur in der Cloud) – dann kann sie kein
Programm öffnen. Im Explorer Rechtsklick auf `_Übersicht` →
*"Immer auf diesem Gerät behalten"*, warten bis grüne Haken erscheinen.

Alternativ den Ordner mit den xlsx-Dateien einfach auf die .bat-Datei ziehen.

## Neue Schnitte aufnehmen

Neue Schnitte einfach wie gewohnt in `OneDrive\DIY\Schnittmuster` ablegen, dann
`1 Neu einlesen.bat` doppelklicken. Alles, was du von Hand eingetragen hast, bleibt –
zugeordnet über den Ablageort. Wenn du einen Schnitt in einen anderen Ordner
verschiebst, gilt er als neu und du trägst ihn einmal nach.

## Wenn Python fehlt

Nur die drei `.bat`-Dateien brauchen Python. Die Seite selbst läuft auch ohne –
`daten.js`, `uebersicht.js` und die Bilder liegen ja schon fertig daneben.

Python gibt es unter python.org – beim Installieren „Add Python to PATH" ankreuzen.
Für `2 Uebersichten einlesen.bat` wird zusätzlich Pillow gebraucht (verkleinert die
Bilder aus den Excel-Dateien):

    pip install Pillow
