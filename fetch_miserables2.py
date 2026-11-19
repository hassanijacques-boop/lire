#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tomes II à V des Misérables depuis Wikisource (Les Misérables (1908)/Tome N/Livre X/01)."""
import json, re, html, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/2.0 (pedagogie; hassanijacques@gmail.com)"}
TOMES = {2:"Cosette", 3:"Marius", 4:"L’idylle rue Plumet", 5:"Jean Valjean"}
LIVRES = {2:8, 3:8, 4:9, 5:9}

def call(p, tries=3):
    p.update({"format":"json","formatversion":"2"})
    u = API + "?" + urllib.parse.urlencode(p)
    for a in range(tries):
        try:
            time.sleep(3.5 + a*6)
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429: continue
            return {}
        except Exception:
            time.sleep(5)
    return {}

def page(title):
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

def cut(txt, n=370):
    w=txt.split(); s=" ".join(w[:n])
    m=max(s.rfind("."), s.rfind("!"), s.rfind("?"), s.rfind("»"))
    if m > len(s)*0.55: s=s[:m+1]
    return s

moments=[]
for tome, nom in TOMES.items():
    got=0
    for livre in range(1, LIVRES[tome]+1):
        if got >= 5: break
        title = f"Les Misérables (1908)/Tome {tome}/Livre {livre}/01"
        txt = page(title)
        if len(txt.split()) < 120:
            print(f"  - T{tome} L{livre} vide", flush=True)
            continue
        body = cut(txt)
        moments.append({"t": f"Tome {tome} · {nom} — livre {livre}",
                        "x": body, "mots": len(body.split()),
                        "src": f"Les Misérables, tome {tome} ({nom}), livre {livre}"})
        got += 1
        print(f"OK T{tome} L{livre} : {len(body.split())} mots | {body[:60]}", flush=True)
    json.dump(moments, open("/workspace/lire/miserables_ii_v.json","w"), ensure_ascii=False, indent=1)

print("TOTAL", len(moments), "moments")
