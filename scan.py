# -*- coding: utf-8 -*-
"""
Scannt den Schnittmuster-Ordner und baut daraus einen Katalog.
Liest NUR Datei- und Ordnernamen sowie Groessen - keine Dateiinhalte.
Jederzeit erneut ausfuehrbar. Deine Handeingaben liegen im Browserspeicher und
haengen an der id (abgeleitet vom Ablageort) - sie ueberleben einen neuen Scan,
solange du den Schnitt nicht verschiebst oder umbenennst.
"""
import os, re, json, sys, hashlib, unicodedata

BASIS = r"C:\Users\LSchneider\OneDrive\DIY\Schnittmuster"
AUSGABE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daten.js")

DOK = {".pdf", ".dxf", ".svg", ".ai", ".docx", ".txt", ".xlsx"}
BILD = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
VIDEO = {".mp4", ".mov"}
IGNORE_DATEI = {"desktop.ini", "thumbs.db", ".ds_store"}

# ---------------------------------------------------------------- Kategorien
KATEGORIE_NAMEN = {
    "_damen": "Damen", "_herren": "Herren", "_kinder": "Kinder",
    "_babys": "Babys", "_taschen": "Taschen", "_sonstiges": "Sonstiges",
    "neu unsortiert": "Unsortiert",
}
# Ordner, die nie ein Schnitt sind
KEIN_SCHNITT = {"_übersicht", "_ergebnisse"}

