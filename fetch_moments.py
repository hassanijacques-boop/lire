#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Récupère plusieurs moments (actes, chapitres, scènes) pour une même œuvre."""
import json, re, html, time, urllib.parse, urllib.request

API = "https://fr.wikisource.org/w/api.php"
UA = {"User-Agent": "LireTube/1.3 (pedagogie; hassanijacques@gmail.com)"}

def call(p, tries=4):
    p.update({"format":"json","formatversion":"2"})
    u = API + "?" + urllib.parse.urlencode(p)
    for a in range(tries):
        try:
            time.sleep(3 + a*8)
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429: continue
            return {}
        except Exception:
            time.sleep(6)
    return {}

def search(q, n=12):
    d = call({"action":"query","list":"search","srsearch":q,"srlimit":n,"srnamespace":0})
    return [x["title"] for x in d.get("query",{}).get("search",[])]

BAD = ("wikisource","licence","domaine public","catégorie","modifier","texte établi",
       "imprimerie","librairie","éditeur","notice","préface","introduction","avant-propos")

def paras(title):
    d = call({"action":"parse","page":title,"prop":"text","redirects":1})
    h = d.get("parse",{}).get("text","")
    if not h or len(h) < 800: return []
    h = re.sub(r'<(sup|table|style|script).*?</\1>', ' ', h, flags=re.S)
    out=[]
    for p in re.findall(r'<p[^>]*>(.*?)</p>', h, re.S):
        t = re.sub(r'<[^>]+>','',p)
        t = html.unescape(t).replace("\u00a0"," ").replace("ſ","s")
        t = re.sub(r'\s+',' ',t).strip()
        if len(t) < 90: continue
        low=t.lower()
        if any(k in low for k in BAD): continue
        if not re.search(r'[.!?»]', t): continue
        out.append(t)
    return out

def num(title):
    m = re.search(r'(?:acte|chapitre|chant|livre|scène)\s*([IVXLC]+|\d+)', title, re.I)
    if not m: return 999
    v = m.group(1)
    if v.isdigit(): return int(v)
    r = {"I":1,"V":5,"X":10,"L":50,"C":100}
    tot=0; prev=0
    for ch in reversed(v):
        val=r.get(ch,0)
        tot = tot-val if val<prev else tot+val
        prev=max(prev,val)
    return tot

# (oeuvre, auteur, genre, niveau, requete de recherche)
OEUVRES = [
 ("Roméo et Juliette","William Shakespeare","Théâtre","CM2","Roméo et Juliette acte"),
 ("Les Misérables","Victor Hugo","Roman","CM2","Les Misérables chapitre"),
 ("Germinal","Émile Zola","Roman","CM2","Germinal chapitre"),
 ("Don Quichotte","Miguel de Cervantès","Roman","CM2","Don Quichotte chapitre"),
 ("Le Tour du monde en 80 jours","Jules Verne","Roman","CM1","Le tour du monde en quatre-vingts jours chapitre"),
 ("Oliver Twist","Charles Dickens","Roman","CM2","Oliver Twist chapitre"),
 ("L'Avare","Molière","Théâtre","CM1","L'Avare acte"),
 ("Candide","Voltaire","Conte","CM2","Candide chapitre"),
]

result = []
for oeuvre, auteur, genre, niv, q in OEUVRES:
    cands = [t for t in search(q) if re.search(r'(acte|chapitre|chant|scène)', t, re.I) and not t.lower().startswith(("auteur","catégorie"))]
    cands = sorted(set(cands), key=num)
    moments=[]
    for title in cands:
        if len(moments) >= 6: break
        ps = paras(title)
        if not ps: continue
        acc,n=[],0
        for p in ps:
            acc.append(p); n+=len(p.split())
            if n>=300: break
        body="\n".join(acc)
        if len(body.split())<90: continue
        label = re.sub(r'^.*?/', '', title)
        label = re.sub(r'\s*\([^)]*\)', '', label)
        moments.append({"t":label[:80], "x":body, "mots":len(body.split()), "src":title})
        print(f"   + {label[:46]:46s} {len(body.split()):4d} mots", flush=True)
    if len(moments)>=2:
        result.append({"oeuvre":oeuvre,"auteur":auteur,"genre":genre,"niveau":niv,"moments":moments})
        print(f"OK {oeuvre} : {len(moments)} moments", flush=True)
    else:
        print(f"ECHEC {oeuvre}", flush=True)
    json.dump(result, open("/workspace/lire/moments.json","w"), ensure_ascii=False, indent=1)

print("TOTAL", len(result), "œuvres")
