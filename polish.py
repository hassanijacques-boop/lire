#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Passe de finition : titres nettoyés, sources vérifiées, Maupassant/Germinal/étranger curatés."""
import json, re, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/2.6 (pedagogie; hassanijacques@gmail.com)"}
BASE = "/workspace/lire"

def call(p, tries=4):
    p.update({"format": "json", "formatversion": "2"})
    u = API + "?" + urllib.parse.urlencode(p)
    for a in range(tries):
        try:
            time.sleep(1.6 + a * 5)
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=35) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                continue
            return {}
        except Exception:
            time.sleep(4)
    return {}

O = json.load(open(f"{BASE}/oeuvres.json"))
B3 = json.load(open(f"{BASE}/batch3.json"))
MAUP = json.load(open(f"{BASE}/maup_final.json"))
d = {o["oeuvre"]: o for o in O}

# ─── 1. nettoyage générique des titres pollués (titre + début du texte) ───
def nettoie_titre(t, x):
    for n in (40, 30, 25, 20):
        frag = x[:n]
        if len(frag) >= 15 and frag in t:
            t = t.split(frag)[0]
            break
    t = re.sub(r"\s+(Plus|Puis|Cependant|Depuis|Mais|Or|Et)\s*$", "", t)
    return t.strip(" ·—-–…").strip() or t.strip()

for o in O:
    for m in o["moments"]:
        m["t"] = nettoie_titre(m["t"], m["x"])

# ─── 2. retrait des extraits lycée + récupération des nouvelles seules ───
def retire(nom):
    for i, o in enumerate(O):
        if o["oeuvre"] == nom:
            return O.pop(i)
    return None

retire("Guerre et Paix"); retire("Le Joueur"); retire("Les Trois Sœurs")
parure = retire("La Parure")["moments"][0]
boule = retire("Boule de Suif")["moments"][0]
retire("Le Horla")
papa = retire("Le Papa de Simon")["moments"][0]

# ─── 3. Maupassant : une œuvre « Nouvelles choisies » ───
ordre = ["Le Papa de Simon", "Pierrot", "La Ficelle", "Mon oncle Jules", "Aux champs",
         "Deux amis", "La Rempailleuse", "Le Petit Fût", "Toine", "La Parure",
         "Boule de Suif", "Le Horla"]
mom = []
for t in ordre:
    if t in MAUP:
        mom.append(MAUP[t])
    elif t == "La Parure":
        mom.append({"t": t, "x": parure["x"], "mots": parure["mots"],
                    "src": "Contes du jour et de la nuit (éd. Flammarion, 1885)/La Parure"})
    elif t == "Boule de Suif":
        mom.append({"t": t, "x": boule["x"], "mots": boule["mots"],
                    "src": "Boule de suif (recueil)/Boule de Suif"})
    elif t == "Le Papa de Simon":
        mom.append({"t": t, "x": papa["x"], "mots": papa["mots"],
                    "src": "La Maison Tellier (recueil, Ollendorff 1891)/Le Papa de Simon"})
nouvelles = {"oeuvre": "Nouvelles choisies", "auteur": "Guy de Maupassant",
             "genre": "Nouvelle", "niveau": "CM2", "moments": mom}

# ─── 4. Germinal reconstruit (15 chapitres titrés) ───
GT = {1: "L’arrivée d’Étienne à Montsou", 2: "Le coron des Deux-Cent-Quarante",
      3: "Dans la cour du Voreux", 7: "La Piolaine, chez les Grégoire",
      8: "Le réveil chez les Maheu", 12: "Étienne s’habitue à la mine",
      15: "La paie du samedi", 19: "La grève s’installe", 22: "Jeanlin, le petit voleur",
      26: "La marche vers Montsou", 29: "La fusillade", 30: "L’hiver de la défaite",
      33: "Étienne et Catherine dans la neige", 36: "La promenade au canal",
      40: "Le printemps revient"}
