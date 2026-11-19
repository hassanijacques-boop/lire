#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, time, urllib.parse, urllib.request
API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/2.2 (pedagogie; hassanijacques@gmail.com)"}
def get(p):
    p.update({"format": "json", "formatversion": "2"})
    u = API + "?" + urllib.parse.urlencode(p)
    for a in range(3):
        try:
            time.sleep(2.0 + a * 5)
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception:
            time.sleep(4)
    return {}
def sp(prefix, n=80):
    d = get({"action": "query", "list": "allpages", "apprefix": prefix, "aplimit": str(n)})
    return [x["title"] for x in d.get("query", {}).get("allpages", [])]
def rech(q, n=8):
    d = get({"action": "query", "list": "search", "srsearch": q, "srlimit": str(n), "srnamespace": "0"})
    return [x["title"] for x in d.get("query", {}).get("search", [])]
for p in ["Miss Harriet (recueil)", "Toine (recueil", "Mademoiselle Fifi (recueil", "Contes de la bécasse", "La Maison Tellier (recueil", "Contes du jour et de la nuit"]:
    print("\nPREFIX:", p, flush=True)
    for t in sp(p, 40): print("   ", t, flush=True)
print("\nRECHERCHES", flush=True)
for q in ['intitle:"Toine" Maupassant', 'intitle:"Voyages de Gulliver"', 'intitle:"Gulliver" Swift', 'intitle:"Le Horla"']:
    print("Q:", q, "->", rech(q), flush=True)
