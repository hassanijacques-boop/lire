#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bibliothèque élargie : nouvelles, romans, poèmes, théâtre — textes du domaine public.
Extraction stricte : uniquement les paragraphes littéraires."""
import json, re, html, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/1.2 (outil pedagogique; hassanijacques@gmail.com)"}

def call(params, tries=4):
    params.update({"format":"json","formatversion":"2"})
    u = API + "?" + urllib.parse.urlencode(params)
    for a in range(tries):
        try:
            time.sleep(3 + a*7)
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("   429", flush=True); continue
            return {}
        except Exception:
            time.sleep(5)
    return {}

def search(q, n=10):
    d = call({"action":"query","list":"search","srsearch":q,"srlimit":n,"srnamespace":0})
    return [x["title"] for x in d.get("query",{}).get("search",[])]

BAD_TITLE = re.compile(r'^(Auteur|Catégorie|Wikisource|Portail|Modèle)\s*:', re.I)

def paras(title):
    d = call({"action":"parse","page":title,"prop":"text","redirects":1})
    h = d.get("parse",{}).get("text","")
    if not h or len(h) < 500: return []
    h = re.sub(r'<(sup|table|style|script).*?</\1>', ' ', h, flags=re.S)
    out = []
    for p in re.findall(r'<p[^>]*>(.*?)</p>', h, re.S):
        t = re.sub(r'<[^>]+>', '', p)
        t = html.unescape(t).replace("\u00a0", " ").replace("ſ", "s")
        t = re.sub(r'\s+', ' ', t).strip()
        if len(t) < 90: continue
        low = t.lower()
        if any(k in low for k in ("wikisource","licence","domaine public","catégorie","modifier",
                                  "texte établi","imprimerie","librairie","éditeur","édition originale")):
            continue
        if not re.search(r'[.!?»]', t): continue
        out.append(t)
    return out

# (recherche, auteur, oeuvre, genre, niveau)
CIBLES = [
 ("Maupassant La Parure", "Guy de Maupassant", "La Parure", "Nouvelle", "CM2"),
 ("Maupassant Boule de Suif", "Guy de Maupassant", "Boule de Suif", "Nouvelle", "CM2"),
 ("Maupassant Le Horla", "Guy de Maupassant", "Le Horla", "Nouvelle", "CM2"),
 ("Maupassant Le Papa de Simon", "Guy de Maupassant", "Le Papa de Simon", "Nouvelle", "CM1"),
 ("Zola Germinal chapitre", "Émile Zola", "Germinal", "Roman", "CM2"),
 ("Zola Au Bonheur des Dames chapitre", "Émile Zola", "Au Bonheur des Dames", "Roman", "CM2"),
 ("Dickens Un chant de Noël", "Charles Dickens", "Un chant de Noël", "Nouvelle", "CM1"),
 ("Dickens Oliver Twist chapitre", "Charles Dickens", "Oliver Twist", "Roman", "CM2"),
 ("Don Quichotte Cervantès chapitre", "Miguel de Cervantès", "Don Quichotte", "Roman", "CM2"),
 ("Cyrano de Bergerac Rostand tirade", "Edmond Rostand", "Cyrano de Bergerac", "Théâtre", "CM2"),
 ("Le Dormeur du val Rimbaud", "Arthur Rimbaud", "Le Dormeur du val", "Poésie", "CM1"),
 ("Demain dès l'aube Hugo", "Victor Hugo", "Demain, dès l'aube", "Poésie", "CE2"),
 ("Le Pont Mirabeau Apollinaire", "Guillaume Apollinaire", "Le Pont Mirabeau", "Poésie", "CM1"),
 ("L'Odyssée Homère chant", "Homère", "L'Odyssée", "Épopée", "CM1"),
 ("Fables La Fontaine Le Corbeau et le Renard", "Jean de La Fontaine", "Le Corbeau et le Renard", "Poésie", "CE1"),
 ("La Cigale et la Fourmi La Fontaine", "Jean de La Fontaine", "La Cigale et la Fourmi", "Poésie", "CP"),
 ("Contes Perrault Le Petit Chaperon rouge", "Charles Perrault", "Le Petit Chaperon rouge", "Conte", "CP"),
 ("Alice au pays des merveilles Carroll chapitre", "Lewis Carroll", "Alice au pays des merveilles", "Roman", "CM1"),
 ("Le Chat botté Perrault", "Charles Perrault", "Le Chat botté", "Conte", "CE1"),
]

out = []
for q, auteur, oeuvre, genre, niv in CIBLES:
    got = None
    for title in search(q):
        if BAD_TITLE.match(title): continue
        ps = paras(title)
        if len(ps) >= 2 and sum(len(p.split()) for p in ps) >= 120:
            got = (title, ps); break
    if not got:
        print("ECHEC", oeuvre, flush=True); continue
    title, ps = got
    acc, n = [], 0
    for p in ps:
        acc.append(p); n += len(p.split())
        if n >= 380: break
    body = "\n".join(acc)
    rec = {"auteur":auteur, "oeuvre":oeuvre, "genre":genre, "niveau":niv,
           "source":title, "texte":body, "mots":len(body.split()), "titre":oeuvre}
    out.append(rec)
    json.dump(out, open("/workspace/lire/textes2.json","w"), ensure_ascii=False, indent=1)
    print(f"OK {auteur[:20]:20s} {oeuvre[:28]:28s} {len(body.split()):4d} | {body[:55]}", flush=True)

print("TOTAL", len(out))
