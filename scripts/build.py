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
             "gezichtsvorm", "wenkbrauw", "oogkleur", "kleding", "onder", "montuur", "oorbel", "pony", "volume")


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
        u = next((uiterlijk.get(koppeling.get(i, "")) for i in m["ids"] if koppeling.get(i)), None)
        kenm = {k: u.get(k) for k in KENMERKEN} if u else None
        ds = sorted(m["debatten"].values(), key=lambda d: d["punt"]["begin"], reverse=True)
        tot = {k: sum(d[k] for d in ds) for k in ("beurten", "interrupties", "woorden")}
        items = []
        for d in ds:
            punt, strip = d["punt"], d["strip"]
            v = punt["vergadering"]
            kop = (f'<a href="../d/{punt["id"]}.html">{twee(strip["titel"])}</a>' if strip else e(punt["titel"]))
            standpunt = next((x["standpunt"] for x in (strip or {}).get("sprekers", []) if x["id"] in m["ids"]), None)
            citaten = [x["citaat"] for x in (strip or {}).get("strip", []) if x["spreker_id"] in m["ids"]]
            items.append(f"""<li class="item"><div class="meta"><span>{datum(v['datum'])}</span><span class="tag">{e(v['soort'])}</span>
<span>{d['beurten']} keer gesproken{f", {d['interrupties']} interrupties" if d['interrupties'] else ""}</span></div>
<h3>{kop}</h3>{('<p class="note">Agendapunt: ' + e(punt['titel']) + '</p>') if strip else '<p class="note">Nog geen samenvatting voor dit debat.</p>'}
{twee(standpunt, "p") if standpunt else ""}{"".join(f'<blockquote class="quote">“{e(c)}”</blockquote>' for c in citaten)}</li>""")
        wat = sp["fractie"] or sp["functie"]
        body = f"""<main style="display:flex;flex-direction:column;gap:20px">
<div class="person"><svg id="av" viewBox="10 10 80 100" aria-hidden="true"></svg><div style="min-width:0"><h1>{e(naam)}</h1>
<p class="note">{e(sp['functie'])}{(' · ' + e(sp['fractie'])) if sp['fractie'] else ''}</p></div></div>
<div class="stats"><div><b>{len(ds)}</b><span>debatten</span></div><div><b>{tot['beurten']}</b><span>spreekbeurten</span></div>
<div><b>{tot['interrupties']}</b><span>interrupties</span></div><div><b>{f"{tot['woorden']:,}".replace(",", ".")}</b><span>woorden</span></div></div>
<p class="note">Geteld over de verslagen die deze site heeft verwerkt, niet over de hele zittingsperiode.</p>
<h2>Activiteit</h2><ul class="list">{''.join(items)}</ul></main>"""
        data = json.dumps({"id": sorted(m["ids"])[0], "fractie": sp["fractie"], "u": kenm}, ensure_ascii=False)
        js = f'<script src="../strip.js"></script><script>const P={data};document.getElementById("av").innerHTML=character(makeLook(P.id,P.fractie,P.u),"neutraal");</script>'
        (out / f"{slug(naam)}.html").write_text(page(f"{naam} – Wat zei de Kamer?", body, js, root="../"))
        per_partij.setdefault(sp["fractie"] or "Kabinet", []).append((naam, len(ds), tot["beurten"]))
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


