#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construction de la bibliothèque finale : Maupassant (nouvelles) + Germinal + étranger."""
import json, re, html, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/2.4 (pedagogie; hassanijacques@gmail.com)"}
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

def texte(title):
    d = call({"action": "parse", "page": title, "prop": "text", "redirects": 1})
    h = d.get("parse", {}).get("text", "")
    if len(h) < 700:
        return ""
    h = re.sub(r'<sup[^>]*>(.*?)</sup>',
               lambda m: re.sub(r'<[^>]+>', '', m.group(1)).lower(), h, flags=re.S)
    h = re.sub(r'<(table|style|script).*?</\1>', ' ', h, flags=re.S)
    h = re.sub(r'<div[^>]*class="[^"]*poem[^"]*"[^>]*>.*?</div>', ' ', h, flags=re.S)
    out = []
    for p in re.findall(r'<p[^>]*>(.*?)</p>', h, re.S):
        t = html.unescape(re.sub(r'<[^>]+>', '', p)).replace("\u00a0", " ").replace("ſ", "s")
        t = re.sub(r'\s+', ' ', t).strip()
        if len(t) < 90:
            continue
        low = t.lower()
        if any(k in low for k in ("wikisource", "licence", "domaine public", "catégorie",
                                 "texte établi", "imprimerie", "cette édition")):
            continue
        if not re.search(r'[.!?»]', t):
            continue
        out.append(t)
    return " ".join(out)

def coupe(txt, n=380):
    s = " ".join(txt.split()[:n])
    m = max(s.rfind("."), s.rfind("!"), s.rfind("?"), s.rfind("»"))
    if m > len(s) * 0.55:
        s = s[:m + 1]
    return s

# ─────────────── 1. Maupassant : onze nouvelles ───────────────
MH = "Miss Harriet (recueil)/Édition Conard, 1910/"
FIFI = "Mademoiselle Fifi (recueil, Ollendorff 1898)/"
BEC = "Contes de la bécasse/"
TOI = "Toine (recueil)/Édition Conard, 1910/"
N = [
 (BEC + "La Rempailleuse", "La Rempailleuse"),
 (MH + "La Ficelle", "La Ficelle"),
 (MH + "Mon oncle Jules", "Mon oncle Jules"),
 (FIFI + "Deux amis", "Deux amis"),
 (BEC + "Aux champs", "Aux champs"),
 (BEC + "Pierrot", "Pierrot"),
 ("Les Sœurs Rondoli (recueil, Ollendorff 1904)/Le Petit Fût", "Le Petit Fût"),
 (TOI + "Toine", "Toine"),
 ("Le Horla (recueil, Ollendorff 1895)/Le Horla", "Le Horla"),
]
chat = {}
for page, titre in N:
    txt = texte(page)
    if len(txt.split()) < 110:
        print("ECHEC", page, flush=True)
        continue
    txt = re.sub(r'^À [A-ZÉÈÀÂÎÔÛ][^.]{0,45}\.\s*', '', txt)  # dédicace
    body = coupe(txt)
    chat[titre] = {"t": titre, "x": body, "mots": len(body.split()), "src": page}
    print(f"MAUP {len(body.split()):4d}m {titre:22s} {body[:60]}", flush=True)
json.dump(chat, open(f"{BASE}/maup_final.json", "w"), ensure_ascii=False, indent=1)

# ─────────────── 2. assemblage ───────────────
O = json.load(open(f"{BASE}/oeuvres.json"))
B3 = json.load(open(f"{BASE}/batch3.json"))
d = {o["oeuvre"]: o for o in O}

def garde(nom):
    return d.pop(nom, None)

# récupérer avant suppression
parure = garde("La Parure")["moments"][0]
boule = garde("Boule de Suif")["moments"][0]
horla_old = garde("Le Horla")
papa = garde("Le Papa de Simon")["moments"][0]
germ_old = garde("Germinal")
garde("Guerre et Paix"); garde("Le Joueur")
bec = d["Contes de la bécasse"]; clair = d["Clair de lune"]
tom = d["Les Aventures de Tom Sawyer"]; croc = d["Croc-Blanc"]

# ── Maupassant : une seule œuvre « Nouvelles choisies » ──
ordre = ["Le Papa de Simon", "Pierrot", "La Ficelle", "Mon oncle Jules", "Aux champs",
         "Deux amis", "La Rempailleuse", "Le Petit Fût", "Toine", "La Parure",
         "Boule de Suif", "Le Horla"]
mom = []
for t in ordre:
    if t in chat:
        mom.append(chat[t])
    elif t == "La Parure":
        parure["src"] = "Contes du jour et de la nuit (éd. Flammarion, 1885)/La Parure"
        mom.append({k: parure[k] for k in ("t", "x", "mots", "src")})
    elif t == "Boule de Suif":
        boule["src"] = "Boule de suif (recueil)/Boule de Suif"
        mom.append({k: boule[k] for k in ("t", "x", "mots", "src")})
    elif t == "Le Papa de Simon":
        papa["src"] = "La Maison Tellier (recueil, Ollendorff 1891)/Le Papa de Simon"
        mom.append({k: papa[k] for k in ("t", "x", "mots", "src")})
nouvelles = {"oeuvre": "Nouvelles choisies", "auteur": "Guy de Maupassant",
             "genre": "Nouvelle", "niveau": "CM2", "moments": mom}

