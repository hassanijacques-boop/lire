#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vague 3 : Maupassant (3 recueils), Verne, Baudelaire, Rimbaud."""
import json, sys
sys.path.insert(0, "/workspace/lire")
from fetch_oeuvre import build

CIBLES = [
 ("https://www.texteslibres.fr/la-maison-tellier-guy-de-maupassant.html",
  "La Maison Tellier","Guy de Maupassant","Nouvelle","CM2",8),
 ("https://www.texteslibres.fr/mademoiselle-fifi-guy-de-maupassant.html",
  "Mademoiselle Fifi","Guy de Maupassant","Nouvelle","CM2",8),
 ("https://www.texteslibres.fr/miss-harriet-guy-de-maupassant.html",
  "Miss Harriet","Guy de Maupassant","Nouvelle","CM2",8),
 ("https://www.texteslibres.fr/cinq-semaines-en-ballon-jules-verne.html",
  "Cinq semaines en ballon","Jules Verne","Roman","CM2",10),
 ("https://www.texteslibres.fr/les-fleurs-du-mal.html",
  "Les Fleurs du mal","Charles Baudelaire","Poésie","Lycée",10),
 ("https://www.texteslibres.fr/poesies-arthur-rimbaud.html",
  "Poésies","Arthur Rimbaud","Poésie","CM2",8),
]

out = []
for url, o, a, g, n, k in CIBLES:
    try:
        r = build(url, o, a, g, n, k)
        if len(r["moments"]) >= 3:
            out.append(r)
            print(f"== {o} : {len(r['moments'])} moments", flush=True)
    except Exception as e:
        print("ERREUR", o, str(e)[:80], flush=True)
    json.dump(out, open("/workspace/lire/oeuvres_batch3.json","w"), ensure_ascii=False, indent=1)

print("TOTAL", len(out), "œuvres,", sum(len(x["moments"]) for x in out), "moments")
