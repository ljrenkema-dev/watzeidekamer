"""Bouw de statische site in public/ uit data/agendapunten en data/strips.

Gebruik: python3 scripts/build.py
Alleen strips die door scripts/check.py komen, worden gepubliceerd.
"""
import html, json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from check import check  # noqa: E402

OUT = ROOT / "public"
MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus",
           "september", "oktober", "november", "december"]
VOORLOPIG = {"Casco", "Ongecorrigeerd"}
e = html.escape


KENMERKEN = ("gezicht", "haarkleur", "kapsel", "bril", "baard", "huid", "leeftijd", "spiegel",
             "gezichtsvorm", "wenkbrauw", "oogkleur", "kleding", "onder", "montuur", "oorbel", "pony", "volume", "slapen")


def niv(x, n):
    """Tekst voor taalniveau n ('normaal' of 'makkelijk'); oude strips hebben één string."""
    if isinstance(x, dict):
        return x.get(n) or x.get("normaal") or x.get("makkelijk") or ""
    return x


def twee(x, tag="span", cls=""):
    """Beide taalniveaus als twee elementen; CSS toont er één."""
    a, b = e(niv(x, "normaal")), e(niv(x, "makkelijk"))
    if a == b:
        return f'<{tag} class="{cls}">{a}</{tag}>'
    return f'<{tag} class="lv-n {cls}">{a}</{tag}><{tag} class="lv-m {cls}">{b}</{tag}>'


def slug(naam):
    import re, unicodedata
    t = unicodedata.normalize("NFKD", naam).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def deel_tag(punt):
    d = punt.get("deel")
    return f'<span class="tag">Deel {d["nummer"]} van {d["van"]}: {e(d["fase"])}</span>' if d else ""


