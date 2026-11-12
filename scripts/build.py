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
</head><body><div class="wrap">
<header class="top"><a class="home" href="{root}index.html">Wat zei de <mark>Kamer?</mark></a><span class="note">Tweede Kamer in makkelijke taal</span></header>
{body}
<footer>Gemaakt met open data van de <a href="https://opendata.tweedekamer.nl/">Tweede Kamer</a>. De tekst is door een AI-model in makkelijke taal gezet. Elk citaat in de strip is automatisch gecontroleerd op het verslag. De figuren zijn getekend naar de officiële portretten van de Tweede Kamer; het zijn geen foto's en geen karikaturen. Geen officiële site van de Tweede Kamer.</footer>
</div>{scripts}</body></html>"""


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
        return {k: u.get(k) for k in ("gezicht", "haarkleur", "kapsel", "bril", "baard", "huid", "leeftijd", "spiegel")} if u else None
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
                       "emotie": p["emotie"], "tekst": p["tekst"], "citaat": p["citaat"]})
    status = (f'<span class="tag warn">Voorlopig verslag</span>' if v["status"] in VOORLOPIG
              else '<span class="tag">Gecorrigeerd verslag</span>')
    bron = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag({v['verslag_id']})/resource"
    kaarten = "".join(
        f'<div class="sp"><svg data-avatar="{e(s["id"])}" data-fractie="{e(s["fractie"])}" viewBox="10 10 80 90" aria-hidden="true"></svg>'
        f'<div style="min-width:0"><h3>{e(s["naam"])}</h3><div class="party">{e(s["fractie"] or s["functie"])}</div><p>{e(s["standpunt"])}</p></div></div>'
        for s in sprekers if not s.get("alleen_strip"))
    woorden = "".join(f'<div class="word"><b>{e(w["woord"])}</b>{e(w["uitleg"])}</div>' for w in strip.get("woorden", []))
    body = f"""<main class="out" style="display:flex;flex-direction:column;gap:20px">
<div class="meta"><span>{datum(v['datum'])}</span><span class="tag">{e(v['soort'])}</span>{status}</div>
<h1>{e(strip['titel'])}</h1>
<p class="note">Agendapunt: {e(punt['titel'])}</p>
<p class="summary">{e(strip['samenvatting'])}</p>
<h2>Wie vindt wat?</h2><div class="speakers">{kaarten}</div>
<h2>Belangrijk om te weten</h2><ul class="points">{''.join(f'<li>{e(k)}</li>' for k in strip['kernpunten'])}</ul>
{'<h2>Moeilijke woorden</h2><div class="words">' + woorden + '</div>' if woorden else ''}
<h2>De strip</h2><div class="strip" id="strip"><p style="color:#fff;padding:12px">De strip laadt…</p></div>
<p class="note">De strip laat alleen zien wat in het verslag staat. <a href="{e(bron)}">Bekijk het verslag van de Tweede Kamer (XML)</a>.</p>
</main>"""
    data = json.dumps({"sprekers": sprekers, "strip": vakken}, ensure_ascii=False).replace("</", "<\\/")
    scripts = f'<script src="../strip.js"></script><script>renderStrip({data});</script>'
    return page(f"{strip['titel']} – Wat zei de Kamer?", body, scripts, root="../"), sprekers


def index(items):
    partijen = sorted({f for it in items for f in it["fracties"]})
    lijst = "".join(
        f'<li class="item" data-zoek="{e(it["zoek"].lower())}" data-fracties="{e("|".join(it["fracties"]))}">'
        f'<div class="meta"><span>{datum(it["datum"])}</span><span class="tag">{e(it["soort"])}</span>'
        f'{"<span class=\"tag warn\">Voorlopig</span>" if it["voorlopig"] else ""}</div>'
        f'<h3><a href="d/{it["id"]}.html">{e(it["titel"])}</a></h3><p>{e(it["lead"])}</p>'
        f'<div class="chips">{"".join(f"<span class=chip>{e(f)}</span>" for f in it["fracties"])}</div></li>'
        for it in items)
    opties = "".join(f'<option value="{e(p)}">{e(p)}</option>' for p in partijen)
    body = f"""<main style="display:flex;flex-direction:column;gap:20px">
<h1>Wat zei de <mark>Kamer?</mark></h1>
<p class="lede">Debatten uit de Tweede Kamer in makkelijke taal, met een strip. Elk plaatje laat zien wat er echt gezegd is.</p>
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
            "id": pid, "titel": strip["titel"], "datum": v["datum"], "soort": v["soort"], "begin": punt["begin"],
            "voorlopig": v["status"] in VOORLOPIG, "lead": strip["samenvatting"].split(". ")[0].rstrip(".") + ".",
            "fracties": sorted({s["fractie"] for s in sprekers if s["fractie"]}),
            "zoek": " ".join([strip["titel"], punt["titel"], strip["samenvatting"], *strip["kernpunten"],
                              *[s["naam"] + " " + s["fractie"] for s in sprekers]]),
        })
    items.sort(key=lambda x: x["begin"], reverse=True)
    (OUT / "index.html").write_text(index(items))
    print(f"{len(items)} debatten gepubliceerd in public/")


if __name__ == "__main__":
    main()
