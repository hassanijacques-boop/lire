#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vague 2 : Verne, Hugo, Balzac, Tchekhov."""
import json, sys
sys.path.insert(0, "/workspace/lire")
from fetch_oeuvre import build

CIBLES = [
 ("https://www.texteslibres.fr/voyage-au-centre-de-la-terre-jules-verne.html",
  "Voyage au centre de la Terre","Jules Verne","Roman","CM2",12),
 ("https://www.texteslibres.fr/de-la-terre-a-la-lune-jules-verne.html",
  "De la Terre à la Lune","Jules Verne","Roman","CM1",10),
 ("https://www.texteslibres.fr/les-enfants-du-capitaine-grant-jules-verne.html",
  "Les Enfants du capitaine Grant","Jules Verne","Roman","CM2",10),
 ("https://www.texteslibres.fr/le-dernier-jour-dun-condamne-victor-hugo.html",
  "Le Dernier Jour d’un condamné","Victor Hugo","Roman","CM2",8),
 ("https://www.texteslibres.fr/les-contemplations-pauca-meae-victor-hugo.html",
  "Les Contemplations · Pauca meae","Victor Hugo","Poésie","CM1",8),
 ("https://www.texteslibres.fr/la-cousine-bette-honore-de-balzac.html",
  "La Cousine Bette","Honoré de Balzac","Roman","Lycée",10),
 ("https://www.texteslibres.fr/les-trois-surs-anton-tchekhov.html",
  "Les Trois Sœurs","Anton Tchekhov","Théâtre","Lycée",5),
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
    json.dump(out, open("/workspace/lire/oeuvres_batch2.json","w"), ensure_ascii=False, indent=1)

print("TOTAL", len(out), "œuvres,", sum(len(x["moments"]) for x in out), "moments")