def politici(strips, uiterlijk, koppeling):
    """Pagina per politicus met activiteit uit alle verwerkte agendapunten."""
    mensen = {}
    for f in sorted((ROOT / "data" / "agendapunten").glob("*.json")):
        punt = json.loads(f.read_text())
        strip = strips.get(punt["id"])
        for b in punt["beurten"]:
            if b["voorzitter"]:
                continue
            sp = b["spreker"]
            m = mensen.setdefault(sp["naam"], {"spreker": sp, "ids": set(), "debatten": {}})
            m["ids"].add(sp["id"]); m["spreker"] = sp
            d = m["debatten"].setdefault(punt["id"], {"punt": punt, "strip": strip, "beurten": 0, "interrupties": 0, "woorden": 0})
            d["beurten"] += 1; d["interrupties"] += b["rol"] == "interrumpant"; d["woorden"] += len(b["tekst"].split())
    out = ROOT / "public" / "p"; out.mkdir(parents=True, exist_ok=True)
    per_partij = {}
    for naam, m in mensen.items():
        sp = m["spreker"]
        sl = next((koppeling.get(i) for i in m["ids"] if koppeling.get(i)), None)
        u = uiterlijk.get(sl or "")
        kenm = {k: u.get(k) for k in KENMERKEN} if u else None
        if kenm and manga(sl):
            kenm["manga"] = manga(sl)
            kenm["manga_int"] = manga_int(sl)
        ds = sorted(m["debatten"].values(), key=lambda d: d["punt"]["begin"], reverse=True)
        tot = {k: sum(d[k] for d in ds) for k in ("beurten", "interrupties", "woorden")}
        # een lang debat in delen telt als één debat
        n_debatten = len({(d["punt"].get("deel") or {}).get("ouder_id", d["punt"]["id"]) for d in ds})
        items = []
        for d in ds:
            punt, strip = d["punt"], d["strip"]
            v = punt["vergadering"]
            kop = (f'<a href="../d/{punt["id"]}.html">{twee(strip["titel"])}</a>' if strip else e(punt["titel"]))
            standpunt = next((x["standpunt"] for x in (strip or {}).get("sprekers", []) if x["id"] in m["ids"]), None)
            citaten = [x["citaat"] for x in (strip or {}).get("strip", []) if x["spreker_id"] in m["ids"]]
            items.append(f"""<li class="item"><div class="meta"><span>{datum(v['datum'])}</span><span class="tag">{e(v['soort'])}</span>
{deel_tag(punt)}<span>{d['beurten']} keer gesproken{f", {d['interrupties']} interrupties" if d['interrupties'] else ""}</span></div>
<h3>{kop}</h3>{('<p class="note">Agendapunt: ' + e(punt['titel']) + '</p>') if strip else '<p class="note">Nog geen samenvatting voor dit debat.</p>'}
{twee(standpunt, "p") if standpunt else ""}{"".join(f'<blockquote class="quote">“{e(c)}”</blockquote>' for c in citaten)}</li>""")
        wat = sp["fractie"] or sp["functie"]
        body = f"""<main style="display:flex;flex-direction:column;gap:20px">
<div class="person"><svg id="av" viewBox="10 10 80 100" aria-hidden="true"></svg><div style="min-width:0"><h1>{e(naam)}</h1>
<p class="note">{e(sp['functie'])}{(' · ' + e(sp['fractie'])) if sp['fractie'] else ''}</p></div></div>
<div class="stats"><div><b>{n_debatten}</b><span>debat{"ten" if n_debatten != 1 else ""}</span></div><div><b>{tot['beurten']}</b><span>spreekbeurten</span></div>
<div><b>{tot['interrupties']}</b><span>interrupties</span></div><div><b>{f"{tot['woorden']:,}".replace(",", ".")}</b><span>woorden</span></div></div>
<p class="note">Geteld over de verslagen die deze site heeft verwerkt, niet over de hele zittingsperiode.</p>
<h2>Activiteit</h2><ul class="list">{''.join(items)}</ul></main>"""
        data = json.dumps({"id": sorted(m["ids"])[0], "fractie": sp["fractie"], "u": kenm}, ensure_ascii=False)
        js = f'<script src="../strip.js"></script><script>const P={data};document.getElementById("av").innerHTML=character(makeLook(P.id,P.fractie,P.u),"neutraal");</script>'
        (out / f"{slug(naam)}.html").write_text(page(f"{naam} – Wat zei de Kamer?", body, js, root="../"))
        per_partij.setdefault(sp["fractie"] or "Kabinet", []).append((naam, n_debatten, tot["beurten"]))
    blokken = "".join(
        f'<section><h2>{e(partij)}</h2><ul class="names">' +
        "".join(f'<li><a href="{slug(n)}.html">{e(n)}</a> <span class="note">{d} debat{"ten" if d != 1 else ""}, {b} spreekbeurten</span></li>'
                for n, d, b in sorted(leden, key=lambda x: -x[2])) + "</ul></section>"
        for partij, leden in sorted(per_partij.items(), key=lambda x: (x[0] == "Kabinet", x[0].lower())))
    body = f"""<main style="display:flex;flex-direction:column;gap:20px"><h1>Politici</h1>
<p class="lede">Iedereen die sprak in de debatten op deze site, per partij. Klik op een naam voor het overzicht van zijn of haar activiteit.</p>
<div class="filters"><label for="pq" style="position:absolute;left:-9999px">Zoek een naam</label><input id="pq" type="search" placeholder="Zoek een naam"></div>
<div class="partijen">{blokken}</div></main>"""
    js = """<script>const q=document.getElementById('pq');q.addEventListener('input',()=>{const t=q.value.trim().toLowerCase();
document.querySelectorAll('.names li').forEach(li=>li.hidden=t&&!li.textContent.toLowerCase().includes(t));
document.querySelectorAll('.partijen section').forEach(s=>s.hidden=![...s.querySelectorAll('li')].some(li=>!li.hidden));});</script>"""
    (out / "index.html").write_text(page("Politici – Wat zei de Kamer?", body, js, root="../"))
    return len(mensen)


def is_interruptie(punt, vak):
    """Komt het citaat van dit vak uit een interruptie (rol 'interrumpant' in het verslag)?"""
    from check import norm
    import re as _re
    stuk = _re.split(r"\s*(?:…|\.\.\.)\s*", norm(vak.get("citaat", "")))[0]
    for b in punt["beurten"]:
        if b["spreker"]["id"] == vak.get("spreker_id") and stuk and stuk in norm(b["tekst"]):
            return b["rol"] == "interrumpant"
    return False


def beurt_index(punt, vak):
    """Nummer van de spreekbeurt waaruit het citaat van dit vak komt, of None."""
    from check import norm
    import re as _re
    stuk = _re.split(r"\s*(?:…|\.\.\.)\s*", norm(vak.get("citaat", "")))[0]
    for i, b in enumerate(punt["beurten"]):
        if b["spreker"]["id"] == vak.get("spreker_id") and stuk and stuk in norm(b["tekst"]):
            return i
    return None