# ---------------------------------------------------------------- Merkmale
# Jede Regel: (Merkmalswert, [Suchbegriffe])
AERMEL = [
    ("Puffärmel",      ["puffärmel", "puffarmel", "puff sleeve", "puffed sleeve", "puff-sleeve", "bishop"]),
    ("Ballonärmel",    ["ballonärmel", "ballonarmel", "balloon sleeve"]),
    ("Raglanärmel",    ["raglan"]),
    ("Fledermausärmel",["fledermaus", "batwing", "dolman"]),
    ("Volantärmel",    ["volantärmel", "flutter sleeve", "angel sleeve", "flügelärmel", "ruffle sleeve"]),
    ("Kimono/angeschnitten", ["kimono", "angeschnitten", "drop shoulder", "drop-shoulder", "dropshoulder"]),
    ("Trompetenärmel", ["trompetenärmel", "trumpet sleeve"]),
    ("Ärmellos",       ["ärmellos", "aermellos", "sleeveless", "tank top", "trägertop", "spaghetti"]),
    ("Langarm",        ["langarm", "long sleeve", "longsleeve"]),
    ("Kurzarm",        ["kurzarm", "short sleeve"]),
    ("3/4-Arm",        ["3/4-arm", "dreiviertelarm", "3/4 arm"]),
]
AUSSCHNITT = [
    ("V-Ausschnitt",   ["v-ausschnitt", "v-neck", "vneck", "v ausschnitt"]),
    ("Rundhals",       ["rundhals", "crew neck", "crewneck", "round neck"]),
    ("Karree",         ["karree", "square neck"]),
    ("Wasserfall",     ["wasserfall", "cowl"]),
    ("Rollkragen",     ["rollkragen", "turtleneck", "turtle neck"]),
    ("Herzausschnitt", ["herzausschnitt", "sweetheart"]),
    ("U-Boot",         ["u-boot", "boat neck", "carmen", "off shoulder", "off-shoulder"]),
    ("Kapuze",         ["kapuze", "hoodie", "hood", "hoody"]),
]
PASSFORM = [
    ("Oversize",       ["oversize", "oversized", "loose fit", "boxy"]),
    ("Tailliert",      ["tailliert", "fitted", "figurbetont"]),
    ("Antifit",        ["antifit", "anti-fit"]),
    ("Weit/A-Linie",   ["a-linie", "a-line", "swing", "trapez"]),
    ("Mitwachsend",    ["mitwachs", "mitwachsend"]),
]
DETAILS = [
    ("Raffung",        ["raffung", "gerafft", "ruched", "ruching", "smok"]),
    ("Twist/Knoten",   ["twist", "knot", "knoten"]),
    ("Wickeloptik",    ["wickel", "wrap"]),
    ("Volants",        ["volant", "rüschen", "ruffle", "flounce"]),
    ("Knopfleiste",    ["knopfleiste", "button", "knöpfe"]),
    ("Reißverschluss", ["reißverschluss", "reisverschluss", "zipper", "zip"]),
    ("Taschen",        ["taschen", "pockets", "eingriffstasche"]),
    ("Tunnelzug",      ["tunnelzug", "drawstring", "kordelzug"]),
    ("Bündchen",       ["bündchen", "buendchen", "cuff"]),
    ("Gefüttert",      ["gefüttert", "gefuettert", "lined", "futter"]),
    ("Colourblocking", ["colorblock", "colourblock", "color blocking", "blocked"]),
    ("Rückenausschnitt", ["rückenausschnitt", "open back", "back detail"]),
]
TEILART = [
    ("T-Shirt",   ["t-shirt", "tshirt", "shirt", " tee", "tee ", "basicshirt"]),
    ("Top",       ["top", "tanktop", "camisole"]),
    ("Bluse",     ["bluse", "blouse", "blusenshirt"]),
    ("Pullover",  ["pulli", "pullover", "sweater", "sweatshirt", "hoodie", "hoody"]),
    ("Kleid",     ["kleid", "dress", "robe"]),
    ("Rock",      ["rock ", "skirt", "röckchen"]),
    ("Hose",      ["hose", "pants", "trousers", "leggings", "jeans", "shorts", "buxe"]),
    ("Jacke",     ["jacke", "jacket", "blouson", "mantel", "coat", "weste", "cardigan", "poncho", "cape"]),
    ("Overall",   ["overall", "jumpsuit", "romper", "anzug", "strampler"]),
    ("Body",      ["body", "bodysuit"]),
    ("Unterwäsche", ["unterwäsche", "dessous", "slip", "bh ", "boxershorts", "panty"]),
    ("Bademode",  ["badeanzug", "bikini", "badehose", "swimsuit", "bademantel", "badeponcho"]),
    ("Tasche",    ["tasche", "bag", "rucksack", "beutel", "clutch", "geldbeutel", "börse", "utensilo"]),
    ("Mütze/Accessoire", ["mütze", "muetze", "beanie", "haarband", "stirnband", "schal", "loop", "handschuh", "socken"]),
    ("Kuscheltier", ["kuscheltier", "bär", "hase", "eule", "kissen", "decke", "schlafsack"]),
]
STOFF = [
    ("Jersey",    ["jersey"]),
    ("Sweat",     ["sweat", "french terry"]),
    ("Walk",      ["walk"]),
    ("Musselin",  ["musselin", "musling", "double gauze"]),
    ("Leinen",    ["leinen", "linen"]),
    ("Webware",   ["webware", "canvas", "popeline", "baumwollstoff"]),
    ("Softshell", ["softshell"]),
    ("Fleece",    ["fleece", "frottee", "plüsch", "teddy"]),
    ("Viskose",   ["viskose", "viscose"]),
]
FORMAT = [
    ("A0",        ["a0", "a-0", "plotdatei", "copyshop"]),
    ("A4",        ["a4", "din a4", "din-a4"]),
    ("Beamer",    ["beamer", "projector"]),
    ("Ebenen",    ["ebenen", "layer"]),
    ("Plotter/DXF", [".dxf"]),
]

# Bekannte Label / Designer
DESIGNER = [
    "Lybstes", "heidimade", "leni pepunkt", "pepunkt", "Anninanni", "PiexSu",
    "Schnittenliebe", "Malomi", "Hansedelli", "Snaply", "mioumiou", "Lilikidz",
    "made by oranges", "nahttuerlich handgemacht", "Bernina", "Westfalenstoffe",
    "Initiative Handarbeit", "DIYeule", "Firlefanz", "Fadenkäfer", "Klimperklein",
    "Erbsenprinzessin", "Pattydoo", "Farbenmix", "Ottobre", "Burda", "Simplicity",
    "Tiana's Closet", "Stoffe.de", "Makerist", "Milchmonster", "Kid5", "Zierstoff",
    "Rosarosa", "Nähfrosch", "Kreativlabor", "Mamahoch2", "Schnabelina",
]

FREEBOOK = ["freebook", "free book", "free-book", "free pdf", "kostenlos", "gratis", "free sewing"]


