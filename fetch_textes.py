#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Récupère des textes du domaine public sur Wikisource FR (texte réel, jamais reconstitué)."""
import json, re, html, urllib.parse, urllib.request, time

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/1.0 (outil pedagogique)"}

import random
def api(params):
    params["format"] = "json"; params["formatversion"] = "2"
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            time.sleep(2.0 if attempt == 0 else 8.0 + attempt * 4)
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("   429, pause...", flush=True); continue
            raise
    return {}

def search(q, limit=6):
    d = api({"action":"query","list":"search","srsearch":q,"srlimit":limit})
    return [x["title"] for x in d.get("query",{}).get("search",[])]

def page_text(title):
    try:
        d = api({"action":"parse","page":title,"prop":"text","redirects":1})
        h = d["parse"]["text"]
    except Exception:
        return ""
    h = re.sub(r'<style.*?</style>', ' ', h, flags=re.S)
    h = re.sub(r'<table.*?</table>', ' ', h, flags=re.S)
    h = re.sub(r'<sup.*?</sup>', ' ', h, flags=re.S)
    h = re.sub(r'<div class="ws-noexport.*?</div>', ' ', h, flags=re.S)
    h = re.sub(r'<(p|div|br|li|h\d)[^>]*>', '\n', h)
    h = re.sub(r'<[^>]+>', '', h)
    t = html.unescape(h)
    t = re.sub(r'[ \t\u00a0]+', ' ', t)
    lines = []
    for l in t.split("\n"):
        l = l.strip()
        if not l: continue
        if re.match(r'^(\d+|Page|Chapitre \d+)$', l): continue
        if len(l) < 2: continue
        lines.append(l)
    return "\n".join(lines)

# (titre de recherche, auteur, oeuvre, genre, niveau conseillé)
WANTED = [
 ("Le Corbeau et le renard La Fontaine", "Jean de La Fontaine", "Fables", "Poésie", "CE1"),
 ("La Cigale et la fourmi La Fontaine", "Jean de La Fontaine", "Fables", "Poésie", "CP"),
 ("Le Loup et l'Agneau La Fontaine", "Jean de La Fontaine", "Fables", "Poésie", "CE2"),
 ("Les Misérables Victor Hugo Fantine Cosette", "Victor Hugo", "Les Misérables", "Roman", "CM2"),
 ("Les Contemplations Victor Hugo Demain dès l'aube", "Victor Hugo", "Les Contemplations", "Poésie", "CM1"),
 ("Le Petit Chaperon rouge Perrault", "Charles Perrault", "Contes", "Conte", "CP"),
 ("La Barbe bleue Perrault", "Charles Perrault", "Contes", "Conte", "CM1"),
 ("Les Trois Mousquetaires Dumas chapitre", "Alexandre Dumas", "Les Trois Mousquetaires", "Roman", "CM2"),
 ("Vingt mille lieues sous les mers Verne chapitre", "Jules Verne", "Vingt mille lieues sous les mers", "Roman", "CM2"),
 ("Roméo et Juliette Shakespeare acte", "William Shakespeare", "Roméo et Juliette", "Théâtre", "CM2"),
 ("Hamlet Shakespeare acte", "William Shakespeare", "Hamlet", "Théâtre", "CM2"),
 ("L'Odyssée Homère chant", "Homère", "L'Odyssée", "Épopée", "CM1"),
 ("Le Malade imaginaire Molière acte", "Molière", "Le Malade imaginaire", "Théâtre", "CM1"),
 ("Cyrano de Bergerac Rostand tirade", "Edmond Rostand", "Cyrano de Bergerac", "Théâtre", "CM2"),
 ("Chanson d'automne Verlaine", "Paul Verlaine", "Poèmes saturniens", "Poésie", "CE2"),
 ("Le Dormeur du val Rimbaud", "Arthur Rimbaud", "Poésies", "Poésie", "CM2"),
 ("Candide Voltaire chapitre", "Voltaire", "Candide", "Conte philosophique", "CM2"),
 ("Alice au pays des merveilles Carroll", "Lewis Carroll", "Alice au pays des merveilles", "Roman", "CM1"),
]

out = []
for q, auteur, oeuvre, genre, niv in WANTED:
    found = None
    for title in search(q):
        t = page_text(title)
        words = len(t.split())
        if words >= 220 and "homonymie" not in t[:200].lower():
            found = (title, t, words); break
        time.sleep(1.5)
    if not found:
        print("ECHEC", q); continue
    title, text, words = found
    # coupe propre à ~450 mots, sur une fin de phrase
    parts = re.split(r'(?<=[.!?»])\s+', text)
    acc, n = [], 0
    for p in parts:
        acc.append(p); n += len(p.split())
        if n >= 420: break
    body = " ".join(acc)
    out.append({"auteur":auteur, "oeuvre":oeuvre, "genre":genre, "niveau":niv,
                "source":title, "texte":body, "mots":len(body.split())})
    json.dump(out, open("/workspace/lire/textes.json","w"), ensure_ascii=False, indent=1)
    print(f"OK  {auteur:22s} {oeuvre[:32]:32s} {len(body.split()):4d} mots  <- {title[:40]}")

json.dump(out, open("/workspace/lire/textes.json","w"), ensure_ascii=False, indent=1)
print("\nTOTAL", len(out), "textes")