def video_link(punt, i):
    """Link naar het moment in Debat Direct waarop spreekbeurt i begint, of None.
    Debat Direct heeft dezelfde id's als de agendapunten; het spreekmoment moet dezelfde persoon hebben
    en hooguit 90 seconden van de begintijd in het verslag afliggen."""
    if i is None:
        return None
    import urllib.parse
    from datetime import datetime
    f = ROOT / "data" / "debatdirect" / f"{punt['id'][:36]}.json"
    if not f.exists():
        return None
    dd = json.loads(f.read_text())
    b = punt["beurten"][i]
    if not b.get("begin"):
        return None
    t = datetime.fromisoformat(b["begin"][:19])
    beste = None
    for m in dd["momenten"]:
        if m["persoon"] != b["spreker"]["id"]:
            continue
        verschil = abs((datetime.fromisoformat(m["start"][:19]) - t).total_seconds())
        if verschil <= 90 and (beste is None or verschil < beste[0]):
            beste = (verschil, m)
    if not beste:
        return None
    m = beste[1]
    return f"{dd['url']}/markeringen?event={urllib.parse.quote(m['soort'] + m['start'], safe='')}"


def video_knop(punt, i):
    url = video_link(punt, i)
    return (f'<a class="video" href="{e(url)}" target="_blank" rel="noopener" '
            f'aria-label="Bekijk dit moment in Debat Direct (opent in een nieuw venster)">▶ video</a>') if url else ""


def verslag_pagina(punt, strip):
    """Leesbare weergave van alle spreekbeurten van dit agendapunt (of deel), met een anker per beurt.
    De tekst komt ongewijzigd uit het verslag; onderaan de link naar de officiële bron."""
    v = punt["vergadering"]
    bron = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag({v['verslag_id']})/resource"
    status = ("Dit is het <b>ongecorrigeerde</b> verslag: sprekers kunnen nog kleine correcties doorgeven."
              if v["status"] in VOORLOPIG else "Dit is het gecorrigeerde verslag.")
    in_strip = {beurt_index(punt, x) for x in strip["strip"] if x.get("spreker_id")}
    rijen, vorige_tijd = [], ""
    for i, b in enumerate(punt["beurten"]):
        sp = b["spreker"]
        naam = sp.get("naam") or sp.get("verslagnaam")
        wat = sp["fractie"] or sp.get("functie", "")
        tijd = (b.get("begin") or "")[11:16]
        tags = []
        if b.get("voorzitter"):
            tags.append('<span class="tag">voorzitter</span>')
        if b["rol"] == "interrumpant":
            tags.append('<span class="tag">interruptie</span>')
        if i in in_strip:
            tags.append('<span class="tag strip-tag">in de strip</span>')
        alineas = "".join(f"<p>{e(a)}</p>" for a in b["tekst"].split("\n") if a.strip())
        kop = (e(naam) if b.get("voorzitter") or not wat
               else f'<a href="../p/{slug(naam)}.html">{e(naam)}</a> <span class="party">({e(wat)})</span>')
        rijen.append(f'<article class="beurt{" vz" if b.get("voorzitter") else ""}{" int" if b["rol"] == "interrumpant" else ""}" id="b{i}">'
                     f'<header><b>{kop}</b> {"".join(tags)}'
                     f'{f"<time>{tijd}</time>" if tijd and tijd != vorige_tijd else ""}'
                     f'{video_knop(punt, i)}'
                     f'<a class="anker" href="#b{i}" aria-label="Link naar deze spreekbeurt">#</a></header>{alineas}</article>')
        vorige_tijd = tijd or vorige_tijd
    body = f"""<main class="out" style="display:flex;flex-direction:column;gap:16px">
<p><a href="../d/{e(punt['id'])}.html">← Terug naar de samenvatting en de strip</a></p>
<div class="meta"><span>{datum(v['datum'])}</span><span class="tag">{e(v['soort'])}</span></div>
<h1>Het hele debat</h1>
<p class="note">Agendapunt: {e(punt['titel'])}</p>{delen_nav(punt)}
<p class="note">Hieronder staan alle spreekbeurten, letterlijk en in volgorde uit het verslag van de Tweede Kamer. {status}
Spreekbeurten die in de strip staan, zijn gemarkeerd.</p>
<div class="verslag">{"".join(rijen)}</div>
<p class="note">Bron: <a href="{e(bron)}">officieel verslag van de Tweede Kamer</a> (XML, {e(v['titel'])}). Met ▶ video bekijk je een spreekbeurt in Debat Direct, de videodienst van de Tweede Kamer.</p>
</main>"""
    return page(f"Het hele debat: {punt['titel']} – Wat zei de Kamer?", body, root="../")


