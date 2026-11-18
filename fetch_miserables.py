#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrait les chapitres des Misérables (Tome I) depuis texteslibres.fr"""
import re, html, json, time, urllib.request

BASE = "https://www.texteslibres.fr/les-miserables-tome-i-fantine-victor-hugo/"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

# (numéro de chapitre, titre donné au moment)
CHOIX = [
 (14, "L’arrivée de Jean Valjean à Digne"),
 (15, "La porte de l’évêque"),
 (19, "Le réveil de Jean Valjean"),
 (25, "Les chandeliers de l’évêque"),
 (26, "Petit-Gervais, la pièce volée"),
 (27, "L’année 1817 — Fantine"),
 (36, "Une mère qui en rencontre une autre"),
 (38, "L’Alouette — Cosette chez les Thénardier"),
 (40, "Monsieur Madeleine"),
 (46, "Madame Victurnien"),
 (52, "Le repos de Fantine"),
 (56, "Une tempête sous un crâne"),
 (62, "Le procès d’Arras"),
 (66, "Fantine heureuse"),
 (69, "Tombeau convenable"),
]

def get(url):
    for a in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45).read().decode("utf-8","ignore")
        except Exception:
            time.sleep(3)
    return ""

def links():
    h = get(BASE + ".html") or get("https://www.texteslibres.fr/les-miserables-tome-i-fantine-victor-hugo.html")
    ls = re.findall(r'href="(https://www\.texteslibres\.fr/les-miserables-tome-i-fantine-victor-hugo/[^"]+\.html)"[^>]*>(.*?)</a>', h, re.S)
    seen=set(); out={}
    for u,t in ls:
        tt=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',t))).strip()
        m=re.match(r'(\d+)\.', tt)
        if not m or u in seen: continue
        seen.add(u); out[int(m.group(1))]=u
    return out

def chap_text(url):
    p = get(url)
    ps = re.findall(r'<p[^>]*>(.*?)</p>', p, re.S)
    out=[]
    for x in ps:
        t = html.unescape(re.sub(r'<[^>]+>','',x))
        t = re.sub(r'\s+',' ',t).strip()
        if len(t) < 110: continue
        low=t.lower()
        if any(k in low for k in ("texteslibres","tous droits","domaine public","partager","signaler",
                                  "les misérables - tome","victor hugo","navigation","sommaire")): continue
        if not re.search(r'[.!?»]', t): continue
        out.append(t)
    return out

def cut(txt, n=380):
    w = txt.split()
    s = " ".join(w[:n])
    m = max(s.rfind("."), s.rfind("!"), s.rfind("?"), s.rfind("»"))
    if m > len(s)*0.55: s = s[:m+1]
    return s

L = links()
print("chapitres indexés:", len(L), flush=True)
moments=[]
for num, titre in CHOIX:
    url = L.get(num)
    if not url:
        print("absent:", num, flush=True); continue
    ps = chap_text(url)
    if not ps:
        print("vide:", num, flush=True); continue
    body = cut(" ".join(ps), 380)
    moments.append({"t": f"{titre} — chapitre {num}", "x": body, "mots": len(body.split()),
                    "src": "Les Misérables, tome I (Fantine), chapitre "+str(num)})
    print(f"OK {num:2d} {titre[:40]:40s} {len(body.split()):4d} mots", flush=True)

json.dump(moments, open("/workspace/lire/miserables.json","w"), ensure_ascii=False, indent=1)
print("TOTAL", len(moments), "moments")
