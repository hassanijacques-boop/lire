#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dernière passe : liens exacts, poèmes remis en vers, titres manquants."""
import json, re, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/2.8 (pedagogie; hassanijacques@gmail.com)"}
BASE = "/workspace/lire"

def existe(t):
    p = {"action": "query", "titles": t, "redirects": "1", "format": "json", "formatversion": "2"}
    u = API + "?" + urllib.parse.urlencode(p)
    for a in range(3):
        try:
            time.sleep(1.2 + a * 3)
            r = json.load(urllib.request.urlopen(
                urllib.request.Request(u, headers=UA), timeout=30))
            pg = r.get("query", {}).get("pages", [{}])[0]
            return not pg.get("missing") and not pg.get("invalid")
        except Exception:
            time.sleep(3)
    return False

O = json.load(open(f"{BASE}/oeuvres.json"))
d = {o["oeuvre"]: o for o in O}

NOUV = {
 "Le Papa de Simon": "La Maison Tellier (recueil, Ollendorff 1891)/Le Papa de Simon",
 "Pierrot": "Contes de la bécasse/Pierrot",
 "La Ficelle": "Miss Harriet (recueil)/Édition Conard, 1910/La Ficelle",
 "Mon oncle Jules": "Miss Harriet (recueil)/Édition Conard, 1910/Mon oncle Jules",
 "Aux champs": "Contes de la bécasse/Aux champs",
 "Deux amis": "Mademoiselle Fifi (recueil, Ollendorff 1898)/Deux amis",
 "La Rempailleuse": "Contes de la bécasse/La Rempailleuse",
 "Le Petit Fût": "Les Sœurs Rondoli (recueil, Ollendorff 1904)/Le Petit Fût",
 "Toine": "Toine (recueil)/Édition Conard, 1910",
 "La Parure": "Contes du jour et de la nuit (éd. Flammarion, 1885)/La Parure",
 "Boule de Suif": "Boule de suif (recueil)/Boule de Suif",
 "Le Horla": "Le Horla (recueil, Ollendorff 1895)/Le Horla",
}
ROM = [("Miss Harriet", "Miss Harriet (1884)"), ("Mademoiselle Fifi", "Mademoiselle Fifi (1882)"),
       ("Contes de la bécasse", "Contes de la bécasse (1883)"), ("Toine (recueil", "Toine (1885)"),
       ("Le Horla (recueil", "Le Horla (1887)"), ("Les Sœurs Rondoli", "Les Sœurs Rondoli (1884)"),
       ("Contes du jour et de la nuit", "Contes du jour et de la nuit (1885)"),
       ("Boule de suif", "Boule de suif (1880)"), ("La Maison Tellier", "La Maison Tellier (1881)")]

for m in d["Nouvelles choisies"]["moments"]:
    u = NOUV.get(m["t"], "")
    m["url"] = u
    for k, v in ROM:
        if u.startswith(k):
            m["src"] = v
            break

for m in d["Contes de la bécasse"]["moments"]:
    m["url"] = "Contes de la bécasse/" + m["t"].replace("'", "’")
    m["src"] = f"Contes de la bécasse (recueil) — « {m['t']} »"
for m in d["Clair de lune"]["moments"]:
    base = "Clair de lune (recueil, 1905)/" if m["t"] in ("Moiron", "La Nuit (cauchemar)") \
        else "Clair de lune (recueil, 1884)/"
    m["url"] = base + m["t"]
    m["src"] = f"Clair de lune (recueil) — « {m['t']} »"

# poèmes : titres + retour à la ligne des vers
POEMES = {"Trois ans après": "Trois ans après",
          "Quand nous habitions tous ensemble": "Quand nous habitions tous ensemble",
          "": "À qui donc sommes-nous ?",
          "Pendant que le marin": "Pendant que le marin",
          "À Villequier Maintenant que Paris, ses pavés et": "À Villequier",
          "Charles Vacquerie": "Charles Vacquerie",
          "À quoi songeaient les deux cavaliers dans la forêt": "À quoi songeaient les deux cavaliers"}
VERS = ("Les Contemplations · Pauca meae", "Poèmes saturniens", "Le Dormeur du val",
        "Le Corbeau et le Renard")
def en_vers(x):
    x = re.sub(r"([;:!?])(?=[A-ZÉÈÀÂÎÔÛÇ«])", r"\1\n", x)
    x = re.sub(r"(\.)(?=[A-ZÉÈÀÂÎÔÛÇ«])", r".\n", x)
    return x

for nom in VERS:
    if nom not in d:
        continue
    for m in d[nom]["moments"]:
        m["t"] = POEMES.get(m["t"], m["t"])
        m["x"] = en_vers(m["x"])
        if nom == "Les Contemplations · Pauca meae":
            m["url"] = "Les Contemplations"
            m["src"] = f"Les Contemplations — « {m['t']} »"

# validation individuelle
vus, garde = {}, 0
for o in O:
    for m in o["moments"]:
        u = m.get("url", "")
        if not u:
            continue
        if u not in vus:
            vus[u] = existe(u)
            if not vus[u]:
                print("   ✗", u[:95])
        if not vus[u]:
            m["url"] = ""

json.dump(O, open(f"{BASE}/oeuvres.json", "w"), ensure_ascii=False, indent=1)
tpl = open(f"{BASE}/template2.html", encoding="utf-8").read()
open(f"{BASE}/index.html", "w", encoding="utf-8").write(
    tpl.replace("__OEUVRES__", json.dumps(O, ensure_ascii=False, separators=(",", ":"))))
tot = sum(len(o["moments"]) for o in O)
liens = sum(1 for o in O for m in o["moments"] if m.get("url"))
print(f"\n{len(O)} œuvres · {tot} moments · {liens} liens Wikisource")