def delen_nav(punt):
    """Bij een lang debat dat in delen is geknipt: welk deel dit is en links naar de andere delen."""
    d = punt.get("deel")
    if not d:
        return ""
    items = []
    for n, pid in enumerate(d.get("ids") or [f"{d['ouder_id']}-d{k}" for k in range(1, d["van"] + 1)], 1):
        af = ROOT / "data" / "agendapunten" / f"{pid}.json"
        fase = json.loads(af.read_text())["deel"]["fase"] if af.exists() else ""
        heeft = (ROOT / "public" / "d" / f"{pid}.html").exists() or (ROOT / "data" / "strips" / f"{pid}.json").exists()
        tekst = f"Deel {n}: {e(fase)}"
        if n == d["nummer"]:
            items.append(f'<li aria-current="page"><b>{tekst}</b></li>')
        elif heeft:
            items.append(f'<li><a href="{pid}.html">{tekst}</a></li>')
        else:
            items.append(f'<li>{tekst} <span class="note">(nog niet samengevat)</span></li>')
    return (f'<nav class="delen" aria-label="Delen van dit debat"><p class="note">Dit lange debat ({d["woorden_totaal"]:,} woorden) '
            f'is in {d["van"]} delen verdeeld. Dit is deel {d["nummer"]}: {e(d["fase"])}'
            f'{(" — " + e(d["sprekers"])) if d["sprekers"] else ""}.</p><ol>{"".join(items)}</ol></nav>').replace(",", ".", 1)


def redactie_regel(punt, strip):
    f = ROOT / "data" / "redactie" / f"{punt['id']}.json"
    if not f.exists():
        return '<p class="note">Nog niet nagelezen door de redactie.</p>'
    r = json.loads(f.read_text())
    if r.get("onafhankelijk") is False:
        return '<p class="note">Nog niet onafhankelijk nagelezen door de redactie.</p>'
    if r.get("verslag_id") != strip.get("verslag_id"):
        return '<p class="note">Het verslag is bijgewerkt; de redactie leest deze strip opnieuw na.</p>'
    if "onafhankelijke_eerste_lezing" in r:  # de eigen controle van de schrijver telt niet mee
        n = sum(len((r.get(k) or {}).get("bevindingen", [])) for k in ("onafhankelijke_eerste_lezing", "onafhankelijke_tweede_lezing"))
    else:
        n = len(r.get("bevindingen", [])) + len((r.get("tweede_lezing") or {}).get("bevindingen", []))
    return f'<p class="note">Nagelezen door de redactie op {datum(r["datum"])}' + (f", {n} correctie{'s' if n != 1 else ''}" if n else "") + '.</p>'


def datum(iso):
    j, m, d = iso[:10].split("-")
    return f"{int(d)} {MAANDEN[int(m) - 1]} {j}"


def page(title, body, scripts="", root=""):
    return f"""<!doctype html>
<html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Zen+Maru+Gothic:wght@700;900&display=swap">
<link rel="stylesheet" href="{root}style.css">
<script>try{{document.documentElement.dataset.taal=localStorage.getItem("taal")||"normaal"}}catch(e){{document.documentElement.dataset.taal="normaal"}}</script>
</head><body><div class="wrap">
<header class="top"><a class="home" href="{root}index.html">Wat zei de <mark>Kamer?</mark></a><nav class="topnav"><a href="{root}p/index.html">Politici</a><button type="button" class="taalknop" id="taalknop" aria-pressed="false">Makkelijke taal</button></nav></header>
{body}
<footer>Gemaakt met open data van de <a href="https://opendata.tweedekamer.nl/">Tweede Kamer</a>. De tekst is door een AI-model in normale taal samengevat. Elk citaat in de strip is automatisch gecontroleerd op het verslag. De figuren zijn getekend naar de officiële portretten van de Tweede Kamer; het zijn geen foto's en geen karikaturen. Geen officiële site van de Tweede Kamer.</footer>
</div>{scripts}<script>
(function(){{const k=document.getElementById("taalknop");
function zet(t){{document.documentElement.dataset.taal=t;k.setAttribute("aria-pressed",t==="makkelijk");k.textContent=t==="makkelijk"?"Normale taal":"Makkelijke taal";
try{{localStorage.setItem("taal",t)}}catch(e){{}};if(window.renderStrip&&window.STRIP)renderStrip(window.STRIP);}}
k.addEventListener("click",()=>zet(document.documentElement.dataset.taal==="makkelijk"?"normaal":"makkelijk"));zet(document.documentElement.dataset.taal);}})();
</script></body></html>"""