def redactie_regel(punt, strip):
    f = ROOT / "data" / "redactie" / f"{punt['id']}.json"
    if not f.exists():
        return '<p class="note">Nog niet nagelezen door de redactie.</p>'
    r = json.loads(f.read_text())
    if r.get("verslag_id") != strip.get("verslag_id"):
        return '<p class="note">Het verslag is bijgewerkt; de redactie leest deze strip opnieuw na.</p>'
    n = len(r.get("bevindingen", []))
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
        return {k: u[k] for k in KENMERKEN if k in u} if u else None
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
                       "emotie": p["emotie"], "citaat": p["citaat"],
                       "tekst": {"normaal": niv(p["tekst"], "normaal"), "makkelijk": niv(p["tekst"], "makkelijk")}})
    status = (f'<span class="tag warn">Voorlopig verslag</span>' if v["status"] in VOORLOPIG
              else '<span class="tag">Gecorrigeerd verslag</span>')
    bron = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag({v['verslag_id']})/resource"
    kaarten = "".join(
        f'<div class="sp"><svg data-avatar="{e(s["id"])}" data-fractie="{e(s["fractie"])}" viewBox="10 10 80 90" aria-hidden="true"></svg>'
        f'<div style="min-width:0"><h3><a href="../p/{slug(s["naam"])}.html">{e(s["naam"])}</a></h3><div class="party">{e(s["fractie"] or s["functie"])}</div>{twee(s["standpunt"], "p")}</div></div>'
        for s in sprekers if not s.get("alleen_strip"))
    kp = strip["kernpunten"]
    kp = kp if isinstance(kp, dict) else {"normaal": kp, "makkelijk": kp}
    lijst = lambda xs: "".join(f"<li>{e(k)}</li>" for k in xs)
    kern = (f'<ul class="points">{lijst(kp["normaal"])}</ul>' if kp["normaal"] == kp["makkelijk"] else
            f'<ul class="points lv-n">{lijst(kp["normaal"])}</ul><ul class="points lv-m">{lijst(kp["makkelijk"])}</ul>')
    woorden = "".join(f'<div class="word"><b>{e(w["woord"])}</b>{e(w["uitleg"])}</div>' for w in strip.get("woorden", []))
    body = f"""<main class="out" style="display:flex;flex-direction:column;gap:20px">
<div class="meta"><span>{datum(v['datum'])}</span><span class="tag">{e(v['soort'])}</span>{status}</div>
<h1>{twee(strip['titel'])}</h1>
<p class="note">Agendapunt: {e(punt['titel'])}</p>
{twee(strip['samenvatting'], "p", "summary")}
<h2>Wie vindt wat?</h2><div class="speakers">{kaarten}</div>
<h2>Belangrijk om te weten</h2>{kern}
{'<h2>Moeilijke woorden</h2><div class="words">' + woorden + '</div>' if woorden else ''}
<h2>De strip</h2><div class="strip" id="strip"><p style="color:#fff;padding:12px">De strip laadt…</p></div>
{redactie_regel(punt, strip)}<p class="note">De strip laat alleen zien wat in het verslag staat. <a href="{e(bron)}">Bekijk het verslag van de Tweede Kamer (XML)</a>.</p>
</main>"""
    data = json.dumps({"sprekers": sprekers, "strip": vakken}, ensure_ascii=False).replace("</", "<\\/")
    scripts = f'<script src="../strip.js"></script><script>window.STRIP={data};renderStrip(window.STRIP);</script>'
    return page(f"{niv(strip['titel'], 'normaal')} – Wat zei de Kamer?", body, scripts, root="../"), sprekers


def index(items):
    partijen = sorted({f for it in items for f in it["fracties"]})
    lijst = "".join(
        f'<li class="item" data-zoek="{e(it["zoek"].lower())}" data-fracties="{e("|".join(it["fracties"]))}">'
        f'<div class="meta"><span>{datum(it["datum"])}</span><span class="tag">{e(it["soort"])}</span>'
        f'{"<span class=\"tag warn\">Voorlopig</span>" if it["voorlopig"] else ""}</div>'
        f'<h3><a href="d/{it["id"]}.html">{twee(it["titel"])}</a></h3>{twee(it["lead"], "p")}'
        f'<div class="chips">{"".join(f"<span class=chip>{e(f)}</span>" for f in it["fracties"])}</div></li>'
        for it in items)
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
        v = punt["vergadering"]
        items.append({
            "id": pid, "titel": strip["titel"] if isinstance(strip["titel"], dict) else {"normaal": strip["titel"]}, "datum": v["datum"], "soort": v["soort"], "begin": punt["begin"],
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
