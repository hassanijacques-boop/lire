#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rattrapage : lien vers la page de l'œuvre + libellé d'origine conservé."""
import json, re, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/2.7 (pedagogie; hassanijacques@gmail.com)"}
BASE = "/workspace/lire"

def call(p, tries=3):
    p.update({"format": "json", "formatversion": "2"})
    u = API + "?" + urllib.parse.urlencode(p)
    for a in range(tries):
        try:
            time.sleep(1.5 + a * 4)
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception:
            time.sleep(3)
    return {}

FALL = {
 "Les Misérables": "Les Misérables",
 "Le Tour du monde en 80 jours": "Le Tour du monde en quatre-vingts jours",
 "Les Trois Mousquetaires": "Les Trois Mousquetaires",
 "L'Avare": "L’Avare",
 "Candide": "Candide, ou l’Optimisme",
 "Roméo et Juliette": "Roméo et Juliette",
 "Poèmes saturniens": "Poèmes saturniens (1902)",
 "Au Bonheur des Dames": "Au bonheur des dames",
 "Un chant de Noël": "Cantique de Noël",
 "Oliver Twist": "Olivier Twist",
 "Don Quichotte": "L’Ingénieux Hidalgo Don Quichotte de la Manche",
 "Le Dormeur du val": "Le Dormeur du val",
 "Le Corbeau et le Renard": "Fables de La Fontaine (éd. 1874)/Le Corbeau et le Renard",
 "Le Petit Chaperon rouge": "Contes de Perrault (éd. 1902)/Le petit Chaperon rouge",
 "Le Chat botté": "Le Maître chat ou le Chat botté",
 "Vingt Mille Lieues sous les mers": "Vingt mille lieues sous les mers",
 "Notre-Dame de Paris": "Notre-Dame de Paris",
 "Le Comte de Monte-Cristo": "Le Comte de Monte-Cristo",
 "Nouvelles choisies": "Toine (recueil)/Édition Conard, 1910",
}

cands = sorted(set(FALL.values()))
ok = set()
for i in range(0, len(cands), 45):
    r = call({"action": "query", "titles": "|".join(cands[i:i + 45]), "redirects": 1})
    for p in r.get("query", {}).get("pages", []):
        if not p.get("missing"):
            ok.add(p["title"])
print("pages d'œuvre valides :", len(ok), "/", len(cands))
for c in cands:
    if c not in ok:
        print("   ✗", c)

O = json.load(open(f"{BASE}/oeuvres.json"))
old = json.load(open(f"{BASE}/oeuvres_avant_polish.json"))
vieux = {}
for o in old:
    for m in o["moments"]:
        vieux[(o["oeuvre"], m["t"])] = m.get("src", "")

def nettoie(s, x):
    s = re.sub(r"^\d+\.\s*", "", s)
    for n in (40, 30, 25, 20):
        frag = x[:n]
        if len(frag) >= 15 and frag in s:
            s = s.split(frag)[0]
            break
    return s.strip(" ·—-–…").strip()

n = 0
for o in O:
    for m in o["moments"]:
        if m.get("url"):
            continue
        lab = nettoie(vieux.get((o["oeuvre"], m["t"]), ""), m["x"])
        if lab and len(lab) > len(o["oeuvre"]) + 4 and lab.lower() != o["oeuvre"].lower():
            m["src"] = lab
        if o["oeuvre"] in FALL and FALL[o["oeuvre"]] in ok:
            m["url"] = FALL[o["oeuvre"]]
            n += 1
print("liens d'œuvre ajoutés :", n)

json.dump(O, open(f"{BASE}/oeuvres.json", "w"), ensure_ascii=False, indent=1)
tpl = open(f"{BASE}/template2.html", encoding="utf-8").read()
open(f"{BASE}/index.html", "w", encoding="utf-8").write(
    tpl.replace("__OEUVRES__", json.dumps(O, ensure_ascii=False, separators=(",", ":"))))
print("total liens :", sum(1 for o in O for m in o["moments"] if m.get("url")), "/",
      sum(len(o["moments"]) for o in O))
