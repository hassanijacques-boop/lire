# -*- coding: utf-8 -*-
"""Nettoie les titres des contes et integre les nouvelles oeuvres dans Lire."""
import json, re

CONNUES = [
 "Le Chat botté", "La Belle au bois dormant", "Les Fées", "Cendrillon",
 "Le Petit Poucet", "Peau d'Âne", "Les Souhaits ridicules", "Barbe-Bleue",
 "La Bergère et le Ramoneur", "L'Ange", "La Princesse sur un pois",
 "Les Fleurs de la petite Ida", "La Petite Fille aux allumettes", "L'Ombre",
 "La Pâquerette", "La Petite Sirène", "Les Cygnes sauvages", "Le Chanvre",
 "Le Vilain Petit Canard", "Les Habits neufs de l'empereur",
]
CLES = {
 "chat bott": "Le Chat botté", "bois dormant": "La Belle au bois dormant",
 "les fées": "Les Fées", "cendrillon": "Cendrillon", "poucet": "Le Petit Poucet",
 "peau d": "Peau d'Âne", "souhaits": "Les Souhaits ridicules", "barbe-bleue": "Barbe-Bleue",
 "bergère et le ramoneur": "La Bergère et le Ramoneur", "l’ange": "L'Ange",
 "princesse sur un pois": "La Princesse sur un pois", "petite ida": "Les Fleurs de la petite Ida",
 "allumettes": "La Petite Fille aux allumettes", "l’ombre": "L'Ombre",
 "pâquerette": "La Pâquerette", "petite sirène": "La Petite Sirène",
 "cygnes sauvages": "Les Cygnes sauvages", "chanvre": "Le Chanvre",
 "vilain petit canard": "Le Vilain Petit Canard",
}

def nettoie(t):
    bas = t.lower()
    for k, v in CLES.items():
        if k in bas:
            return v
    # sinon : couper au premier passage en minuscule long
    m = re.search(r'^(.*?[a-zéèêàâîôûç’\'A-ZÉÈ]{3,})\s+[A-ZÉÈ][a-zéèêàâîôûç]{2,}', t)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) > 48:
        t = t[:45].rsplit(' ', 1)[0] + '…'
    return t

new = json.load(open('/workspace/lire/oeuvres_vague4.json'))
for o in new:
    for m in o["moments"]:
        m["t"] = nettoie(m["t"])

O = json.load(open('/workspace/lire/oeuvres.json'))
noms = {x["oeuvre"] for x in O}
ajout = 0
for o in new:
    if o["oeuvre"] not in noms:
        O.append(o); ajout += 1
        print("ajouté:", o["oeuvre"], "-", len(o["moments"]), "moments")

json.dump(O, open('/workspace/lire/oeuvres.json', 'w'), ensure_ascii=False, indent=1)
tpl = open('/workspace/lire/template2.html', encoding='utf-8').read()
html = tpl.replace("__OEUVRES__", json.dumps(O, ensure_ascii=False, separators=(",", ":")))
open('/workspace/lire/index.html', 'w', encoding='utf-8').write(html)

import collections
print("\nœuvres:", len(O), "| moments:", sum(len(x['moments']) for x in O))
print("par niveau:", dict(collections.Counter(x['niveau'] for x in O)))
print("taille:", len(html))
for o in O:
    if o["oeuvre"] in ("Contes de Perrault", "Contes d'Andersen"):
        print(o["oeuvre"], ":", [m["t"] for m in o["moments"]][:6])
