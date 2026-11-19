#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lot 3 (final) : Germinal complet + littérature étrangère.
Corrections : <sup> conservé (Mme, Mlle), poèmes/épigraphes retirés."""
import json, re, html, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/2.3 (pedagogie; hassanijacques@gmail.com)"}

def page_germinal(n):
    for a, b, p in [(1, 6, "I"), (7, 11, "II"), (12, 16, "III"), (17, 23, "IV"),
                    (24, 29, "V"), (30, 34, "VI"), (35, 40, "VII")]:
        if a <= n <= b:
            return f"Germinal/Partie {p}/Chapitre {n - a + 1}"

GERM = [1, 2, 3, 7, 8, 12, 15, 19, 22, 26, 29, 30, 33, 36, 40]

PLAN = [(page_germinal(n), "GERM", n) for n in GERM]
PLAN += [
 ("David Copperfield (Traduction Lorain)/Chapitre 1", "DC", "Ma naissance"),
 ("David Copperfield (Traduction Lorain)/Chapitre 5", "DC", "Le départ de la maison"),
 ("David Copperfield (Traduction Lorain)/Chapitre 11", "DC", "Le travail à l’entrepôt"),
 ("David Copperfield (Traduction Lorain)/Chapitre 26", "DC", "Uriah Heep et Agnès"),
 ("Alice au pays des merveilles/1", "ALICE", "Dans le terrier du lapin"),
 ("Alice au pays des merveilles/2", "ALICE", "Le lac de larmes"),
 ("Alice au pays des merveilles/5", "ALICE", "La chenille et le chat du Cheshire"),
 ("Alice au pays des merveilles/7", "ALICE", "Le thé chez le Chapelier fou"),
 ("Alice au pays des merveilles/8", "ALICE", "Le jardin de la Reine"),
 ("Alice au pays des merveilles/12", "ALICE", "Le procès du Valet"),
 ("Le Livre de la jungle (trad. Fabulet et Humières)/Les Frères de Mowgli", "JUNGLE", "Les frères de Mowgli"),
 ("Le Livre de la jungle (trad. Fabulet et Humières)/La chasse de Kaa", "JUNGLE", "La chasse de Kaa"),
 ("Le Livre de la jungle (trad. Fabulet et Humières)/« Au tigre, au tigre ! »", "JUNGLE", "« Au tigre, au tigre ! »"),
 ("Le Livre de la jungle (trad. Fabulet et Humières)/« Rikki-Tikki-Tavi »", "JUNGLE", "Rikki-Tikki-Tavi"),
 ("Le Livre de la jungle (trad. Fabulet et Humières)/Toomai des Éléphants", "JUNGLE", "Toomai des éléphants"),
 ("Les Aventures de Sherlock Holmes/Aventure de la bande mouchetée", "SHER", "La bande mouchetée"),
 ("Les Aventures de Sherlock Holmes/L’Escarboucle bleue", "SHER", "L’escarboucle bleue"),
 ("Les Aventures de Sherlock Holmes/Les Hêtres pourpres", "SHER", "Les hêtres pourpres"),
 ("Les Aventures de Sherlock Holmes/Le Pouce de l’ingénieur", "SHER", "Le pouce de l’ingénieur"),
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
    h = re.sub(r'<sup[^>]*>(.*?)</sup>',
               lambda m: re.sub(r'<[^>]+>', '', m.group(1)).lower(), h, flags=re.S)
    h = re.sub(r'<(table|style|script).*?</\1>', ' ', h, flags=re.S)
    # les poèmes / épigraphes sont dans <div class="poem"> : on les retire
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

def cut(txt, n=380):
    w = txt.split()
    s = " ".join(w[:n])
    m = max(s.rfind("."), s.rfind("!"), s.rfind("?"), s.rfind("»"))
    if m > len(s) * 0.55:
        s = s[:m + 1]
    return s

res, echecs = [], []
for i, (page, cle, val) in enumerate(PLAN, 1):
    txt = texte(page)
    if len(txt.split()) < 110:
        echecs.append(page)
        print(f"{i:2d}/{len(PLAN)} ECHEC {page}", flush=True)
        continue
    body = cut(txt)
    res.append({"page": page, "cle": cle, "val": val, "x": body,
                "mots": len(body.split()), "debut": body[:220]})
    print(f"{i:2d}/{len(PLAN)} OK {len(body.split()):4d}m {cle:6s} {str(val):4s} | {body[:70]}", flush=True)
    json.dump(res, open("/workspace/lire/batch3.json", "w"), ensure_ascii=False, indent=1)

print("\nTOTAL OK:", len(res), "| ECHECS:", echecs, flush=True)