def umlaute_reparieren(s):
    """Repariert Dateinamen wie 'FrÃ¼hlingsluft' -> 'Frühlingsluft'.

    Entsteht, wenn ein UTF-8-Name irgendwo als Latin-1 gelesen wurde - typisch
    bei Dateien aus Online-Shops.

    Zuerst NFC: manche Namen liegen zerlegt vor (A + kombinierende Tilde statt
    'Ã'), etwa wenn sie ueber einen Mac gelaufen sind. Ohne diesen Schritt
    erkennt die Pruefung unten das Problem gar nicht.
    """
    s = unicodedata.normalize("NFC", s)
    if "Ã" not in s and "Â" not in s:
        return s
    try:
        repariert = s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s
    return repariert if "Ã" not in repariert else s


def norm(s):
    """Vergleichsform: klein, Umlaute erhalten, Trenner zu Leerzeichen."""
    s = umlaute_reparieren(s).lower()
    s = s.replace("_", " ").replace("-", " ").replace(".", " ")
    s = re.sub(r"\s+", " ", s)
    return " " + s + " "


def treffer(regeln, text):
    out = []
    for wert, begriffe in regeln:
        for b in begriffe:
            if b in text:
                out.append(wert)
                break
    return out


def groessen_aus_text(text):
    """Erkennt Groessenangaben wie 'Gr. 34-50', '32-56', '50-104', 'XS-XXXL', '3-18 Monate'."""
    text = text.lower()
    funde = []
    # Zahlenbereiche: "34-50", "gr 34 bis 50", "Gr. 92 - 146", "50_104"
    for m in re.finditer(r"(\d{2,3})\s*(?:-|–|_|bis|to|\s)\s*(\d{2,3})", text):
        a, b = int(m.group(1)), int(m.group(2))
        if not b > a:
            continue
        if 28 <= a <= 62 and 30 <= b <= 68:          # Konfektion Erwachsene
            funde.append((b - a, "%d-%d" % (a, b)))
        elif 44 <= a <= 170 and 50 <= b <= 176:      # Kindergroessen in cm
            funde.append((b - a, "%d-%d" % (a, b)))
    # Buchstabengroessen
    m = re.search(r"\b(xxs|xs|s|m|l|xl|xxl)\s*[-–]\s*(xs|s|m|l|xl|xxl|xxxl|4xl|5xl)\b", text)
    if m:
        funde.append((99, m.group(0).upper()))
    # Monatsangaben
    m = re.search(r"\b(\d{1,2})\s*[-–]\s*(\d{1,2})\s*(monate|months)\b", text)
    if m:
        funde.append((98, "%s-%s Monate" % (m.group(1), m.group(2))))
    if not funde:
        return None
    # groesster abgedeckter Bereich gewinnt
    return max(funde)[1]


def designer_aus_text(roh):
    low = roh.lower()
    for d in DESIGNER:
        if d.lower() in low:
            return d
    m = re.search(r"\bby\s+([A-Za-zÄÖÜäöüß0-9'&. ]{3,25})", roh)
    if m:
        return m.group(1).strip(" .-_")
    return ""


def sammle_dateien(pfad):
    """Alle Dateien unterhalb von pfad, rekursiv."""
    res = []
    for wurzel, dirs, files in os.walk(pfad):
        dirs[:] = [d for d in dirs if d.lower() not in KEIN_SCHNITT]
        for f in files:
            if f.lower() in IGNORE_DATEI:
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext not in DOK and ext not in BILD and ext not in VIDEO:
                continue
            voll = os.path.join(wurzel, f)
            try:
                groesse = os.path.getsize(voll)
            except OSError:
                groesse = 0
            res.append({"name": f, "pfad": voll, "ext": ext, "groesse": groesse})
    return res


def ist_kategorie(pfad):
    """Ordner mit mehreren Unterordnern und kaum eigenen Dateien = Kategorie, kein Schnitt."""
    try:
        eintraege = os.listdir(pfad)
    except OSError:
        return False
    unter = [e for e in eintraege if os.path.isdir(os.path.join(pfad, e))]
    dateien = [e for e in eintraege
               if not os.path.isdir(os.path.join(pfad, e))
               and os.path.splitext(e)[1].lower() in DOK]
    return len(unter) >= 3 and len(unter) >= len(dateien)


