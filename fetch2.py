#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extraction propre : uniquement les <p> littéraires, sur des pages de chapitre."""
import json, re, html, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/1.1 (outil pedagogique; contact: hassanijacques@gmail.com)"}

def api(params):
    params.update({"format":"json","formatversion":"2"})
    url = API + "?" + urllib.parse.urlencode(params)
    for a in range(4):
        try:
            time.sleep(2.5 + a*6)
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429: continue
            return {}
    return {}

def search(q, n=8):
    d = api({"action":"query","list":"search","srsearch":q,"srlimit":n})
    return [x["title"] for x in d.get("query",{}).get("search",[])]

def paragraphs(title):
    d = api({"action":"parse","page":title,"prop":"text","redirects":1})
    if "parse" not in d: return []
    h = d["parse"]["text"]
    h = re.sub(r'<sup.*?</sup>', ' ', h, flags=re.S)
    h = re.sub(r'<table.*?</table>', ' ', h, flags=re.S)
    h = re.sub(r'<style.*?</style>', ' ', h, flags=re.S)
    ps = re.findall(r'<p[^>]*>(.*?)</p>', h, re.S)
    out = []
    for p in ps:
        t = re.sub(r'<[^>]+>', '', p)
        t = html.unescape(t).replace("\u00a0", " ").replace("ſ", "s")
        t = re.sub(r'\s+', ' ', t).strip()
        if len(t) < 90: continue
        if any(k in t.lower() for k in ("wikisource","licence","domaine public","catégorie","modifier","éditeur","imprimerie","texte établi")):
            continue
        out.append(t)
    return out

CIBLES = [
 ("Les Misérables Tome I chapitre Cosette", "Victor Hugo", "Les Misérables", "Roman", "CM2"),
 ("Le tour du monde en quatre-vingts jours chapitre", "Jules Verne", "Le Tour du monde en 80 jours", "Roman", "CM1"),
 ("Les Trois Mousquetaires chapitre", "Alexandre Dumas", "Les Trois Mousquetaires", "Roman", "CM2"),
 ("Roméo et Juliette acte scène Hugo", "William Shakespeare", "Roméo et Juliette", "Théâtre", "CM2"),
 ("L'Avare acte scène Molière", "Molière", "L'Avare", "Théâtre", "CM1"),
 ("Candide chapitre Voltaire", "Voltaire", "Candide", "Conte", "CM2"),
 ("Alice au pays des merveilles chapitre", "Lewis Carroll", "Alice au pays des merveilles", "Roman", "CM1"),
 ("L'Odyssée chant", "Homère", "L'Odyssée", "Épopée", "CM1"),
 ("Contes Perrault Le petit chaperon rouge", "Charles Perrault", "Contes", "Conte", "CP"),
 ("Fables de La Fontaine Le Corbeau", "Jean de La Fontaine", "Fables", "Poésie", "CE1"),
]

out = []
for q, auteur, oeuvre, genre, niv in CIBLES:
    best = None
    for title in search(q):
        if not re.search(r'(chapitre|acte|chant|scène|scene|livre)', title, re.I): continue
        ps = paragraphs(title)
        if len(ps) >= 2 and sum(len(p.split()) for p in ps) >= 130:
            best = (title, ps); break
    if not best:
        print("ECHEC", q, flush=True); continue
    title, ps = best
    acc, n = [], 0
    for p in ps:
        acc.append(p); n += len(p.split())
        if n >= 380: break
    body = "\n".join(acc)
    out.append({"auteur":auteur, "oeuvre":oeuvre, "genre":genre, "niveau":niv,
                "source":title, "texte":body, "mots":len(body.split())})
    json.dump(out, open("/workspace/lire/textes.json","w"), ensure_ascii=False, indent=1)
    print(f"OK {auteur:20s} {oeuvre[:26]:26s} {len(body.split()):4d} mots <- {title[:44]}", flush=True)

print("TOTAL", len(out))