def manga(sleutel):
    """Map met goedgekeurde manga-beelden voor deze persoon (site/manga/, gemaakt door manga_site.py), of None."""
    m = (sleutel or "").replace(":", "-")
    return m if m and (ROOT / "site" / "manga" / m / "neutraal.jpg").exists() else None


def manga_int(sleutel):
    m = manga(sleutel)
    return bool(m and (ROOT / "site" / "manga" / m / "interruptie.jpg").exists())


def wie(sp):
    if sp["fractie"]:
        return f"{sp['verslagnaam']} ({sp['fractie']})"
    return f"{sp['verslagnaam']}, {sp['functie']}"


def debat(punt, strip):
    bekend = {b["spreker"]["id"]: b["spreker"] for b in punt["beurten"]}
    v = punt["vergadering"]
    def lees(naam):
        f = ROOT / "data" / naam
        return json.loads(f.read_text()) if f.exists() else {}
    uiterlijk, koppeling = lees("uiterlijk.json"), lees("sprekers.json")
    def kenmerken(sid):
        u = uiterlijk.get(koppeling.get(sid, ""))
        if not u:
            return None
        k_ = {k: u[k] for k in KENMERKEN if k in u}
        if manga(koppeling.get(sid)):
            k_["manga"] = manga(koppeling.get(sid))
            k_["manga_int"] = manga_int(koppeling.get(sid))
        return k_
    gebruikt = [s["id"] for s in strip["sprekers"]] + [p["spreker_id"] for p in strip["strip"] if p["spreker_id"]]
    sprekers = [{"id": s["id"], **bekend[s["id"]], "standpunt": s["standpunt"],
                 "label": bekend[s["id"]]["verslagnaam"], "uiterlijk": kenmerken(s["id"])} for s in strip["sprekers"]]
    for sid in dict.fromkeys(gebruikt):  # sprekers die alleen in de strip staan (bijv. de voorzitter)
        if sid not in {s["id"] for s in sprekers}:
            sprekers.append({"id": sid, **bekend[sid], "standpunt": "", "label": bekend[sid]["verslagnaam"],
                             "uiterlijk": kenmerken(sid), "alleen_strip": True})
    vakken = []
    for p in strip["strip"]:
        sp = bekend.get(p["spreker_id"]) if p["spreker_id"] else None
        vakken.append({"spreker": sp["verslagnaam"] if sp else "Verteller", "wie": wie(sp) if sp else "",
                       "emotie": p["emotie"], "citaat": p["citaat"], "interruptie": is_interruptie(punt, p),
                       "beurt": beurt_index(punt, p) if p["spreker_id"] else None,
                       "video": video_link(punt, beurt_index(punt, p)) if p["spreker_id"] else None,
                       "tekst": {"normaal": niv(p["tekst"], "normaal"), "makkelijk": niv(p["tekst"], "makkelijk")}})
    status = (f'<span class="tag warn">Voorlopig verslag</span>' if v["status"] in VOORLOPIG
              else '<span class="tag">Gecorrigeerd verslag</span>')
    bron = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag({v['verslag_id']})/resource"
    # Standpunten per partij: iedereen uit "sprekers" (één per fractie, plus bewindspersonen)
    standpunten = "".join(
        f'<tr><th scope="row">{e(s["fractie"] or "Kabinet")}</th>'
        f'<td><a href="../p/{slug(s["naam"])}.html">{e(s["naam"])}</a>{"" if s["fractie"] else ", " + e(s["functie"])}</td>'
        f'<td>{twee(s["standpunt"])}</td></tr>'
        for s in sorted((x for x in sprekers if not x.get("alleen_strip")), key=lambda x: (not x["fractie"], x["fractie"].lower())))
    # Kaartjes: de belangrijkste sprekers, standaard 6 en hooguit 9.
    # Eerst wie in de strip staat (in volgorde van het debat), dan wie het meest sprak; bewindspersonen altijd.
    woorden_per = {}
    beurten_per = {}
    for b in punt["beurten"]:
        if not b["voorzitter"]:
            woorden_per[b["spreker"]["id"]] = woorden_per.get(b["spreker"]["id"], 0) + len(b["tekst"].split())
            beurten_per[b["spreker"]["id"]] = beurten_per.get(b["spreker"]["id"], 0) + 1
    in_strip = list(dict.fromkeys(p["spreker_id"] for p in strip["strip"] if p["spreker_id"] and p["spreker_id"] in woorden_per))
    kabinet = [sid for sid in woorden_per if not bekend[sid]["fractie"]]
    rest = sorted(woorden_per, key=lambda sid: -woorden_per[sid])
    gekozen = []
    for sid in in_strip + kabinet + rest:
        if sid not in gekozen and (len(gekozen) < 6 or (sid in in_strip or sid in kabinet) and len(gekozen) < 9):
            gekozen.append(sid)
    per_id = {s["id"]: s for s in sprekers}
    eerste_vak = {}
    for p_ in strip["strip"]:
        if p_["spreker_id"] and p_["spreker_id"] not in eerste_vak:
            eerste_vak[p_["spreker_id"]] = p_
    def kaart(sid):
        sp = per_id.get(sid) or {**bekend[sid], "id": sid}
        n = beurten_per.get(sid, 0)
        vak = eerste_vak.get(sid)
        emo = vak["emotie"] if vak else "neutraal"
        ballon = (f'<div class="ballon">{twee(vak["tekst"])}</div>' if vak else "")
        standpunt = twee(sp["standpunt"], "p", "standpunt") if sp.get("standpunt") else ""
        return (f'<div class="sp kaart" data-kaart="{e(sid)}">{ballon}'
                f'<div class="kaart-body"><svg data-avatar="{e(sid)}" data-fractie="{e(sp["fractie"])}" data-emo="{e(emo)}" viewBox="10 10 80 90" aria-hidden="true"></svg>'
                f'<div style="min-width:0"><h3><a href="../p/{slug(sp["naam"])}.html">{e(sp["naam"])}</a></h3>'
                f'<div class="party">{e(sp["fractie"] or sp["functie"])}</div>{standpunt}'
                f'<p class="note">{n} keer gesproken</p></div></div></div>')
    kaarten = "".join(kaart(sid) for sid in gekozen)
    aantal_partijen = len({x["fractie"] for x in sprekers if x["fractie"] and not x.get("alleen_strip")})
    heeft_kabinet = any(not x["fractie"] and not x.get("alleen_strip") for x in sprekers)
    meer = len(woorden_per) - len(gekozen)
    kaarten_noot = (f'<p class="note">Nog {meer} andere spreker{"s" if meer != 1 else ""} in dit debat; '
                    f'hun partij staat bij “Alle standpunten”.</p>' if meer > 0 else "")
    # figuren voor kaartjes van sprekers die niet in 'sprekers' stonden
    for sid in gekozen:
        if sid not in per_id:
            sprekers.append({"id": sid, **bekend[sid], "standpunt": "", "label": bekend[sid]["verslagnaam"],
                             "uiterlijk": kenmerken(sid), "alleen_strip": True})
    kp = strip["kernpunten"]
    kp = kp if isinstance(kp, dict) else {"normaal": kp, "makkelijk": kp}
    lijst = lambda xs: "".join(f"<li>{e(k)}</li>" for k in xs)
    kern = (f'<ul class="points">{lijst(kp["normaal"])}</ul>' if kp["normaal"] == kp["makkelijk"] else
            f'<ul class="points lv-n">{lijst(kp["normaal"])}</ul><ul class="points lv-m">{lijst(kp["makkelijk"])}</ul>')
    woorden = "".join(f'<div class="word"><b>{e(w["woord"])}</b>{e(w["uitleg"])}</div>' for w in strip.get("woorden", []))
    body = f"""<main class="out" style="display:flex;flex-direction:column;gap:20px">
<div class="meta"><span>{datum(v['datum'])}</span><span class="tag">{e(v['soort'])}</span>{status}</div>
<h1>{twee(strip['titel'])}</h1>
<p class="note">Agendapunt: {e(punt['titel'])}</p>{delen_nav(punt)}
{twee(strip['samenvatting'], "p", "summary")}
<h2>Wie vindt wat?</h2><div class="speakers">{kaarten}</div>{kaarten_noot}
<details class="alle-standpunten"><summary>Alle standpunten ({aantal_partijen} {"partij" if aantal_partijen == 1 else "partijen"}{" en kabinet" if heeft_kabinet else ""})</summary>
<div class="tabelwrap"><table class="standpunten"><thead><tr><th scope="col">Partij</th><th scope="col">Woordvoerder</th><th scope="col">Standpunt</th></tr></thead><tbody>{standpunten}</tbody></table></div></details>
<h2>Belangrijk om te weten</h2>{kern}
{'<h2>Moeilijke woorden</h2><div class="words">' + woorden + '</div>' if woorden else ''}
<h2>De strip</h2><div class="strip" id="strip"><p style="color:#fff;padding:12px">De strip laadt…</p></div>
{redactie_regel(punt, strip)}<p class="note">De strip laat alleen zien wat in het verslag staat. <a href="../v/{e(punt['id'])}.html"><b>Lees het hele debat</b></a>, of bekijk het <a href="{e(bron)}">officiële verslag van de Tweede Kamer</a> (XML).</p>
</main>"""
    data = json.dumps({"sprekers": sprekers, "strip": vakken, "verslag": f"../v/{punt['id']}.html"}, ensure_ascii=False).replace("</", "<\\/")
    scripts = f'<script src="../strip.js"></script><script>window.STRIP={data};renderStrip(window.STRIP);</script>'
    return page(f"{niv(strip['titel'], 'normaal')} – Wat zei de Kamer?", body, scripts, root="../"), sprekers


