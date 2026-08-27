# -*- coding: utf-8 -*-
"""
Liest die Excel-Uebersichten aus _Uebersicht ein und reichert den Katalog an:
Groesse, Stoffart, Stofflaenge und das Vorschaubild je Schnitt.

Die Bilder sind Produktfotos der Designer. Sie landen NUR in der oertlichen
Ansicht (Ordner bilder/) und werden von teilen.py bewusst nicht mitgenommen.

Aufruf:  python uebersicht_einlesen.py <Ordner mit den xlsx-Dateien>
"""
import os, re, sys, io, json, zipfile, glob, hashlib, unicodedata
from difflib import SequenceMatcher
from PIL import Image

HIER = os.path.dirname(os.path.abspath(__file__))
DATEN = os.path.join(HIER, "daten.js")
BILDORDNER = os.path.join(HIER, "bilder")
UEBERNAHME = os.path.join(HIER, "uebersicht.js")

# Aus der Freitext-Spalte "Stoffart" die filterbaren Merkmale ableiten.
# Gleiche Werte wie in scan.py, damit die Filterleiste eine Sprache spricht.
STOFF_ERKENNUNG = [
    ("Jersey",    ["jersey"]),
    ("Sweat",     ["sweat", "french terry"]),
    ("Walk",      ["walk"]),
    ("Musselin",  ["musselin", "musling", "double gauze"]),
    ("Leinen",    ["leinen", "linen"]),
    ("Webware",   ["webware", "canvas", "popeline", "baumwollstoff", "blusenstoff",
                   "webstoff", "batist"]),
    ("Softshell", ["softshell"]),
    ("Fleece",    ["fleece", "frottee", "plüsch", "teddy", "nicki"]),
    ("Viskose",   ["viskose", "viscose", "modal"]),
]


def stoffe_aus_text(t):
    t = (t or "").lower()
    return [wert for wert, begriffe in STOFF_ERKENNUNG if any(b in t for b in begriffe)]

THUMB_BREITE = 420      # reicht fuer die Kartenansicht
THUMB_QUALI = 78


# ----------------------------------------------------------------- Excel lesen
def zellen_einer_datei(z):
    """Gibt {zeile: {spalte: text}} zurueck."""
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        roh = z.read("xl/sharedStrings.xml").decode("utf8", "ignore")
        # <si> kann mehrere <t> enthalten (Formatwechsel) - zusammenfuegen
        for si in re.findall(r"<si>(.*?)</si>", roh, re.S):
            ss.append("".join(re.findall(r"<t[^>]*>(.*?)</t>", si, re.S)))

    def entschaerfe(s):
        s = s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
        s = s.replace("&quot;", '"').replace("&#10;", "\n")
        return re.sub(r"[\r\n]+", " / ", s).strip()

    sh = z.read("xl/worksheets/sheet1.xml").decode("utf8", "ignore")
    zeilen = {}
    for r, inhalt in re.findall(r'<row[^>]*r="(\d+)"[^>]*>(.*?)</row>', sh, re.S):
        werte = {}
        for sp, attr, v in re.findall(
                r'<c r="([A-Z]+)\d+"([^>]*)>(?:<v>(.*?)</v>)?', inhalt):
            if v is None or v == "":
                continue
            if 't="s"' in attr:
                try:
                    werte[sp] = entschaerfe(ss[int(v)])
                except (ValueError, IndexError):
                    pass
            elif not v.startswith("#"):
                werte[sp] = entschaerfe(v)
        if werte:
            zeilen[int(r)] = werte
    return zeilen


def bilder_je_zeile(z):
    """Ordnet jeder Excel-Zeile ihre eingebetteten Bilder zu."""
    treffer = {}
    for dpfad in [n for n in z.namelist() if re.match(r"xl/drawings/drawing\d+\.xml$", n)]:
        dr = z.read(dpfad).decode("utf8", "ignore")
        relpfad = dpfad.replace("drawings/", "drawings/_rels/") + ".rels"
        if relpfad not in z.namelist():
            continue
        rels = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"',
                               z.read(relpfad).decode("utf8", "ignore")))
        # sowohl twoCellAnchor als auch oneCellAnchor erfassen
        for block in re.findall(r"<xdr:(?:two|one)CellAnchor.*?</xdr:(?:two|one)CellAnchor>",
                                dr, re.S):
            mr = re.search(r"<xdr:from>.*?<xdr:row>(\d+)</xdr:row>.*?</xdr:from>", block, re.S)
            mi = re.search(r'r:embed="(rId\d+)"', block)
            if not (mr and mi):
                continue
            ziel = rels.get(mi.group(1), "")
            if not ziel:
                continue
            pfad = "xl/" + ziel.replace("../", "")
            # xdr:row ist zeilenbasiert ab 0 -> Excel-Zeile = +1
            treffer.setdefault(int(mr.group(1)) + 1, []).append(pfad)
    return treffer


