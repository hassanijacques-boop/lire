#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sources : libellé lisible (m.src) + lien vérifié facultatif (m.url)."""
import json, re, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/2.5 (pedagogie; hassanijacques@gmail.com)"}
BASE = "/workspace/lire"

def call(p, tries=4):
    p.update({"format": "json", "formatversion": "2"})
    u = API + "?" + urllib.parse.urlencode(p)
    for a in range(tries):
        try:
            time.sleep(1.8 + a * 5)
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=35) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                continue
            return {}
        except Exception:
            time.sleep(4)
    return {}

O = json.load(open(f"{BASE}/oeuvres.json"))
ROM = [("Miss Harriet", "Miss Harriet (1884)"), ("Mademoiselle Fifi", "Mademoiselle Fifi (1882)"),
       ("Contes de la bécasse", "Contes de la bécasse (1883)"), ("Toine (recueil", "Toine (1885)"),
       ("Le Horla (recueil", "Le Horla (1887)"), ("Les Sœurs Rondoli", "Les Sœurs Rondoli (1884)"),
       ("Contes du jour et de la nuit", "Contes du jour et de la nuit (1885)"),
       ("Boule de suif", "Boule de suif (1880)"), ("La Maison Tellier", "La Maison Tellier (1881)"),
       ("Clair de lune", "Clair de lune (1883)")]

# corrections de titres de pages
REPL = {"Clair de lune (recueil, 1884)/La Légende du Mont Saint-Michel":
        "Clair de lune (recueil, 1884)/La Légende du mont Saint-Michel",
        "Clair de lune (recueil, 1884)/Moiron": "Clair de lune (recueil, 1905)/Moiron",
        "Clair de lune (recueil, 1884)/La Nuit (cauchemar)": "Clair de lune (recueil, 1905)/La Nuit",
        "Contes de la bécasse/Un Fils": "Contes de la bécasse/Un fils"}

def libelle(o, m):
    nom, url, t = o["oeuvre"], m.get("src", ""), m["t"]
    if nom == "Nouvelles choisies":
        for k, v in ROM:
            if url.startswith(k):
                return v
        return "Wikisource"
    if nom == "Germinal":
        r = re.search(r"Partie (\w+)/(\w+) (\d+)", url)
        if r:
            chiffres = {"I": "I", "II": "II", "III": "III", "IV": "IV", "V": "V", "VI": "VI", "VII": "VII"}
            return f"Germinal, partie {r.group(1)}, chapitre {r.group(3)}"
    if nom == "Les Aventures de Tom Sawyer":
        return f"Tom Sawyer, chapitre {url.split('/')[-1]}"
    if nom == "Croc-Blanc":
        return f"Croc-Blanc, chapitre {url.split(' ')[-1]}"
    if nom == "Alice au pays des merveilles":
        return f"Alice au pays des merveilles, chapitre {url.split('/')[-1]}"
    if nom == "David Copperfield":
        return f"David Copperfield, chapitre {url.split(' ')[-1]}"
    if nom in ("Le Livre de la jungle", "Les Aventures de Sherlock Holmes"):
        return f"{nom} — {t}" if t.startswith("«") else f"{nom} — « {t} »"
    if nom in ("Contes de la bécasse", "Clair de lune"):
        return f"{nom} (recueil) — « {t} »"
    return m.get("src", "")

for o in O:
    for m in o["moments"]:
        u = REPL.get(m.get("src", ""), m.get("src", ""))
        m["url"] = u
        m["src"] = libelle(o, {"src": u, "t": m["t"]})
        if not m["src"]:
            m["src"] = "Wikisource"

# vérification
toutes = sorted({m["url"] for o in O for m in o["moments"] if m.get("url")})
ok = set()
for i in range(0, len(toutes), 45):
    lot = toutes[i:i + 45]
    r = call({"action": "query", "titles": "|".join(lot), "redirects": 1})
    for p in r.get("query", {}).get("pages", []):
        if not p.get("missing"):
            ok.add(p["title"])
            if p.get("redirects"):
                pass
print("URL vérifiées :", len(ok), "/", len(toutes))
ko = [u for u in toutes if u not in ok]
for u in ko:
    print("   ✗", u)
for o in O:
    for m in o["moments"]:
        if m.get("url") and m["url"] not in ok:
            m["url"] = ""

json.dump(O, open(f"{BASE}/oeuvres.json", "w"), ensure_ascii=False, indent=1)
print("Total liens conservés :", sum(1 for o in O for m in o["moments"] if m.get("url")))
print("Moments sans lien :", sum(1 for o in O for m in o["moments"] if not m.get("url")))

# rendu HTML
tpl = open(f"{BASE}/template2.html", encoding="utf-8").read()
open(f"{BASE}/index.html", "w", encoding="utf-8").write(
    tpl.replace("__OEUVRES__", json.dumps(O, ensure_ascii=False, separators=(",", ":"))))
print("index.html régénéré :", len(O), "œuvres")