def groepeer(items):
    """Delen van één lang debat worden één regel in het overzicht, met de delen eronder."""
    uit, groepen = [], {}
    for it in items:
        d = it.get("deel")
        if not d:
            uit.append(it); continue
        g = groepen.get(d["ouder_id"])
        if not g:
            g = groepen[d["ouder_id"]] = {**it, "id": None, "delen": [], "fracties": set(), "zoek": "",
                                          "titel": {"normaal": d["ouder_titel"], "makkelijk": d["ouder_titel"]}}
            uit.append(g)
        g["delen"].append(it)
        g["fracties"] |= set(it["fracties"]); g["zoek"] += " " + it["zoek"]
        g["voorlopig"] = g["voorlopig"] or it["voorlopig"]
    for g in groepen.values():
        g["delen"].sort(key=lambda x: x["deel"]["nummer"])
        g["fracties"] = sorted(g["fracties"])
        eerste = g["delen"][0]
        g["lead"] = {n: f"In {eerste['deel']['van']} delen. " + niv(eerste["lead"], n) for n in ("normaal", "makkelijk")}
    return uit


def item_html(it):
    kop = (f'<a href="d/{it["id"]}.html">{twee(it["titel"])}</a>' if it.get("id") else twee(it["titel"]))
    delen = ""
    if it.get("delen"):
        delen = '<ol class="delenlijst">' + "".join(
            f'<li><a href="d/{x["id"]}.html">Deel {x["deel"]["nummer"]}: {e(x["deel"]["fase"])}</a> — {twee(x["titel"])}</li>'
            for x in it["delen"]) + "</ol>"
    return (f'<li class="item" data-zoek="{e(it["zoek"].lower())}" data-fracties="{e("|".join(it["fracties"]))}">'
            f'<div class="meta"><span>{datum(it["datum"])}</span><span class="tag">{e(it["soort"])}</span>'
            f'{"<span class=\"tag warn\">Voorlopig</span>" if it["voorlopig"] else ""}</div>'
            f'<h3>{kop}</h3>{twee(it["lead"], "p")}{delen}'
            f'<div class="chips">{"".join(f"<span class=chip>{e(f)}</span>" for f in it["fracties"])}</div></li>')