# ----------------------------------------------------------------- Abgleich
def nur_name(bez):
    """Aus 'Heartclover-Kleid / (gerades Kleid mit Peplum) / (Langarm)' wird
    'Heartclover-Kleid'. Die Zusaetze beschreiben Varianten und wuerden beim
    Abgleich falsche Stichwoerter liefern."""
    bez = bez.split(" / ")[0]
    bez = re.sub(r"\([^)]*\)", " ", bez)
    return re.sub(r"\s+", " ", bez).strip(" -/")


def schluessel(s):
    """Vergleichsform: klein, ohne Umlaute, ohne Fuellwoerter und Sonderzeichen."""
    s = s.lower()
    for a, b in [("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss"),("'","")]:
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"\b(schnittmuster|ebook|e-book|freebook|naehanleitung|anleitung|"
               r"damen|gr|komplett|by|the|und|mit|fuer|von|im|in)\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# Gattungswoerter. Sie stehen in fast jedem Titel und taugen nicht zur
# Unterscheidung - "Kleid Ava" und "Tonalco Kleid" haben nur das Wort gemeinsam.
GENERISCH = {
    "kleid", "kleider", "shirt", "shirts", "tshirt", "top", "tops", "bluse",
    "blusen", "blusenshirt", "pulli", "pullis", "pullover", "hoodie", "sweater",
    "hose", "hosen", "rock", "jacke", "jacken", "mantel", "weste", "overall",
    "jumpsuit", "body", "set", "dress", "gown", "skirt", "pants", "tee", "tunika",
    "tunica", "basic", "classic", "langarm", "kurzarm", "arm", "aermel", "sleeve",
    "oversize", "slim", "wide", "belt", "raffung", "jersey", "musselin", "sweat",
    "leinen", "webware", "viskose", "sommer", "summer", "winter", "damen", "herren",
    "kinder", "baby", "mini", "midi", "maxi", "lang", "kurz", "gross", "klein",
    "badeanzug", "bikini", "unterwaesche", "hoeschen", "slip", "swimwear",
}


def woerter(s):
    return {w for w in schluessel(s).split() if len(w) > 2}


# Wird zur Laufzeit aus dem Katalog gefuellt: Woerter, die in vielen Titeln
# vorkommen, unterscheiden nichts. Das faengt auch Gattungsbegriffe, an die
# beim Schreiben der Liste oben niemand gedacht hat (tie, bralette, bodysuit...).
HAEUFIG = set()


def haeufige_woerter_bestimmen(katalog, grenze=0.012):
    zaehler = {}
    for e in katalog:
        for w in woerter(e["titel"]):
            zaehler[w] = zaehler.get(w, 0) + 1
    schwelle = max(3, int(len(katalog) * grenze))
    return {w for w, n in zaehler.items() if n >= schwelle}


def kern(s):
    """Nur die unterscheidenden Wortteile - Modellnamen, keine Gattungsbegriffe."""
    return {w for w in schluessel(s).split()
            if len(w) > 2 and w not in GENERISCH and w not in HAEUFIG}


def finde_partner(bez, kandidaten):
    """Bestes Gegenstueck im Katalog. Rueckgabe (eintrag, guete 0..1).

    Zwei Signale, weil keins allein reicht:
      - Wortvergleich  faengt umgestellte Titel ("Kleid Juna" / "Juna Kleid")
      - Zeichenvergleich faengt zusammengeschriebene ("Hoodiekleid" / "hoodie kleid")
    """
    bw, bk = woerter(bez), kern(bez)
    if not bk:
        return None, 0          # ohne Modellname keine sichere Zuordnung moeglich
    bs = "".join(sorted(bk))    # Vergleichskette nur aus den Kernwoertern

    bester, beste_guete = None, 0
    for e in kandidaten:
        kw, kk = woerter(e["titel"]), kern(e["titel"])
        if not kk:
            continue

        # (1) Kernwoerter, die exakt uebereinstimmen
        gemein = bk & kk
        g1 = 0
        if gemein:
            g1 = 0.6 + 0.4 * len(gemein) / len(bk)
            if any(len(w) >= 5 for w in gemein):
                g1 = min(1.0, g1 + 0.15)

        # (2) Zeichenvergleich je Kernwortpaar - faengt Schreibvarianten
        #     ("Fanny"/"Fanni", "Hoodiekleid"/"hoodie kleid", Tippfehler)
        g2 = 0
        for a in bk:
            for b in kk:
                m = SequenceMatcher(None, a, b).find_longest_match(0, len(a), 0, len(b))
                if m.size >= 5 and m.size / max(len(a), len(b)) >= 0.7:
                    g2 = max(g2, 0.55 + 0.35 * m.size / max(len(a), len(b)))

        guete = max(g1, g2)
        # kleiner Zuschlag, wenn auch die Gattung passt (Kleid zu Kleid)
        if guete and (bw & kw) - bk:
            guete = min(1.0, guete + 0.05)

        if guete > beste_guete:
            bester, beste_guete = e, guete
    return bester, round(min(beste_guete, 1.0), 2)


