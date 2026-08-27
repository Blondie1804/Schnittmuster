# -*- coding: utf-8 -*-
"""
Baut aus dem Katalog eine eigenstaendige Seite zum Weitergeben: teilen.html

Was NICHT mitgeht: Dateipfade, Dateinamen, Dateigroessen, Kaufpreis, Kaufdatum,
Ablageort der Papierboegen. Es geht nur mit, was fuer andere nuetzlich ist -
Name, Merkmale, Designer, Groessen, deine Erfahrung und ggf. der Shop-Link.

Vorher in der Seite einmal auf "Sichern" klicken; die heruntergeladene Datei
schnittmuster-pflegedaten.json hierher legen (oder im Download-Ordner lassen).
"""
import os, json, io, re, glob

HIER = os.path.dirname(os.path.abspath(__file__))
DATEN = os.path.join(HIER, "daten.js")
AUSGABE = os.path.join(HIER, "teilen.html")

# Nur diese Felder verlassen den Rechner
OEFFENTLICH = ["id", "titel", "kategorie", "unterkategorie", "teilart", "aermel",
               "ausschnitt", "passform", "details", "stoff", "designer", "groessen",
               "freebook", "schwierigkeit", "stoffart", "stoffverbrauch", "kurzwaren",
               "genaeht", "anzahlGenaeht", "meineGroesse", "anpassungen", "bewertung",
               "notizen", "shopLink", "bestand"]
# "bild" fehlt hier mit Absicht: das sind die Produktfotos der Designer.
# Sie duerfen in der oertlichen Ansicht stehen, aber nicht in einer weitergegebenen Datei.


def pflegedaten_finden():
    """Sucht die gesicherten Handeingaben hier und im Download-Ordner."""
    kandidaten = [os.path.join(HIER, "schnittmuster-pflegedaten.json")]
    kandidaten += sorted(
        glob.glob(os.path.join(os.path.expanduser("~"), "Downloads",
                               "schnittmuster-pflegedaten*.json")),
        key=os.path.getmtime, reverse=True)
    for k in kandidaten:
        if not os.path.exists(k):
            continue
        try:
            with io.open(k, encoding="utf8") as f:
                d = json.load(f)
        except Exception:
            continue
        # Neues Format: {"pflege": {...}, "eigene": [...]}
        # Altes Format: einfach {...} mit den Pflegedaten
        if isinstance(d, dict) and "pflege" in d:
            return d.get("pflege", {}), d.get("eigene", []), k
        return d, [], k
    return {}, [], None


def main():
    if not os.path.exists(DATEN):
        print("daten.js fehlt - bitte zuerst scan.py ausfuehren."); return

    roh = io.open(DATEN, encoding="utf8").read()
    schnitte = json.loads(roh[roh.index("["):roh.rindex("]") + 1])

    # Angaben aus den Excel-Uebersichten (Groesse, Stoffart, Stoffverbrauch)
    ueber = {}
    pfad_ueber = os.path.join(HIER, "uebersicht.js")
    if os.path.exists(pfad_ueber):
        try:
            ru = io.open(pfad_ueber, encoding="utf8").read()
            ueber = json.loads(ru[ru.index("{"):ru.rindex("}") + 1])
            print("Übersichts-Angaben übernommen: %d Schnitte" % len(ueber))
        except Exception as ex:
            print("uebersicht.js nicht lesbar (%s)" % ex)

    pflege, selbst, quelle = pflegedaten_finden()
    if quelle:
        print("Pflegedaten uebernommen aus: %s" % quelle)
    else:
        print("Keine Pflegedaten gefunden - es geht nur der automatische Stand mit.")
        print("(In der Seite auf \"Sichern\" klicken, Datei hierher legen, nochmal starten.)")

    # Selbst angelegte Schnitte (Papier / Wunschliste) mit aufnehmen
    schnitte = list(schnitte) + list(selbst)
    if selbst:
        print("Selbst angelegte Schnitte: %d" % len(selbst))

    raus = []
    for e in schnitte:
        e = dict(e)
        u = dict(ueber.get(e["id"], {}))
        u.pop("bild", None)                 # Designer-Fotos bleiben hier
        u = {k: v for k, v in u.items() if not k.startswith("_")}
        e.update(u)
        e.update(pflege.get(e["id"], {}))
        raus.append({k: e.get(k, "") for k in OEFFENTLICH})

    for e in raus:
        if not e.get("bestand"):
            e["bestand"] = "digital"

    nur_gepflegt = [e for e in raus if any(
        e.get(f) for f in ["aermel", "ausschnitt", "passform", "details", "stoff",
                           "notizen", "bewertung", "genaeht"])]

    vorlage = io.open(os.path.join(HIER, "teilen-vorlage.html"), encoding="utf8").read()
    html = vorlage.replace("/*HIER_DATEN*/", json.dumps(raus, ensure_ascii=False))
    io.open(AUSGABE, "w", encoding="utf8").write(html)

    mb = os.path.getsize(AUSGABE) / 1048576
    print("\nGeschrieben: %s  (%.1f MB)" % (AUSGABE, mb))
    print("  %d Schnitte, davon %d mit eigenen Angaben" % (len(raus), len(nur_gepflegt)))
    print("\nDiese eine Datei kannst du weitergeben. Sie enthaelt KEINE Schnittmuster,")
    print("keine Dateipfade und keine Kaufdaten - nur den Katalog.")


if __name__ == "__main__":
    main()
