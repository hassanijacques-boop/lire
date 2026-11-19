#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Don Quichotte — chapitres choisis (Wikisource, trad. Alaux)."""
import json, re, html, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/2.1 (pedagogie; hassanijacques@gmail.com)"}
BASE1 = "L’Ingénieux Hidalgo Don Quichotte de la Manche/Première partie/Chapitre "
BASE2 = "L’Ingénieux Hidalgo Don Quichotte de la Manche/Deuxième partie/Chapitre "

CHOIX = [
 (BASE1, "I",    "Don Quichotte devient chevalier errant"),
 (BASE1, "II",   "La première sortie"),
 (BASE1, "III",  "L’auberge et l’adoubement"),
 (BASE1, "V",    "Le retour ensanglanté"),
 (BASE1, "VII",  "Sancho Panza, écuyer"),
 (BASE1, "VIII", "Les moulins à vent"),
 (BASE1, "XX",   "Les troupeaux pris pour des armées"),
 (BASE1, "XXII", "Les galériens délivrés"),
 (BASE1, "XXXV", "Le combat contre les outres de vin"),
 (BASE1, "LII",  "La fin de la première partie"),
 (BASE2, "X",    "La fausse Dulcinée"),
 (BASE2, "XXIII", "La caverne de Montésinos"),
 (BASE2, "XLI",  "Le cheval de bois"),
 (BASE2, "LXXIV","La mort de Don Quichotte"),
]

def call(p, tries=3):
    p.update({"format":"json","formatversion":"2"})
    u = API + "?" + urllib.parse.urlencode(p)
    for a in range(tries):
        try:
            time.sleep(3.5 + a*7)
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429: continue
            return {}
        except Exception:
            time.sleep(5)
    return {}

def texte(title):
    d = call({"action":"parse","page":title,"prop":"text","redirects":1})
    h = d.get("parse",{}).get("text","")
    if len(h) < 900: return ""
    h = re.sub(r'<(sup|table|style|script).*?</\1>', ' ', h, flags=re.S)
    out=[]
    for p in re.findall(r'<p[^>]*>(.*?)</p>', h, re.S):
        t = html.unescape(re.sub(r'<[^>]+>','',p)).replace("\u00a0"," ").replace("ſ","s")
        t = re.sub(r'\s+',' ',t).strip()
        if len(t) < 110: continue
        low=t.lower()
        if any(k in low for k in ("wikisource","licence","domaine public","catégorie","texte établi","imprimerie")): continue
        if not re.search(r'[.!?»]', t): continue
        out.append(t)
    return " ".join(out)

def cut(txt, n=380):
    w=txt.split(); s=" ".join(w[:n])
    m=max(s.rfind("."), s.rfind("!"), s.rfind("?"), s.rfind("»"))
    if m > len(s)*0.55: s=s[:m+1]
    return s

moments=[]
for base, rom, titre in CHOIX:
    txt = texte(base + rom)
    if len(txt.split()) < 120:
        print("ECHEC", rom, flush=True); continue
    body = cut(txt)
    partie = "1re partie" if base == BASE1 else "2e partie"
    moments.append({"t": f"{titre} — {partie}", "x": body, "mots": len(body.split()),
                    "src": f"Don Quichotte, {partie}, chapitre {rom}"})
    print(f"OK {rom:5s} {titre[:38]:38s} {len(body.split()):4d} mots | {body[:50]}", flush=True)
    json.dump(moments, open("/workspace/lire/quichotte.json","w"), ensure_ascii=False, indent=1)

print("TOTAL", len(moments))
