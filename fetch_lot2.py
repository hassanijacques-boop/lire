#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lot 2 : Maupassant (nouvelles) + Zola (Germinal) + littérature étrangère.
Récupère les textes depuis Wikisource et écrit batch.json (à vérifier avant intégration).
"""
import json, re, html, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/2.2 (pedagogie; hassanijacques@gmail.com)"}

MAUP = "Miss Harriet (recueil)/Édition Conard, 1910/"
FIFI = "Mademoiselle Fifi (recueil, Ollendorff 1898)/"
BEC = "Contes de la bécasse/"
TOINE = "Toine (recueil)/Édition Conard, 1910/"

# (page wikisource, titre affiché, oeuvre, auteur, genre, niveau, source lisible)
PLAN = [
 # ── MAUPASSANT ──
 (BEC + "La Rempailleuse", "La Rempailleuse", "Nouvelles choisies", "Guy de Maupassant", "Nouvelle", "CM2", "Contes de la bécasse (1883)"),
 (MAUP + "La Ficelle", "La Ficelle", "Nouvelles choisies", "Guy de Maupassant", "Nouvelle", "CM2", "Miss Harriet (1884)"),
 (MAUP + "Mon oncle Jules", "Mon oncle Jules", "Nouvelles choisies", "Guy de Maupassant", "Nouvelle", "CM2", "Miss Harriet (1884)"),
 (FIFI + "Deux amis", "Deux amis", "Nouvelles choisies", "Guy de Maupassant", "Nouvelle", "CM2", "Mademoiselle Fifi (1882)"),
 (BEC + "Aux champs", "Aux champs", "Nouvelles choisies", "Guy de Maupassant", "Nouvelle", "CM2", "Contes de la bécasse (1883)"),
 (BEC + "Pierrot", "Pierrot", "Nouvelles choisies", "Guy de Maupassant", "Nouvelle", "CM1", "Contes de la bécasse (1883)"),
 (BEC + "En mer", "En mer", "Nouvelles choisies", "Guy de Maupassant", "Nouvelle", "CM2", "Contes de la bécasse (1883)"),
 ("Clair de lune (recueil, 1884)/Le Loup", "Le Loup", "Nouvelles choisies", "Guy de Maupassant", "Nouvelle", "CM2", "Clair de lune (1883)"),
 ("Les Sœurs Rondoli (recueil, Ollendorff 1904)/Le Petit Fût", "Le Petit Fût", "Nouvelles choisies", "Guy de Maupassant", "Nouvelle", "CM2", "Les Sœurs Rondoli (1884)"),
 (TOINE + "Toine", "Toine", "Nouvelles choisies", "Guy de Maupassant", "Nouvelle", "CM2", "Toine (1885)"),
 ("Le Horla (recueil, Ollendorff 1895)/Le Horla", "Le Horla", "Nouvelles choisies", "Guy de Maupassant", "Nouvelle", "CM2", "Le Horla (1887)"),

 # ── ZOLA / GERMINAL ──
 ("Germinal/Partie I/Chapitre 1", "L’arrivée d’Étienne au Voreux", "Germinal", "Émile Zola", "Roman", "CM2", "Partie I, ch. 1"),
 ("Germinal/Partie I/Chapitre 2", "La descente dans la mine", "Germinal", "Émile Zola", "Roman", "CM2", "Partie I, ch. 2"),
 ("Germinal/Partie II/Chapitre 1", "Chez les Maheu : la vie du coron", "Germinal", "Émile Zola", "Roman", "CM2", "Partie II, ch. 1"),
 ("Germinal/Partie III/Chapitre 3", "La forêt de Vandame", "Germinal", "Émile Zola", "Roman", "CM2", "Partie III, ch. 3"),
 ("Germinal/Partie IV/Chapitre 4", "La foule devant la fosse", "Germinal", "Émile Zola", "Roman", "CM2", "Partie IV, ch. 4"),
 ("Germinal/Partie V/Chapitre 1", "La délégation chez le directeur", "Germinal", "Émile Zola", "Roman", "CM2", "Partie V, ch. 1"),
 ("Germinal/Partie V/Chapitre 5", "La fusillade", "Germinal", "Émile Zola", "Roman", "CM2", "Partie V, ch. 5"),
 ("Germinal/Partie VI/Chapitre 1", "Le sabotage de la mine", "Germinal", "Émile Zola", "Roman", "CM2", "Partie VI, ch. 1"),
 ("Germinal/Partie VII/Chapitre 6", "Le printemps revient", "Germinal", "Émile Zola", "Roman", "CM2", "Partie VII, ch. 6"),

 # ── LITTÉRATURE ÉTRANGÈRE ──
 ("Les Aventures de Tom Sawyer/Traduction Hughes, 1884/1", "Tom et la confiture", "Les Aventures de Tom Sawyer", "Mark Twain", "Roman", "CM1", "ch. 1"),
 ("Les Aventures de Tom Sawyer/Traduction Hughes, 1884/2", "La barrière à repeindre", "Les Aventures de Tom Sawyer", "Mark Twain", "Roman", "CM1", "ch. 2"),
 ("Les Aventures de Tom Sawyer/Traduction Hughes, 1884/13", "Les pirates de l’île Jackson", "Les Aventures de Tom Sawyer", "Mark Twain", "Roman", "CM1", "ch. 13"),
 ("Les Aventures de Tom Sawyer/Traduction Hughes, 1884/18", "Le retour au village", "Les Aventures de Tom Sawyer", "Mark Twain", "Roman", "CM1", "ch. 18"),
 ("Les Aventures de Tom Sawyer/Traduction Hughes, 1884/23", "Le procès de Muff Potter", "Les Aventures de Tom Sawyer", "Mark Twain", "Roman", "CM1", "ch. 23"),
 ("Les Aventures de Tom Sawyer/Traduction Hughes, 1884/31", "Perdus dans la caverne", "Les Aventures de Tom Sawyer", "Mark Twain", "Roman", "CM1", "ch. 31"),

 ("David Copperfield (Traduction Lorain)/Chapitre 1", "Ma naissance", "David Copperfield", "Charles Dickens", "Roman", "CM2", "ch. 1"),
 ("David Copperfield (Traduction Lorain)/Chapitre 5", "Le départ de la maison", "David Copperfield", "Charles Dickens", "Roman", "CM2", "ch. 5"),
 ("David Copperfield (Traduction Lorain)/Chapitre 11", "Le travail à l’entrepôt", "David Copperfield", "Charles Dickens", "Roman", "CM2", "ch. 11"),
 ("David Copperfield (Traduction Lorain)/Chapitre 26", "M. Micawber et Uriah Heep", "David Copperfield", "Charles Dickens", "Roman", "CM2", "ch. 26"),

 ("Alice au pays des merveilles/1", "Dans le terrier du lapin", "Alice au pays des merveilles", "Lewis Carroll", "Conte", "CM1", "ch. 1"),
 ("Alice au pays des merveilles/2", "Le lac de larmes", "Alice au pays des merveilles", "Lewis Carroll", "Conte", "CM1", "ch. 2"),
 ("Alice au pays des merveilles/5", "Le chat du Cheshire", "Alice au pays des merveilles", "Lewis Carroll", "Conte", "CM1", "ch. 5"),
 ("Alice au pays des merveilles/7", "Le thé chez le Chapelier fou", "Alice au pays des merveilles", "Lewis Carroll", "Conte", "CM1", "ch. 7"),
 ("Alice au pays des merveilles/8", "Le jardin de la Reine", "Alice au pays des merveilles", "Lewis Carroll", "Conte", "CM1", "ch. 8"),
 ("Alice au pays des merveilles/12", "Le procès du Valet", "Alice au pays des merveilles", "Lewis Carroll", "Conte", "CM1", "ch. 12"),

 ("Le Livre de la jungle (trad. Fabulet et Humières)/Les Frères de Mowgli", "Les frères de Mowgli", "Le Livre de la jungle", "Rudyard Kipling", "Nouvelle", "CM2", "Les frères de Mowgli"),
 ("Le Livre de la jungle (trad. Fabulet et Humières)/La chasse de Kaa", "La chasse de Kaa", "Le Livre de la jungle", "Rudyard Kipling", "Nouvelle", "CM2", "La chasse de Kaa"),
 ("Le Livre de la jungle (trad. Fabulet et Humières)/« Au tigre, au tigre ! »", "« Au tigre, au tigre ! »", "Le Livre de la jungle", "Rudyard Kipling", "Nouvelle", "CM2", "Au tigre, au tigre !"),
 ("Le Livre de la jungle (trad. Fabulet et Humières)/« Rikki-Tikki-Tavi »", "Rikki-Tikki-Tavi", "Le Livre de la jungle", "Rudyard Kipling", "Nouvelle", "CM2", "Rikki-Tikki-Tavi"),
 ("Le Livre de la jungle (trad. Fabulet et Humières)/Toomai des Éléphants", "Toomai des éléphants", "Le Livre de la jungle", "Rudyard Kipling", "Nouvelle", "CM2", "Toomai des éléphants"),

 ("Les Aventures de Sherlock Holmes/Aventure de la bande mouchetée", "La bande mouchetée", "Les Aventures de Sherlock Holmes", "Arthur Conan Doyle", "Nouvelle", "CM2", "La bande mouchetée"),
 ("Les Aventures de Sherlock Holmes/L’Escarboucle bleue", "L’escarboucle bleue", "Les Aventures de Sherlock Holmes", "Arthur Conan Doyle", "Nouvelle", "CM2", "L’escarboucle bleue"),
 ("Les Aventures de Sherlock Holmes/Les Hêtres pourpres", "Les hêtres pourpres", "Les Aventures de Sherlock Holmes", "Arthur Conan Doyle", "Nouvelle", "CM2", "Les hêtres pourpres"),
 ("Les Aventures de Sherlock Holmes/Le Pouce de l’ingénieur", "Le pouce de l’ingénieur", "Les Aventures de Sherlock Holmes", "Arthur Conan Doyle", "Nouvelle", "CM2", "Le pouce de l’ingénieur"),
]

def call(p, tries=4):
    p.update({"format": "json", "formatversion": "2"})
    u = API + "?" + urllib.parse.urlencode(p)
    for a in range(tries):
        try:
            time.sleep(2.5 + a * 6)
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=35) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                continue
            print("   HTTP", e.code, flush=True)
            return {}
        except Exception as ex:
            print("   ERR", type(ex).__name__, flush=True)
            time.sleep(5)
    return {}

def texte(title):
    d = call({"action": "parse", "page": title, "prop": "text", "redirects": 1})
    h = d.get("parse", {}).get("text", "")
    if len(h) < 700:
        return ""
    h = re.sub(r'<(sup|table|style|script).*?</\1>', ' ', h, flags=re.S)
    out = []
    for p in re.findall(r'<p[^>]*>(.*?)</p>', h, re.S):
        t = html.unescape(re.sub(r'<[^>]+>', '', p)).replace("\u00a0", " ").replace("ſ", "s")
        t = re.sub(r'\s+', ' ', t).strip()
        if len(t) < 110:
            continue
        low = t.lower()
        if any(k in low for k in ("wikisource", "licence", "domaine public", "catégorie",
                                 "texte établi", "imprimerie", "cette édition")):
            continue
        if not re.search(r'[.!?»]', t):
            continue
        out.append(t)
    return " ".join(out)

def cut(txt, n=380):
    w = txt.split()
    s = " ".join(w[:n])
    m = max(s.rfind("."), s.rfind("!"), s.rfind("?"), s.rfind("»"))
    if m > len(s) * 0.55:
        s = s[:m + 1]
    return s

res, echecs = [], []
for i, (page, titre, oeuvre, auteur, genre, niveau, src) in enumerate(PLAN, 1):
    txt = texte(page)
    if len(txt.split()) < 110:
        echecs.append(page)
        print(f"{i:2d}/{len(PLAN)} ECHEC  {page}", flush=True)
        continue
    body = cut(txt)
    res.append({"t": titre, "x": body, "mots": len(body.split()), "src": src,
                "page": page, "oeuvre": oeuvre, "auteur": auteur,
                "genre": genre, "niveau": niveau})
    print(f"{i:2d}/{len(PLAN)} OK {len(body.split()):4d}m  {oeuvre[:26]:28s} | {titre[:32]:34s} | {body[:60]}", flush=True)
    json.dump(res, open("/workspace/lire/batch.json", "w"), ensure_ascii=False, indent=1)

print("\nTOTAL OK:", len(res), "| ECHECS:", len(echecs), echecs, flush=True)
