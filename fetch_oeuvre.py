#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Découpe une œuvre TextesLibres en moments répartis sur l'arc narratif."""
import re, html, json, time, sys, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

def get(url):
    for _ in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45).read().decode("utf-8","ignore")
        except Exception:
            time.sleep(3)
    return ""

def chapitres(base):
    h = get(base)
    slug = base.rstrip("/").split("/")[-1].replace(".html","")
    ls = re.findall(r'href="(https://www\.texteslibres\.fr/'+re.escape(slug)+r'/[^"]+\.html)"[^>]*>(.*?)</a>', h, re.S)
    seen=set(); out=[]
    for u,t in ls:
        tt = html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',t))).strip()
        if u in seen or len(tt)<3: continue
        seen.add(u); out.append((tt,u))
    # dédoublonner en gardant l'ordre d'apparition
    return out

def texte(url):
    p = get(url)
    ps = re.findall(r'<p[^>]*>(.*?)</p>', p, re.S)
    out=[]
    for x in ps:
        t = html.unescape(re.sub(r'<[^>]+>','',x))
        t = re.sub(r'\s+',' ',t).strip()
        if len(t) < 110: continue
        low=t.lower()
        if any(k in low for k in ("texteslibres","tous droits","domaine public","partager","signaler",
                                  "navigation","sommaire","table des matières")): continue
        if not re.search(r'[.!?»]', t): continue
        out.append(t)
    return " ".join(out)

def cut(txt, n=370):
    w=txt.split(); s=" ".join(w[:n])
    m=max(s.rfind("."), s.rfind("!"), s.rfind("?"), s.rfind("»"))
    if m > len(s)*0.55: s=s[:m+1]
    return s

def build(url, oeuvre, auteur, genre, niveau, nb=12):
    ch = chapitres(url)
    print(f"{oeuvre}: {len(ch)} chapitres", flush=True)
    if len(ch) < nb: nb = len(ch)
    # indices répartis (on évite les 2 premiers = souvent préface)
    idxs = sorted({int(round(i*(len(ch)-1)/(nb-1))) for i in range(nb)}) if nb>1 else [len(ch)//2]
    moments=[]
    for i in idxs:
        titre, u = ch[i]
        txt = texte(u)
        if len(txt.split()) < 100:
            print("   vide:", titre[:40], flush=True); continue
        body = cut(txt, 370)
        moments.append({"t": titre[:90], "x": body, "mots": len(body.split()), "src": titre[:90]})
        print(f"   + {titre[:52]:52s} {len(body.split()):4d} mots", flush=True)
    return {"oeuvre":oeuvre,"auteur":auteur,"genre":genre,"niveau":niveau,"moments":moments}

if __name__ == "__main__":
    CIBLES = [
      ("https://www.texteslibres.fr/vingt-mille-lieues-sous-les-mers-jules-verne.html",
       "Vingt Mille Lieues sous les mers","Jules Verne","Roman","CM2",12),
      ("https://www.texteslibres.fr/notre-dame-de-paris-victor-hugo.html",
       "Notre-Dame de Paris","Victor Hugo","Roman","CM2",12),
      ("https://www.texteslibres.fr/le-comte-de-monte-cristo-alexandre-dumas.html",
       "Le Comte de Monte-Cristo","Alexandre Dumas","Roman","CM2",12),
    ]
    out=[]
    for url, o, a, g, n, k in CIBLES:
        try:
            r = build(url, o, a, g, n, k)
            if r["moments"]: out.append(r)
        except Exception as e:
            print("ERREUR", o, e, flush=True)
        json.dump(out, open("/workspace/lire/oeuvres_new.json","w"), ensure_ascii=False, indent=1)
    print("TOTAL", len(out), "œuvres,", sum(len(x["moments"]) for x in out), "moments")
