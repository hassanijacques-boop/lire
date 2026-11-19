#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Découverte des pages Wikisource pour Maupassant / Zola / littérature étrangère."""
import json, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/2.2 (pedagogie; hassanijacques@gmail.com)"}

def get(p):
    p.update({"format": "json", "formatversion": "2"})
    u = API + "?" + urllib.parse.urlencode(p)
    for a in range(4):
        try:
            time.sleep(2.0 + a * 5)
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                continue
            print("HTTP", e.code, p, flush=True)
            return {}
        except Exception as ex:
            print("ERR", ex, flush=True)
            time.sleep(4)
    return {}

def sous_pages(prefix):
    d = get({"action": "query", "list": "allpages", "apprefix": prefix, "aplimit": "60"})
    return [x["title"] for x in d.get("query", {}).get("allpages", [])]

def recherche(q, n=10):
    d = get({"action": "query", "list": "search", "srsearch": q, "srlimit": str(n), "srnamespace": "0"})
    return [x["title"] for x in d.get("query", {}).get("search", [])]

if __name__ == "__main__":
    print("### MAUPASSANT — recueils")
    for p in ["Miss Harriet", "Toine", "Mademoiselle Fifi", "La Maison Tellier",
              "Contes du jour et de la nuit", "Le Rosier de Mme Husson", "Clair de lune"]:
        print(flush=True)
        print("PREFIX:", p, flush=True)
        for t in sous_pages(p)[:40]:
            print("   ", t, flush=True)

    print("\n### RECHERCHES NOUVELLES", flush=True)
    for q in ['intitle:"La Ficelle"', 'intitle:"Deux Amis"', 'intitle:"Mon oncle Jules"',
              'intitle:"Aux champs"', 'intitle:"Le Loup"', 'intitle:"Pierrot"',
              'intitle:"Le Petit Fût"', 'intitle:"En voyage"']:
        print("Q:", q, "->", recherche(q, 6), flush=True)

    print("\n### GERMINAL", flush=True)
    for t in sous_pages("Germinal"):
        print("   ", t, flush=True)

    print("\n### ETRANGER", flush=True)
    for p in ["Les Aventures de Tom Sawyer", "Les Aventures de Tom Sawyer (trad. Bay)",
              "David Copperfield", "Les Aventures d’Alice au pays des merveilles",
              "Alice au pays des merveilles", "Robinson Crusoé", "Voyages de Gulliver",
              "Le Livre de la jungle", "Les Aventures de Sherlock Holmes"]:
        print(flush=True)
        print("PREFIX:", p, flush=True)
        for t in sous_pages(p)[:25]:
            print("   ", t, flush=True)
