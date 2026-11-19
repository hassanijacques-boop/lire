#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Maupassant (recueils), Zola (Germinal), et littérature étrangère."""
import json, sys
sys.path.insert(0, "/workspace/lire")
from fetch_oeuvre import build

CIBLES = [
 ("https://www.texteslibres.fr/contes-de-la-becasse-guy-de-maupassant.html",
  "Contes de la bécasse","Guy de Maupassant","Nouvelle","CM2",8),
 ("https://www.texteslibres.fr/clair-de-lune-guy-de-maupassant.html",
  "Clair de lune","Guy de Maupassant","Nouvelle","CM2",8),
 ("https://www.texteslibres.fr/germinal-emile-zola.html",
  "Germinal","Émile Zola","Roman","CM2",12),
 ("https://www.texteslibres.fr/guerre-et-paix-leon-tolstoi.html",
  "Guerre et Paix","Léon Tolstoï","Roman","Lycée",12),
 ("https://www.texteslibres.fr/crime-et-chatiment-fiodor-dostoievski.html",
  "Crime et Châtiment","Fiodor Dostoïevski","Roman","Lycée",12),
 ("https://www.texteslibres.fr/les-aventures-de-tom-sawyer-mark-twain.html",
  "Les Aventures de Tom Sawyer","Mark Twain","Roman","CM2",12),
 ("https://www.texteslibres.fr/croc-blanc-jack-london.html",
  "Croc-Blanc","Jack London","Roman","CM1",12),
 ("https://www.texteslibres.fr/le-joueur-fiodor-dostoievski.html",
  "Le Joueur","Fiodor Dostoïevski","Roman","Lycée",6),
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
    json.dump(out, open("/workspace/lire/oeuvres_batch.json","w"), ensure_ascii=False, indent=1)

print("TOTAL", len(out), "œuvres,", sum(len(x["moments"]) for x in out), "moments")