# ----------------------------------------------------------------- Hauptlauf
def main():
    # Ohne Angabe: der _Übersicht-Ordner neben den Schnittmustern.
    # Wichtig: die Dateien muessen oertlich verfuegbar sein, nicht nur als
    # OneDrive-Platzhalter (im Explorer: Rechtsklick > "Immer behalten").
    standard = r"C:\Users\LSchneider\OneDrive\DIY\Schnittmuster\_Übersicht"
    quelle = sys.argv[1] if len(sys.argv) > 1 else standard
    if not os.path.isdir(quelle):
        print("Ordner nicht gefunden: %s" % quelle)
        print("Zieh den Ordner mit den xlsx-Dateien auf diese .bat-Datei,")
        print("oder rufe auf: python uebersicht_einlesen.py <Ordner>")
        sys.exit(1)
    dateien = sorted(glob.glob(os.path.join(quelle, "*.xlsx")))
    if not dateien:
        print("Keine xlsx-Dateien in:", quelle); sys.exit(1)

    roh = io.open(DATEN, encoding="utf8").read()
    katalog = json.loads(roh[roh.index("["):roh.rindex("]") + 1])
    os.makedirs(BILDORDNER, exist_ok=True)

    global HAEUFIG
    HAEUFIG = haeufige_woerter_bestimmen(katalog)
    print("Als Gattungswoerter erkannt (%d): %s"
          % (len(HAEUFIG), ", ".join(sorted(HAEUFIG))))
    print("")

    uebernahme = {}     # id -> Felder
    bericht = []
    unklar = []
    angenommen = []
    fehlende = []

    for f in dateien:
        name = os.path.basename(f)
        # "_Damen T-Shirts.xlsx" -> Unterkategorie "T-Shirts"
        unter = re.sub(r"^_Damen\s*", "", name).replace(".xlsx", "").strip()
        try:
            z = zipfile.ZipFile(f)
        except (zipfile.BadZipFile, OSError):
            # Typisch fuer OneDrive "Dateien bei Bedarf": die Datei ist nur ein
            # Platzhalter, der Inhalt liegt in der Cloud.
            print("  %s laesst sich nicht oeffnen." % name)
            print("     Vermutlich ein OneDrive-Platzhalter. Im Explorer Rechtsklick")
            print("     auf den Ordner _Uebersicht > \"Immer auf diesem Geraet behalten\",")
            print("     warten bis die gruenen Haken erscheinen, dann nochmal starten.")
            fehlende.append(name)
            continue
        zeilen = zellen_einer_datei(z)
        bilder = bilder_je_zeile(z)

        # Kandidaten: bevorzugt gleiche Unterkategorie, sonst ganze Kategorie Damen
        eng = [e for e in katalog if e["kategorie"] == "Damen"
               and schluessel(e["unterkategorie"]) == schluessel(unter)]
        weit = [e for e in katalog if e["kategorie"] == "Damen"]

        gefunden = fehl = 0
        for r in sorted(zeilen):
            if r == 1:
                continue                      # Kopfzeile
            zl = zeilen[r]
            bez = zl.get("A", "").strip()
            if not bez:
                continue

            name = nur_name(bez)
            e, guete = finde_partner(name, eng or weit)
            if guete < 0.75 and (eng or weit) is not weit:
                e2, g2 = finde_partner(name, weit)
                if g2 > guete:
                    e, guete = e2, g2

            if not e or guete < 0.62:
                fehl += 1
                unklar.append((unter, name, e["titel"] if e else "-", guete))
                continue

            angenommen.append((unter, name, e["titel"], guete))
            feld = uebernahme.setdefault(e["id"], {})
            if zl.get("B"): feld["groessen"] = zl["B"]
            if zl.get("C"):
                feld["stoffart"] = zl["C"]
                erkannt = stoffe_aus_text(zl["C"])
                if erkannt:
                    feld["stoff"] = erkannt
            if zl.get("D"): feld["stoffverbrauch"] = zl["D"]
            feld["_quelle"] = unter
            feld["_guete"] = guete

            # Bild sichern
            for bp in bilder.get(r, [])[:1]:
                try:
                    im = Image.open(io.BytesIO(z.read(bp)))
                    if im.mode in ("RGBA", "P", "LA"):
                        hg = Image.new("RGB", im.size, (255, 255, 255))
                        hg.paste(im, mask=im.convert("RGBA").split()[-1])
                        im = hg
                    else:
                        im = im.convert("RGB")
                    if im.width > THUMB_BREITE:
                        im = im.resize((THUMB_BREITE,
                                        round(im.height * THUMB_BREITE / im.width)),
                                       Image.LANCZOS)
                    ziel = e["id"] + ".jpg"
                    im.save(os.path.join(BILDORDNER, ziel), "JPEG",
                            quality=THUMB_QUALI, optimize=True)
                    feld["bild"] = "bilder/" + ziel
                except Exception as ex:
                    print("  Bild uebersprungen (%s): %s" % (bp, ex))
            gefunden += 1

        bericht.append((unter, len(zeilen) - 1, gefunden, fehl))
        z.close()

    if fehlende and not uebernahme:
        print("")
        print("Keine einzige Uebersicht konnte gelesen werden - nichts geaendert.")
        return

    with io.open(UEBERNAHME, "w", encoding="utf8") as f:
        f.write("// Aus den Excel-Uebersichten erzeugt von uebersicht_einlesen.py\n")
        f.write("window.UEBERSICHT = ")
        json.dump(uebernahme, f, ensure_ascii=False, indent=1)
        f.write(";\n")

    # ------------------------------------------------------------- Bericht
    print("Datei                     Zeilen  zugeordnet  offen")
    for unter, n, g, fh in bericht:
        print("  %-22s %5d %10d %6d" % (unter, n, g, fh))
    mit_bild = sum(1 for v in uebernahme.values() if v.get("bild"))
    print("\nInsgesamt %d Schnitte angereichert, davon %d mit Vorschaubild."
          % (len(uebernahme), mit_bild))
    if os.path.isdir(BILDORDNER):
        mb = sum(os.path.getsize(os.path.join(BILDORDNER, x))
                 for x in os.listdir(BILDORDNER)) / 1048576
        print("Bilder-Ordner: %.1f MB" % mb)

    if angenommen:
        angenommen.sort(key=lambda x: x[3])
        print("")
        print("Schwaechste angenommene Zuordnungen (zur Kontrolle):")
        for unter, bez, tit, g in angenommen[:18]:
            print("  %.2f  %-38s -> %s" % (g, bez[:38], tit[:44]))

    if unklar:
        print("\nNicht sicher zugeordnet (%d) - Stichprobe:" % len(unklar))
        for unter, bez, verm, g in unklar[:25]:
            print("  [%s] %-42s -> %-38s (%.2f)" % (unter, bez[:42], verm[:38], g))
    # Pruefliste: alles, was nicht zweifelsfrei war
    pfad_pruef = os.path.join(HIER, "uebersicht-pruefen.txt")
    with io.open(pfad_pruef, "w", encoding="utf8") as fp:
        fp.write("Zuordnungen aus den Excel-Uebersichten, die du kurz pruefen solltest.\n")
        fp.write("Diese Schnitte tragen in der Seite den Hinweis 'aus Uebersicht'.\n\n")
        fp.write("--- unsicher zugeordnet: Groesse/Stoff/Bild koennten am falschen Schnitt haengen ---\n")
        unsicher = [x for x in sorted(angenommen, key=lambda x: x[3]) if x[3] < 0.9]
        for unter, bez, tit, g in unsicher:
            fp.write("  %.2f  [%s] %s\n           -> %s\n" % (g, unter, bez, tit))
        fp.write("\n--- gar nicht zugeordnet: im Katalog nicht gefunden ---\n")
        for unter, bez, verm, g in unklar:
            fp.write("  [%s] %s\n" % (unter, bez))

    print("\n%d Zuordnungen sind unsicher, %d Excel-Zeilen blieben offen." %
          (len(unsicher), len(unklar)))
    print("Pruefliste:  %s" % pfad_pruef)
    print("Geschrieben: %s" % UEBERNAHME)


if __name__ == "__main__":
    main()