def mach_id(relpfad):
    return hashlib.md5(relpfad.encode("utf8")).hexdigest()[:10]


def baue_eintrag(anzeige_name, quelle_pfad, kategorie, unterkategorie, dateien):
    rel = os.path.relpath(quelle_pfad, BASIS)
    rohtext = anzeige_name + " " + " ".join(d["name"] for d in dateien) + " " + unterkategorie
    such = norm(rohtext)

    pdfs   = [d for d in dateien if d["ext"] == ".pdf"]
    bilder = [d for d in dateien if d["ext"] in BILD]

    formate = treffer(FORMAT, such)
    if any(d["ext"] == ".dxf" for d in dateien):
        formate.append("Plotter/DXF")

    titel = re.sub(r"\.(pdf|docx|xlsx)$", "", anzeige_name, flags=re.I)
    titel = umlaute_reparieren(titel)
    titel = titel.replace("_", " ")
    # Bindestriche nur trennen, wenn sie als Worttrenner dienen (nicht in "(Jogging-)Hose")
    titel = re.sub(r"(?<=[a-zäöüß0-9])-(?=[a-zA-ZÄÖÜäöü0-9]{3,})", " ", titel)
    # Shop-Kürzel am Ende wie "-5ebzao", "-88qt2q" entfernen
    titel = re.sub(r"[- ][a-z0-9]{6}$", "", titel)
    titel = re.sub(r"\s+", " ", titel).strip(" -")

    return {
        "id": mach_id(rel),
        "titel": titel,
        "kategorie": kategorie,
        "unterkategorie": unterkategorie,
        "pfad": rel.replace("\\", "/"),
        "istOrdner": os.path.isdir(quelle_pfad),
        # --- automatisch erkannt ---
        "teilart": treffer(TEILART, such)[:2],
        "aermel": treffer(AERMEL, such),
        "ausschnitt": treffer(AUSSCHNITT, such),
        "passform": treffer(PASSFORM, such),
        "details": treffer(DETAILS, such),
        "stoff": treffer(STOFF, such),
        "format": sorted(set(formate)),
        "groessen": groessen_aus_text(rohtext) or "",
        "designer": designer_aus_text(anzeige_name + " " + " ".join(d["name"] for d in dateien)),
        "freebook": any(f in such for f in FREEBOOK),
        "anzahlPdf": len(pdfs),
        "bilder": [os.path.relpath(b["pfad"], BASIS).replace("\\", "/") for b in bilder[:4]],
        "mb": round(sum(d["groesse"] for d in dateien) / 1048576, 1),
        # --- von Hand zu pflegen ---
        "genaeht": False,
        "anzahlGenaeht": 0,
        "meineGroesse": "",
        "anpassungen": "",
        "bewertung": 0,
        "schwierigkeit": "",
        "stoffverbrauch": "",
        "kurzwaren": "",
        "gekauftBei": "",
        "gekauftAm": "",
        "preis": "",
        "shopLink": "",
        "papierbogen": "",
        "notizen": "",
        "meineFotos": [],
    }