def index(items):
    items = groepeer(items)
    partijen = sorted({f for it in items for f in it["fracties"]})
    lijst = "".join(item_html(it) for it in items)
    opties = "".join(f'<option value="{e(p)}">{e(p)}</option>' for p in partijen)
    body = f"""<main style="display:flex;flex-direction:column;gap:20px">
<h1>Wat zei de <mark>Kamer?</mark></h1>
<p class="lede">Debatten uit de Tweede Kamer in normale taal, met een strip. Elk plaatje laat zien wat er echt gezegd is.</p>
<div class="filters"><label for="q" class="visually-hidden" style="position:absolute;left:-9999px">Zoeken</label>
<input id="q" type="search" placeholder="Zoek op onderwerp of naam, bijvoorbeeld 'belasting'">
<label for="partij" style="position:absolute;left:-9999px">Partij</label>
<select id="partij"><option value="">Alle partijen</option>{opties}</select></div>
<p class="note" id="telling"></p>
<ul class="list" id="lijst">{lijst}</ul>
</main>"""
    js = """<script>
const q=document.getElementById('q'),p=document.getElementById('partij'),items=[...document.querySelectorAll('#lijst .item')];
function f(){const t=q.value.trim().toLowerCase();let n=0;for(const it of items){const ok=(!t||it.dataset.zoek.includes(t))&&(!p.value||it.dataset.fracties.split('|').includes(p.value));it.hidden=!ok;n+=ok;}
document.getElementById('telling').textContent=n+' debat'+(n===1?'':'ten');}
q.addEventListener('input',f);p.addEventListener('change',f);f();
</script>"""
    return page("Wat zei de Kamer?", body, js)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "d").mkdir(parents=True)
    for f in ("style.css", "strip.js"):
        shutil.copy(ROOT / "site" / f, OUT / f)
    if (ROOT / "site" / "manga").exists():
        shutil.copytree(ROOT / "site" / "manga", OUT / "manga")
    items = []
    for sf in sorted((ROOT / "data" / "strips").glob("*.json")):
        pid = sf.stem
        if json.loads(sf.read_text()).get("ingetrokken"):
            print(f"ingetrokken {pid}: {json.loads(sf.read_text()).get('reden', '')}")
            continue
        fouten, _ = check(pid)
        if fouten:
            print(f"overgeslagen {pid}: {len(fouten)} fout(en)")
            continue
        punt = json.loads((ROOT / "data" / "agendapunten" / f"{pid}.json").read_text())
        strip = json.loads(sf.read_text())
        html_, sprekers = debat(punt, strip)
        (OUT / "d" / f"{pid}.html").write_text(html_)
        (OUT / "v").mkdir(exist_ok=True)
        (OUT / "v" / f"{pid}.html").write_text(verslag_pagina(punt, strip))
        v = punt["vergadering"]
        items.append({
            "id": pid, "deel": punt.get("deel"), "titel": strip["titel"] if isinstance(strip["titel"], dict) else {"normaal": strip["titel"]}, "datum": v["datum"], "soort": v["soort"], "begin": punt["begin"],
            "voorlopig": v["status"] in VOORLOPIG, "lead": {n: niv(strip["samenvatting"], n).split(". ")[0].rstrip(".") + "." for n in ("normaal", "makkelijk")},
            "fracties": sorted({s["fractie"] for s in sprekers if s["fractie"]}),
            "zoek": " ".join([niv(strip["titel"], "normaal"), niv(strip["titel"], "makkelijk"), punt["titel"],
                              niv(strip["samenvatting"], "normaal"), niv(strip["samenvatting"], "makkelijk"),
                              *[k for v in (strip["kernpunten"].values() if isinstance(strip["kernpunten"], dict) else [strip["kernpunten"]]) for k in v],
                              *[s["naam"] + " " + s["fractie"] for s in sprekers]]),
        })
    items.sort(key=lambda x: x["begin"], reverse=True)
    goed = {i["id"]: json.loads((ROOT / "data" / "strips" / f"{i['id']}.json").read_text()) for i in items}
    def lees(naam):
        f = ROOT / "data" / naam
        return json.loads(f.read_text()) if f.exists() else {}
    n = politici(goed, lees("uiterlijk.json"), lees("sprekers.json"))
    print(f"{n} politicuspagina's")
    (OUT / "index.html").write_text(index(items))
    print(f"{len(items)} debatten gepubliceerd in public/")


if __name__ == "__main__":
    main()
