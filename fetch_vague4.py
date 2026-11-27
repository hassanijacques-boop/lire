# -*- coding: utf-8 -*-
"""Ajoute des oeuvres pour tous les niveaux dans Lire."""
import json, sys
sys.path.insert(0, "/workspace/lire")
from fetch_oeuvre import build

CIBLES = [
 ("https://www.texteslibres.fr/contes-de-perrault-charles-perrault.html",
  "Contes de Perrault","Charles Perrault","Conte","CP",14),
 ("https://www.texteslibres.fr/contes-d-andersen-hans-christian-andersen.html",
  "Contes d'Andersen","Hans Christian Andersen","Conte","CE1",14),
 ("https://www.texteslibres.fr/lettres-de-mon-moulin-alphonse-daudet.html",
  "Lettres de mon moulin","Alphonse Daudet","Nouvelle","CE2",10),
 ("https://www.texteslibres.fr/alice-au-pays-des-merveilles-lewis-carroll.html",
  "Alice au pays des merveilles","Lewis Carroll","Roman","CE2",12),
 ("https://www.texteslibres.fr/les-fourberies-de-scapin.html",
  "Les Fourberies de Scapin","Molière","Théâtre","CM1",5),
 ("https://www.texteslibres.fr/le-bourgeois-gentilhomme.html",
  "Le Bourgeois gentilhomme","Molière","Théâtre","CM1",5),
 ("https://www.texteslibres.fr/l-appel-de-la-foret-jack-london.html",
  "L'Appel de la forêt","Jack London","Roman","CM1",12),
 ("https://www.texteslibres.fr/sans-famille-hector-malot.html",
  "Sans famille","Hector Malot","Roman","CM2",14),
 ("https://www.texteslibres.fr/les-enfants-du-capitaine-grant-jules-verne.html",
  "Les Enfants du capitaine Grant","Jules Verne","Roman","CM2",12),
 ("https://www.texteslibres.fr/cyrano-de-bergerac-edmond-rostand.html",
  "Cyrano de Bergerac","Edmond Rostand","Théâtre","CM2",6),
]

out = []
for url, o, a, g, n, k in CIBLES:
    try:
        r = build(url, o, a, g, n, k)
        if len(r["moments"]) >= 3:
            out.append(r)
            print(f"== {o} : {len(r['moments'])} moments", flush=True)
        else:
            print(f"-- {o} : trop peu ({len(r['moments'])})", flush=True)
    except Exception as e:
        print("ERREUR", o, str(e)[:70], flush=True)
    json.dump(out, open("/workspace/lire/oeuvres_vague4.json", "w"), ensure_ascii=False, indent=1)

print("TOTAL", len(out), "oeuvres,", sum(len(x["moments"]) for x in out), "moments")