def scanne():
    eintraege = []
    for top in sorted(os.listdir(BASIS)):
        tpfad = os.path.join(BASIS, top)
        tl = top.lower()
        if tl in KEIN_SCHNITT:
            continue

        if os.path.isfile(tpfad):
            if os.path.splitext(top)[1].lower() in DOK:
                eintraege.append(baue_eintrag(
                    top, tpfad, "Sonstiges", "",
                    [{"name": top, "pfad": tpfad, "ext": os.path.splitext(top)[1].lower(),
                      "groesse": os.path.getsize(tpfad)}]))
            continue

        kategorie = KATEGORIE_NAMEN.get(tl, top.lstrip("_"))

        for zweit in sorted(os.listdir(tpfad)):
            zpfad = os.path.join(tpfad, zweit)
            if zweit.lower() in IGNORE_DATEI or zweit.lower() in KEIN_SCHNITT:
                continue

            if os.path.isfile(zpfad):
                ext = os.path.splitext(zweit)[1].lower()
                if ext not in DOK:
                    continue
                eintraege.append(baue_eintrag(
                    zweit, zpfad, kategorie, "",
                    [{"name": zweit, "pfad": zpfad, "ext": ext, "groesse": os.path.getsize(zpfad)}]))
                continue

            # Ordner: Kategorie oder Schnitt?
            if ist_kategorie(zpfad):
                unter = zweit.lstrip("_")
                for dritt in sorted(os.listdir(zpfad)):
                    dpfad = os.path.join(zpfad, dritt)
                    if dritt.lower() in IGNORE_DATEI:
                        continue
                    if os.path.isfile(dpfad):
                        ext = os.path.splitext(dritt)[1].lower()
                        if ext not in DOK:
                            continue
                        eintraege.append(baue_eintrag(
                            dritt, dpfad, kategorie, unter,
                            [{"name": dritt, "pfad": dpfad, "ext": ext,
                              "groesse": os.path.getsize(dpfad)}]))
                    else:
                        dateien = sammle_dateien(dpfad)
                        if dateien:
                            eintraege.append(baue_eintrag(dritt, dpfad, kategorie, unter, dateien))
            else:
                dateien = sammle_dateien(zpfad)
                if dateien:
                    eintraege.append(baue_eintrag(zweit, zpfad, kategorie, "", dateien))

    return eintraege


def main():
    if not os.path.isdir(BASIS):
        print("Basisordner nicht gefunden:", BASIS); sys.exit(1)

    neu = scanne()

    # Handeingaben liegen im Browserspeicher und haengen an der id (= Ablageort).
    # Hier wird nur verglichen, was sich seit dem letzten Lauf geaendert hat.
    alt_ids = set()
    if os.path.exists(AUSGABE):
        try:
            with open(AUSGABE, encoding="utf8") as f:
                roh = f.read()
            alt_ids = {e["id"] for e in json.loads(roh[roh.index("["):roh.rindex("]") + 1])}
        except Exception as ex:
            print("Hinweis: bisherige daten.js nicht lesbar (%s)." % ex)

    neu_ids = {e["id"] for e in neu}
    dazu = neu_ids - alt_ids
    weg = alt_ids - neu_ids

    # Handeingaben, die keinem Schnitt mehr zugeordnet werden koennen
    verwaist = 0
    sicherung = os.path.join(os.path.dirname(AUSGABE), "schnittmuster-pflegedaten.json")
    if os.path.exists(sicherung):
        try:
            with open(sicherung, encoding="utf8") as f:
                verwaist = len([k for k in json.load(f) if k not in neu_ids])
        except Exception:
            pass

    with open(AUSGABE, "w", encoding="utf8") as f:
        f.write("// Automatisch erzeugt von scan.py - Handeingaben bleiben bei erneutem Scan erhalten.\n")
        f.write("window.SCHNITTE = ")
        json.dump(neu, f, ensure_ascii=False, indent=1)
        f.write(";\n")

    # Bericht
    print("Schnitte gesamt: %d" % len(neu))
    if alt_ids:
        print("Neu hinzugekommen: %d   Nicht mehr gefunden: %d" % (len(dazu), len(weg)))
    if verwaist:
        print("ACHTUNG: %d gepflegte Eintraege passen zu keinem Schnitt mehr." % verwaist)
        print("         Vermutlich hast du Ordner verschoben oder umbenannt.")
    print("\nNach Kategorie:")
    kat = {}
    for e in neu:
        kat[e["kategorie"]] = kat.get(e["kategorie"], 0) + 1
    for k, v in sorted(kat.items(), key=lambda x: -x[1]):
        print("  %-14s %4d" % (k, v))

    def quote(feld):
        n = sum(1 for e in neu if e[feld])
        return "%d (%d%%)" % (n, round(100 * n / len(neu)))

    print("\nAutomatisch erkannt:")
    for f in ["teilart", "aermel", "ausschnitt", "passform", "details", "stoff",
              "format", "groessen", "designer", "bilder"]:
        print("  %-12s %s" % (f, quote(f)))
    print("  freebook     %d" % sum(1 for e in neu if e["freebook"]))
    print("  Gesamtgroesse: %.1f GB" % (sum(e["mb"] for e in neu) / 1024))
    print("\nGeschrieben nach: %s" % AUSGABE)


if __name__ == "__main__":
    main()