germ = {"oeuvre": "Germinal", "auteur": "Émile Zola", "genre": "Roman", "niveau": "CM2",
        "moments": [{"t": GT[b["val"]], "x": b["x"], "mots": b["mots"], "src": b["page"]}
                    for b in B3 if b["cle"] == "GERM"]}

# ─── 5. œuvres étrangères ajoutées si absentes ───
def depuis_b3(cle, nom, auteur, genre, niveau):
    if nom in d:
        return None
    return {"oeuvre": nom, "auteur": auteur, "genre": genre, "niveau": niveau,
            "moments": [{"t": b["val"], "x": b["x"], "mots": b["mots"], "src": b["page"]}
                        for b in B3 if b["cle"] == cle]}

nouvelles_oeuvres = [depuis_b3("DC", "David Copperfield", "Charles Dickens", "Roman", "CM2"),
                     depuis_b3("ALICE", "Alice au pays des merveilles", "Lewis Carroll", "Conte", "CM1"),
                     depuis_b3("JUNGLE", "Le Livre de la jungle", "Rudyard Kipling", "Nouvelle", "CM2"),
                     depuis_b3("SHER", "Les Aventures de Sherlock Holmes", "Arthur Conan Doyle", "Nouvelle", "CM2")]

# ─── 6. ordre final ───
final = []
for o in O:
    if o["oeuvre"] == "Germinal":
        final.append(germ)
    elif o["oeuvre"] == "Contes de la bécasse":
        final.append(nouvelles)
        final.append(o)
    elif o["oeuvre"] == "Clair de lune":
        final.append(o)
        final += [x for x in nouvelles_oeuvres if x]
    else:
        final.append(o)

# ─── 7. sources : URL par œuvre connue ───
TOM = "Les Aventures de Tom Sawyer/Traduction Hughes, 1884/"
VCT = "Voyage au centre de la Terre/Chapitre "
LUNE = "De la Terre à la Lune/Chapitre "
GT5 = {5: "Le parchemin", 9: "Le départ", 13: "En Islande", 17: "Le véritable voyage commence",
       21: "Cinq jours de marche", 25: "Au plus profond des abîmes", 29: "Le réveil dans l’obscurité",
       33: "La mer souterraine", 37: "La stupeur du professeur", 41: "Le 27 août", 45: "La conclusion"}
REPL = {"Clair de lune (recueil, 1884)/La Légende du Mont Saint-Michel":
        "Clair de lune (recueil, 1884)/La Légende du mont Saint-Michel",
        "Clair de lune (recueil, 1884)/Moiron": "Clair de lune (recueil, 1905)/Moiron",
        "Clair de lune (recueil, 1884)/La Nuit (cauchemar)": "Clair de lune (recueil, 1905)/La Nuit",
        "Contes de la bécasse/Un Fils": "Contes de la bécasse/Un fils",
        "Toine (recueil)/Édition Conard, 1910/Toine": "Toine (recueil)/Toine"}

for o in final:
    nom = o["oeuvre"]
    for m in o["moments"]:
        old = m.get("src", "")
        num = re.match(r"(\d+)\.", old)
        if nom in ("Les Aventures de Tom Sawyer", "Croc-Blanc", "De la Terre à la Lune",
                   "Voyage au centre de la Terre") and num:
            n = num.group(1)
            m["url"] = {"Les Aventures de Tom Sawyer": TOM + n,
                        "Croc-Blanc": "Croc-Blanc/Chapitre " + n,
                        "De la Terre à la Lune": LUNE + n,
                        "Voyage au centre de la Terre": VCT + n}[nom]
        elif nom == "Voyage au centre de la Terre" and num:
            m["url"] = VCT + num.group(1)
        elif nom in ("Contes de la bécasse", "Clair de lune"):
            m["url"] = nom + "/" + m["t"].replace("'", "’")
        elif nom == "Les Contemplations · Pauca meae":
            m["url"] = "Les Contemplations/" + m["t"].replace("'", "’")
        else:
            m["url"] = old
        m["url"] = REPL.get(m["url"], m["url"])