# ── Contes de la bécasse / Clair de lune : sources réparées ──
for m in bec["moments"]:
    m["src"] = BEC + m["t"].replace("'", "’")
for m in clair["moments"]:
    if m["t"].startswith("La Nuit"):
        m["t"] = "La Nuit (cauchemar)"
    m["src"] = "Clair de lune (recueil, 1884)/" + m["t"]

# ── Tom Sawyer / Croc-Blanc : source = chapitre d'après le numéro ──
TOM = "Les Aventures de Tom Sawyer/Traduction Hughes, 1884/"
fix_tom = {"Les fiançailles Plus": "Les fiançailles",
           "Le pique-nique Bien que le vendredi soit un jour…": "Le pique-nique"}
for m in tom["moments"]:
    n = int(re.match(r"(\d+)\.", m["src"]).group(1))
    m["src"] = TOM + str(n)
    m["t"] = fix_tom.get(m["t"], m["t"])
for m in croc["moments"]:
    n = int(re.match(r"(\d+)\.", m["src"]).group(1))
    m["src"] = "Croc-Blanc/Chapitre " + str(n)
    if m["t"].startswith("Le domaine du dieu"):
        m["t"] = "Le domaine du dieu"

# ── Germinal : 15 chapitres, titres vérifiés sur le texte ──
GT = {
 1: "L’arrivée d’Étienne à Montsou",
 2: "Le coron des Deux-Cent-Quarante",
 3: "Dans la cour du Voreux",
 7: "La Piolaine, chez les Grégoire",
 8: "Le réveil chez les Maheu",
 12: "Étienne s’habitue à la mine",
 15: "La paie du samedi",
 19: "La grève s’installe",
 22: "Jeanlin, le petit voleur",
 26: "La marche vers Montsou",
 29: "La fusillade",
 30: "L’hiver de la défaite",
 33: "Étienne et Catherine dans la neige",
 36: "La promenade au canal",
 40: "Le printemps revient",
}
germ = {"oeuvre": "Germinal", "auteur": "Émile Zola", "genre": "Roman", "niveau": "CM2",
        "moments": [{"t": GT[b["val"]], "x": b["x"], "mots": b["mots"], "src": b["page"]}
                    for b in B3 if b["cle"] == "GERM"]}

# ── nouvelles œuvres étrangères ──
def oeuvre(cle, nom, auteur, genre, niveau):
    ms = [{"t": b["val"], "x": b["x"], "mots": b["mots"], "src": b["page"]}
          for b in B3 if b["cle"] == cle]
    return {"oeuvre": nom, "auteur": auteur, "genre": genre, "niveau": niveau, "moments": ms}

dc = oeuvre("DC", "David Copperfield", "Charles Dickens", "Roman", "CM2")
alice = oeuvre("ALICE", "Alice au pays des merveilles", "Lewis Carroll", "Conte", "CM1")
jungle = oeuvre("JUNGLE", "Le Livre de la jungle", "Rudyard Kipling", "Nouvelle", "CM2")
sher = oeuvre("SHER", "Les Aventures de Sherlock Holmes", "Arthur Conan Doyle", "Nouvelle", "CM2")

# ── ordre final ──
final, place_nouv, place_germ = [], False, False
for o in O:
    nom = o["oeuvre"]
    if nom in ("La Parure", "Boule de Suif", "Le Horla", "Le Papa de Simon",
               "Guerre et Paix", "Le Joueur"):
        continue
    if nom == "Contes de la bécasse":
        final.append(nouvelles)
        final.append(o)
    elif nom == "Germinal":
        final.append(germ)
    elif nom == "Don Quichotte":
        final.append(o)
    elif nom == "Clair de lune":
        final.append(o)
        final += [dc, alice, jungle, sher]
    else:
        final.append(o)

json.dump(final, open(f"{BASE}/oeuvres.json", "w"), ensure_ascii=False, indent=1)
t = open(f"{BASE}/template2.html", encoding="utf-8").read()
open(f"{BASE}/index.html", "w", encoding="utf-8").write(
    t.replace("__OEUVRES__", json.dumps(final, ensure_ascii=False, separators=(",", ":"))))

print("\n=== TOTAL :", len(final), "œuvres ·", sum(len(o["moments"]) for o in final), "moments")
for o in final:
    print(f"   {len(o['moments']):3d}  {o['oeuvre'][:36]:38s} {o['auteur'][:22]:24s} {o['niveau']}")

# ─────────────── 3. vérification de toutes les sources ───────────────
allsrc = sorted({m["src"] for o in final for m in o["moments"] if m.get("src")})
print("\n=== VÉRIFICATION DE", len(allsrc), "PAGES SOURCE ===")
manquants = []
for i in range(0, len(allsrc), 45):
    lot = allsrc[i:i + 45]
    r = call({"action": "query", "titles": "|".join(lot)})
    pages = r.get("query", {}).get("pages", [])
    if isinstance(pages, dict):
        pages = list(pages.values())
    for p in pages:
        if p.get("missing"):
            manquants.append(p["title"])
print("PAGES MANQUANTES :", len(manquants))
for m in manquants:
    print("   ✗", m)
json.dump(manquants, open(f"{BASE}/sources_manquantes.json", "w"), ensure_ascii=False, indent=1)