# titres des chapitres de Voyage au centre de la Terre
for o in final:
    if o["oeuvre"] == "Voyage au centre de la Terre":
        for m in o["moments"]:
            n = int(m["url"].split(" ")[-1])
            if n in GT5:
                m["t"] = GT5[n] + f" · chapitre {n}"

# ─── 8. validation des liens ───
toutes = sorted({m["url"] for o in final for m in o["moments"] if m.get("url")})
ok = set()
for i in range(0, len(toutes), 45):
    r = call({"action": "query", "titles": "|".join(toutes[i:i + 45]), "redirects": 1})
    for p in r.get("query", {}).get("pages", []):
        if not p.get("missing"):
            ok.add(p["title"])
print(f"Liens valides : {len(ok)}/{len(toutes)}")
for u in toutes:
    if u not in ok:
        print("   ✗", u[:90])

# ─── 9. libellés lisibles ───
ROM = [("Miss Harriet", "Miss Harriet (1884)"), ("Mademoiselle Fifi", "Mademoiselle Fifi (1882)"),
       ("Contes de la bécasse", "Contes de la bécasse (1883)"), ("Toine (recueil", "Toine (1885)"),
       ("Le Horla (recueil", "Le Horla (1887)"), ("Les Sœurs Rondoli", "Les Sœurs Rondoli (1884)"),
       ("Contes du jour et de la nuit", "Contes du jour et de la nuit (1885)"),
       ("Boule de suif", "Boule de suif (1880)"), ("La Maison Tellier", "La Maison Tellier (1881)")]

def libelle(o, m, url):
    nom, t = o["oeuvre"], m["t"]
    if nom == "Nouvelles choisies":
        for k, v in ROM:
            if url.startswith(k):
                return v
        return "Wikisource"
    if nom == "Germinal":
        r = re.search(r"Partie (\w+)/\w+ (\d+)", url)
        return f"Germinal, partie {r.group(1)}, chapitre {r.group(2)}" if r else "Germinal"
    if nom in ("Les Aventures de Tom Sawyer", "Croc-Blanc", "De la Terre à la Lune",
               "Voyage au centre de la Terre", "Alice au pays des merveilles", "David Copperfield"):
        return f"{nom}, {m['t'].split(' · ')[0] if 'chapitre' in m['t'] else m['t']}"
    if nom in ("Le Livre de la jungle", "Les Aventures de Sherlock Holmes"):
        return f"{nom} — {t}" if t.startswith("«") else f"{nom} — « {t} »"
    if nom in ("Contes de la bécasse", "Clair de lune"):
        return f"{nom} (recueil) — « {t} »"
    if nom == "Les Contemplations · Pauca meae":
        return f"Les Contemplations — « {t} »"
    return nom

for o in final:
    for m in o["moments"]:
        u = m.get("url", "")
        if u and u in ok:
            m["src"] = libelle(o, m, u)
        else:
            m["url"] = ""
            olds = re.sub(r"^\d+\.\s*", "", m.get("src", ""))
            if olds and not re.search(r"[a-zà-ÿ]{3,} [A-ZÉÈÀ][a-zà-ÿ]+ [a-zà-ÿ]{2,}", olds):
                m["src"] = olds if len(olds) < 70 else o["oeuvre"]
            else:
                m["src"] = o["oeuvre"]

json.dump(final, open(f"{BASE}/oeuvres.json", "w"), ensure_ascii=False, indent=1)
tpl = open(f"{BASE}/template2.html", encoding="utf-8").read()
open(f"{BASE}/index.html", "w", encoding="utf-8").write(
    tpl.replace("__OEUVRES__", json.dumps(final, ensure_ascii=False, separators=(",", ":"))))

print("\n=== TOTAL :", len(final), "œuvres ·", sum(len(o["moments"]) for o in final), "moments")
print("Liens Wikisource :", sum(1 for o in final for m in o["moments"] if m.get("url")))
for o in final:
    print(f"   {len(o['moments']):3d}  {o['oeuvre'][:38]:40s} {o['niveau']}")
