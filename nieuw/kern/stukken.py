"""Gedeelde HTML-stukken voor de drie varianten: kop met meta en Open Graph, moties en uitslagen, afloopblok,
verslagpagina, woordenlijst, vaste uitleg, "Zo werken we", sitemap en RSS. De varianten bepalen opzet en vorm."""
import html, json, re
from pathlib import Path
from . import model as M

e = html.escape
SITE = "https://watzeidekamer.nl"
NAAM = "Wat zei de Kamer?"
WERKZIN = "Elk debat in gewone taal, met de letterlijke woorden erbij."
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&display=swap">')


# ------------------------------------------------------------------ pagina-kop

def head(titel, beschrijving, pad, root, css, og=None, extra="", type_="website"):
    """<head> met titel, meta description, canonical, Open Graph en Twitter-kaart."""
    url = f"{SITE}/{pad}"
    beeld = f"{SITE}/{og}" if og else f"{SITE}/og/site.png"
    return f"""<!doctype html>
<html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(titel)}</title>
<meta name="description" content="{e(beschrijving)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:site_name" content="{NAAM}"><meta property="og:locale" content="nl_NL">
<meta property="og:type" content="{type_}"><meta property="og:title" content="{e(titel)}">
<meta property="og:description" content="{e(beschrijving)}"><meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e(beeld)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(beschrijving)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="color-scheme" content="light dark">
<link rel="alternate" type="application/rss+xml" title="{NAAM}" href="{root}feed.xml">
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
{FONTS}
<link rel="stylesheet" href="{root}{css}">
{extra}
</head>"""


FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#1d1b2e"/>'
           '<path d="M7 9h18a3 3 0 0 1 3 3v8a3 3 0 0 1-3 3H15l-6 5v-5H7a3 3 0 0 1-3-3v-8a3 3 0 0 1 3-3z" fill="#ffe066"/></svg>')


def beschrijving(d, deel=None):
    """Meta description: de eerste zin van de samenvatting, anders een vaste zin uit titel en datum."""
    x = deel or (d.delen[0] if len(d.delen) == 1 else None)
    if x and x.pagina and x.pagina["samenvatting"]:
        t = x.pagina["samenvatting"].split("\n")[0]
        zin = re.split(r"(?<=[.!?])\s", t)[0]
        return zin[:300]
    return f"{d.soort_label} op {M.datum_lang(d.datum)}: {d.titel_agenda}. Met het letterlijke verslag en de moties."


# ------------------------------------------------------------------ namen en fracties

def fractie_kort(code):
    """'D66 (26 zetels, coalitie)'."""
    f = M.fractie(code)
    if not f:
        return e(code)
    return f"{e(f['code'])} ({f['zetels']} {'zetel' if f['zetels'] == 1 else 'zetels'}, {'coalitie' if f['coalitie'] else 'oppositie'})"


def wie(p, met_fractie=True):
    """Naam met rol: 'Mariëtte Patijn' + 'PRO · 20 zetels · oppositie'."""
    if not p:
        return "", ""
    rol = p.label_fractie() if p.fractie_code else p.functie
    return e(p.naam), e(rol)


def fig(p, cls="fg", alt=True, root=""):
    if p is None:
        return f'<img class="{cls}" src="{root}fig/neutraal.svg" alt="" width="80" height="80">'
    a = f'Getekend figuur van {p.naam}' if alt else ""
    return f'<img class="{cls}" src="{root}{p.fig}" alt="{e(a)}" width="80" height="80" loading="lazy" decoding="async">'


# ------------------------------------------------------------------ vaste uitleg

UITLEG = {
    "motie": ("Motie", "Een verzoek van de Tweede Kamer aan de regering. Wordt een motie aangenomen, dan vraagt de Kamer de regering iets te doen. Het is geen wet en geen besluit van de regering: de regering beslist zelf hoe ze het verzoek uitvoert."),
    "amendement": ("Amendement", "Een voorstel om een wetsvoorstel te veranderen. Wordt een amendement aangenomen, dan verandert de tekst van de wet."),
    "wet": ("Wetsvoorstel", "Een voorstel voor een nieuwe wet of een wijziging van een wet, zoals een begroting of het Belastingplan. De Tweede Kamer stemt erover; daarna stemt de Eerste Kamer. Pas als beide Kamers voor zijn, kan de wet ingaan."),
    "eerste_kamer": ("Eerste Kamer", "Na de Tweede Kamer stemt ook de Eerste Kamer over elk wetsvoorstel. De Eerste Kamer kan een wetsvoorstel aannemen of verwerpen, maar niet veranderen. Over moties van de Tweede Kamer stemt de Eerste Kamer niet."),
    "oordeel": ("Oordeel van het kabinet", "Voor de stemming zegt de minister wat het kabinet van een motie vindt. 'Oordeel Kamer' betekent: het kabinet laat het aan de Kamer over. 'Ontraden' betekent: het kabinet raadt de Kamer aan tegen te stemmen. 'Ontijdig' betekent: het kabinet vindt het te vroeg. Een motie die 'aangehouden' is, komt (nog) niet in stemming."),
    "stemming": ("Stemming", "De Kamer stemt meestal op dinsdag over de moties uit de week ervoor. Elke fractie stemt als geheel; de zetels van een fractie tellen dan allemaal voor of allemaal tegen. Een meerderheid is 76 van de 150 zetels."),
    "coalitie": ("Coalitie en oppositie", "De coalitie zijn de fracties die het kabinet steunen. Nu zijn dat D66, CDA en VVD. De andere fracties zijn de oppositie."),
    "plenair": ("Debat in de plenaire zaal", "Een debat in de grote zaal van de Tweede Kamer, waar alle Kamerleden mogen meedoen en waar ook gestemd wordt."),
    "commissie": ("Commissiedebat en wetgevingsoverleg", "Een debat in een kleinere zaal met de Kamerleden die over een onderwerp gaan. Een wetgevingsoverleg gaat over een wetsvoorstel, bijvoorbeeld een deel van de begroting. Hier wordt niet gestemd; moties uit een wetgevingsoverleg komen later in de plenaire zaal in stemming."),
    "tweeminuten": ("Tweeminutendebat", "Een kort debat na een commissiedebat. Elk Kamerlid heeft twee minuten, vooral om moties in te dienen. De minister zegt daarna wat het kabinet van de moties vindt."),
    "vragenuur": ("Vragenuur", "Elke dinsdag stellen Kamerleden mondelinge vragen aan ministers over actuele onderwerpen. Andere Kamerleden mogen aanvullende vragen stellen. Er worden geen moties ingediend en er wordt niet gestemd."),
    "stemmingen": ("Stemmingen", "Het moment in de plenaire zaal waarop de Kamer stemt over moties, amendementen en wetsvoorstellen. Kamerleden kunnen kort uitleggen waarom ze zo stemmen (een stemverklaring)."),
    "ordedebat": ("Ordedebat", "Een kort debat over de agenda zelf: wat de Kamer wanneer en in welke volgorde bespreekt."),
    "termijn": ("Eerste en tweede termijn", "Een debat heeft meestal twee rondes. In de eerste termijn spreken de Kamerleden en antwoordt het kabinet. In de tweede termijn reageren de Kamerleden nog kort, vaak met moties, en antwoordt het kabinet opnieuw. Daardoor spreekt een minister vaak als laatste: dat volgt uit de vaste orde van een debat, niet uit wie gelijk heeft."),
    "voorlopig": ("Voorlopig verslag", "Het verslag van de Kamer verschijnt eerst als ongecorrigeerde versie. Sprekers kunnen daarna nog kleine verschrijvingen laten verbeteren. Citaten op deze site komen uit de versie die op het moment van bouwen beschikbaar was."),
}


def uitleg_voor(d):
    """Welke vaste uitleg bij dit debat hoort (vaste regel op soort, zaal en moties)."""
    k = []
    if d.is_vragenuur:
        k.append("vragenuur")
    elif d.is_stemmingen:
        k += ["stemmingen", "stemming"]
    elif d.is_tweeminuten:
        k.append("tweeminuten")
    elif d.zaal == "Commissie":
        k.append("commissie")
    else:
        k.append("plenair")
    if any("ordedebat" in x.fase.lower() for x in d.delen):
        k.append("ordedebat")
    if d.moties or d.genoemde_moties:
        k += ["motie", "oordeel"]
    if d.over_wet:
        k += ["wet", "amendement", "eerste_kamer"]
    if len(d.delen) > 1 or d.soort in ("Plenair debat", "Wetgevingsoverleg"):
        k.append("termijn")
    k.append("coalitie")
    if d.voorlopig:
        k.append("voorlopig")
    uit = []
    for x in k:
        if x not in uit:
            uit.append(x)
    return uit


def uitleg_lijst(sleutels, cls="uitleg"):
    return (f'<div class="{cls}">' + "".join(f'<details><summary>{e(UITLEG[s][0])}</summary><p>{e(UITLEG[s][1])}</p></details>' for s in sleutels) + "</div>")


# ------------------------------------------------------------------ moties

def fracties_regel(lijst):
    """'coalitie: D66 (26), VVD (22); oppositie: PVV (19), SP (3)'. Grootste fractie eerst, bij gelijk op naam."""
    co, op, onb = [], [], []
    for c in lijst:
        f = M.fractie(c)
        if not f:
            onb.append(c)
        elif f["coalitie"]:
            co.append(f)
        else:
            op.append(f)
    def fmt(fs):
        return ", ".join(f"{e(f['code'])} ({f['zetels']})" for f in sorted(fs, key=lambda f: (-f["zetels"], f["code"].lower())))
    delen = []
    if co:
        delen.append(f"coalitie: {fmt(co)}")
    if op:
        delen.append(f"oppositie: {fmt(op)}")
    if onb:
        delen.append("onbekend: " + ", ".join(e(x) for x in onb))
    return "; ".join(delen)


def indieners(m):
    uit = []
    for i in m["indieners"]:
        n = re.sub(r"^[A-Z]\.(?:[A-Z]\.)*\s*(?:\(([^)]+)\)\s*)?", lambda k: (k.group(1) + " ") if k.group(1) else "", i["naam"])
        uit.append(f"{e(n)} ({e(i['fractie'])})" if i.get("fractie") else e(n))
    return uit


def motie_status(m):
    u = m.get("uitslag")
    if u and u.get("besluit"):
        return "aangenomen" if u["besluit"].lower().startswith("aangenomen") else "verworpen" if u["besluit"].lower().startswith("verworpen") else u["besluit"].rstrip(".").lower()
    return None


def motie_item(m, root="", met_debat=None, kop="h4"):
    """Eén motie: nummer, indiener, waarover (uit de Kamerdata), oordeel kabinet, uitslag met zetels per fractie."""
    st = motie_status(m)
    ind = indieners(m)
    wie_ = ind[0] + (f" en {len(ind) - 1} {'ander' if len(ind) == 2 else 'anderen'}" if len(ind) > 1 else "")
    over = M.motie_omschrijving(m)
    u = m.get("uitslag") or {}
    uitslag = ""
    if st:
        v, t, afw = M.uitslag_controle(u)
        balk = (f'<div class="balk" role="img" aria-label="{u["zetels_voor"]} zetels voor, {u["zetels_tegen"]} zetels tegen">'
                f'<span class="v" style="flex:{u["zetels_voor"]}"></span><span class="t" style="flex:{u["zetels_tegen"]}"></span><i class="mid"></i></div>')
        uitslag = (f'<p class="uitslag uitslag-{e(st)}"><b>{e(st.capitalize())}</b>: {u["zetels_voor"]} zetels voor, {u["zetels_tegen"]} tegen.</p>{balk}'
                   f'<p class="fr"><b>Voor</b> — {fracties_regel(u.get("voor") or [])}</p>'
                   f'<p class="fr"><b>Tegen</b> — {fracties_regel(u.get("tegen") or [])}</p>'
                   + (f'<p class="afwijking">Let op: de telling wijkt af ({e(afw)}).</p>' if afw else ""))
    oordeel = f'<p class="oordeel">Oordeel van het kabinet: {e(m["oordeel_kabinet"])}</p>' if m.get("oordeel_kabinet") else ""
    verzoek = M.motie_verzoek(m)
    tekst = (f'<details class="motietekst"><summary>Letterlijke tekst van het verzoek</summary><div class="doc">{e(verzoek)}</div>'
             f'<p class="klein"><a href="{e(m["bron"])}" rel="noopener">Hele motie bij de Tweede Kamer</a> (Kamerstuk {e(m["dossier"])}, nr. {e(m["nummer"])})</p></details>') if verzoek else \
        f'<p class="klein"><a href="{e(m["bron"])}" rel="noopener">Hele motie bij de Tweede Kamer</a></p>'
    deb = ""
    if met_debat:
        deb = f'<p class="klein">Ingediend in: <a href="{root}debat/{met_debat.slug}.html">{e(met_debat.titel_agenda)}</a>, {M.datum_lang(met_debat.datum)}</p>'
    return (f'<li class="motie{" m-" + st if st else ""}" id="motie-{e(m["dossier"].replace(" ", ""))}-{e(m["nummer"])}">'
            f'<{kop} class="mkop">Motie {e(m["nummer"])}: {e(over)}</{kop}>'
            f'<p class="mwie">Ingediend door {wie_}</p>{oordeel}{uitslag}{deb}{tekst}</li>')


def moties_telling(ms):
    a = sum(1 for m in ms if motie_status(m) == "aangenomen")
    v = sum(1 for m in ms if motie_status(m) == "verworpen")
    o = len(ms) - a - v
    return a, v, o


def afloop_tekst(d):
    """Korte zin voor 'Hoe liep het af' (zonder verouderende woorden)."""
    if d.is_vragenuur:
        return "Bij een vragenuur worden geen moties ingediend en wordt niet gestemd."
    if d.is_stemmingen:
        return ("In deze vergadering stemde de Kamer over moties, amendementen en wetsvoorstellen. Welke dat waren, kunnen we uit onze "
                "gegevens niet betrouwbaar afleiden; het verslag laat zien wat Kamerleden bij hun stem zeiden. De uitslag van een motie staat bij het debat waarin ze is ingediend.")
    ms = d.moties
    if not ms:
        return "In onze gegevens staan geen moties bij dit debat."
    a, v, o = moties_telling(ms)
    zinnen = [f"In dit debat {'is' if len(ms) == 1 else 'zijn'} {len(ms)} {'motie' if len(ms) == 1 else 'moties'} ingediend."]
    if a or v:
        delen = []
        if a:
            delen.append(f"{a} aangenomen")
        if v:
            delen.append(f"{v} verworpen")
        zinnen.append("Uitslag: " + " en ".join(delen) + ".")
    if o:
        zinnen.append(f"Van {'deze motie' if len(ms) == 1 else str(o) + (' motie' if o == 1 else ' moties')} staat geen uitslag in onze gegevens." if o != len(ms)
                      else ("Van deze motie staat geen uitslag in onze gegevens." if len(ms) == 1 else "Van deze moties staat geen uitslag in onze gegevens."))
    return " ".join(zinnen)


def wet_zin(d):
    if not d.over_wet:
        return ""
    return ("Dit debat ging over een wetsvoorstel. Over het wetsvoorstel zelf en over amendementen stemt de Kamer apart; "
            "die uitslagen staan niet in onze gegevens. Na de Tweede Kamer stemt de Eerste Kamer over het wetsvoorstel.")


def moties_lijst(d, root="", kop="h4"):
    ms = d.moties
    if not ms and not d.genoemde_moties:
        return ""
    if d.is_stemmingen:
        return '<ul class="moties">' + "".join(motie_item(m, root, met_debat=M.motie_debat(m["id"]), kop=kop) for m in d.genoemde_moties) + "</ul>"
    # eerst met uitslag (aangenomen, verworpen), dan zonder; binnen een groep op motienummer
    rang = {"aangenomen": 0, "verworpen": 1}
    ms = sorted(ms, key=lambda m: rang.get(motie_status(m), 2))
    return '<ul class="moties">' + "".join(motie_item(m, root, kop=kop) for m in ms) + "</ul>"


# ------------------------------------------------------------------ woorden en standpunten

def woord_id(w):
    return "w-" + M.slug(w)


def link_woorden(html_, woorden):
    """Moeilijke woorden in lopende tekst worden een link naar hun uitleg op dezelfde pagina."""
    if not woorden:
        return html_
    lijst = sorted(woorden, key=lambda w: -len(w["woord"]))
    pat = re.compile(r"(?<![\w-])(" + "|".join(re.escape(w["woord"]) for w in lijst) + r")(?![\w-])", re.I)
    uitleg = {w["woord"].lower(): w for w in lijst}
    gedaan = set()
    delen, in_a = re.split(r"(<[^>]+>)", html_), False
    for i, x in enumerate(delen):
        if x.startswith("<"):
            if re.match(r"<a[\s>]", x):
                in_a = True
            elif x.startswith("</a"):
                in_a = False
            continue
        if in_a or not x:
            continue
        def vervang(k):
            w = uitleg.get(k.group(1).lower())
            if not w or w["woord"].lower() in gedaan:
                return k.group(0)
            gedaan.add(w["woord"].lower())
            return f'<a class="woordlink" href="#{woord_id(w["woord"])}">{k.group(1)}</a>'
        delen[i] = pat.sub(vervang, x)
    return "".join(delen)


def alineas(t, woorden=None):
    """Samenvatting: alinea's, en regels die met '- ' beginnen als opsomming."""
    regels = [r.strip() for r in (t or "").split("\n") if r.strip()]
    uit, punten = [], []
    for r in regels:
        if r.startswith("- "):
            punten.append(f"<li>{e(r[2:])}</li>")
        else:
            if punten:
                uit.append("<ul>" + "".join(punten) + "</ul>")
                punten = []
            uit.append(f"<p>{e(r)}</p>")
    if punten:
        uit.append("<ul>" + "".join(punten) + "</ul>")
    return link_woorden("".join(uit), woorden)


def woordenlijst(woorden, cls="woorden"):
    if not woorden:
        return ""
    return (f'<dl class="{cls}">' + "".join(f'<div id="{woord_id(w["woord"])}"><dt>{e(w["woord"])}</dt><dd>{e(w["uitleg"])}</dd></div>' for w in woorden) + "</dl>")


def standpunten(x, root="", cls="standpunten"):
    """Standpunten als kaartjes (geen tabel): figuur, naam, fractie met zetels en coalitie/oppositie, standpunt.
    Volgorde: zoals in de paginatekst (de volgorde waarin ze spraken)."""
    if not x.pagina or not x.pagina["sprekers"]:
        return ""
    per = {p.id: p for p in x.personen()}
    kaartjes = []
    for s in x.pagina["sprekers"]:
        p = per.get(s["id"])
        if not p:
            continue
        n, r = wie(p)
        kaartjes.append(f'<li class="sp">{fig(p, "fg", root=root)}<div><p class="spn"><b>{n}</b> <span>{r}</span></p>'
                        f'<p>{link_woorden(e(s["standpunt"]), x.pagina["woorden"])}</p></div></li>')
    return f'<ul class="{cls}">' + "".join(kaartjes) + "</ul>"


def kernpunten(x):
    if not x.pagina or not x.pagina["kernpunten"]:
        return ""
    return "<ul class=\"kern\">" + "".join(f"<li>{link_woorden(e(k), x.pagina['woorden'])}</li>" for k in x.pagina["kernpunten"]) + "</ul>"


def nagelezen(x):
    r = x.redactie
    if not x.pagina:
        return ""
    if not r:
        return '<p class="klein">Tekst geschreven door een AI-model; nog niet nagelezen.</p>'
    if r["zelfde_versie"]:
        return f'<p class="klein">Tekst geschreven door een AI-model en nagelezen op {M.datum_lang(r["datum"])} tegen het verslag.</p>'
    return f'<p class="klein">Tekst geschreven door een AI-model en nagelezen op {M.datum_lang(r["datum"])}, tegen een eerdere versie van het verslag.</p>'


def oud_verslag(x):
    if x.pagina and not x.pagina["actueel"]:
        return '<p class="let">Het verslag is na het schrijven van deze tekst bijgewerkt. De citaten zijn opnieuw gecontroleerd; de samenvatting nog niet.</p>'
    return ""


# ------------------------------------------------------------------ citaten tegen het verslag

def citaat_stukken(c):
    return [s for s in re.split(r"\s*(?:…|\.\.\.)\s*", M.norm(c)) if s]


def citaat_in_beurt(c, beurt_tekst):
    t = M.norm(beurt_tekst)
    return all(s in t for s in citaat_stukken(c))


def citaat_weergave(c):
    """Citaat zoals getoond: met '…' vooraan als het midden in een zin begint."""
    t = c.strip()
    return ("… " if re.match(r"[a-zà-ÿ]", t) else "") + t


# ------------------------------------------------------------------ verslagpagina

def _patroon(stuk):
    """Regex die een genormaliseerd citaatstuk terugvindt in de ruwe tekst (witruimte en aanhalingstekens vrij)."""
    uit = []
    for ch in stuk:
        if ch == " ":
            uit.append(r"\s+")
        elif ch == "'":
            uit.append("['’‘]")
        elif ch == '"':
            uit.append('["“”]')
        else:
            uit.append(re.escape(ch))
    return "".join(uit)


def markeer(tekst_, stukken):
    """HTML van een spreekbeurt met de geciteerde stukken gemarkeerd (<mark>)."""
    spans = []
    for s in stukken:
        k = re.search(_patroon(s), tekst_)
        if k:
            spans.append((k.start(), k.end()))
    spans.sort()
    alineas_ = []
    for a_start, a_tekst in _alineas_met_positie(tekst_):
        delen, pos = [], 0
        for s0, s1 in spans:
            l0, l1 = max(s0 - a_start, 0), min(s1 - a_start, len(a_tekst))
            if l1 <= 0 or l0 >= len(a_tekst) or l0 < pos:
                continue
            delen.append(e(a_tekst[pos:l0]))
            delen.append(f'<mark class="cm">{e(a_tekst[l0:l1])}</mark>')
            pos = l1
        delen.append(e(a_tekst[pos:]))
        if a_tekst.strip():
            alineas_.append("<p>" + "".join(delen) + "</p>")
    return "".join(alineas_)


def _alineas_met_positie(t):
    pos = 0
    for regel in t.split("\n"):
        yield pos, regel
        pos += len(regel) + 1


def verslag_body(x, root, terug_href, terug_tekst, cls=""):
    """De spreekbeurten van één deel, letterlijk, met anker per beurt, tijd, videolink en gemarkeerde citaten."""
    d = x.debat
    v = x.punt["vergadering"]
    citaat_per_beurt = {}
    for dd in [x]:
        if dd.kaart:
            for c in dd.kaart["citaten"]:
                citaat_per_beurt.setdefault(c["beurt"], []).extend(citaat_stukken(c["citaat"]))
    rijen, vorige = [], ""
    for i, b in enumerate(x.beurten):
        p = M.Persoon(b["spreker"])
        tijd_ = M.tijd(b.get("begin"))
        vid = M.video_beurt(x.punt, i)
        labels = []
        if b.get("voorzitter"):
            labels.append('<span class="lbl">voorzitter</span>')
        if b["rol"] == "interrumpant":
            labels.append('<span class="lbl">interruptie</span>')
        if i in citaat_per_beurt:
            labels.append('<span class="lbl lbl-c">geciteerd op deze site</span>')
        rol = "" if b.get("voorzitter") else (f' <span class="rol">{e(p.label_fractie() if p.fractie_code else p.functie)}</span>')
        tekst_html = markeer(b["tekst"], citaat_per_beurt.get(i, []))
        rijen.append(
            f'<article class="beurt{" vz" if b.get("voorzitter") else ""}{" int" if b["rol"] == "interrumpant" else ""}{" gec" if i in citaat_per_beurt else ""}" id="b{i}">'
            f'<header><b>{e(p.naam)}</b>{rol} {"".join(labels)}'
            f'<span class="bt">{f"<time>{tijd_}</time>" if tijd_ else ""}'
            f'{f" <a class=bvid href={e(vid)!r} rel=noopener>Bekijk dit moment (Debat Direct)</a>" if vid else ""}'
            f' <a class="anker" href="#b{i}" aria-label="Link naar spreekbeurt {i}">#</a></span></header>{tekst_html}</article>')
    status = ("Dit is het <b>ongecorrigeerde</b> verslag: sprekers kunnen nog kleine verschrijvingen laten verbeteren."
              if v["status"] in M.VOORLOPIG else "Dit is het gecorrigeerde verslag.")
    bron = M.bron_verslag(x)
    deel_kop = f"Deel {x.nummer} van {x.van}: {e(x.titel)}" if x.van > 1 else ""
    return (f'<main class="verslag {cls}" id="inhoud"><p class="terug"><a href="{terug_href}">← {e(terug_tekst)}</a></p>'
            f'<p class="vmeta">{M.datum_lang(d.datum, dag=True)} · {e(d.soort_label)}{" · <span class=voorl>voorlopig verslag</span>" if v["status"] in M.VOORLOPIG else ""}</p>'
            f'<h1>Verslag: {e(d.titel_agenda)}</h1>{f"<p class=vdeel>{deel_kop}</p>" if deel_kop else ""}'
            f'<div class="vuitleg"><p>Hieronder staan alle spreekbeurten, letterlijk en in volgorde, uit het verslag van de Tweede Kamer. {status}</p>'
            f'<p>Stukken die deze site citeert, zijn <mark class="cm">zo gemarkeerd</mark>. Met “Bekijk dit moment” open je de video van die spreekbeurt in Debat Direct, de videosite van de Tweede Kamer.</p></div>'
            f'<div class="beurten">{"".join(rijen)}</div>'
            f'<p class="klein">Bron: <a href="{e(bron)}" rel="noopener">officieel verslag van de Tweede Kamer</a> ({e(v["titel"])}).</p></main>')


# ------------------------------------------------------------------ afzender en "Zo werken we"

def afzender():
    a = M.lees(M.EIGEN / "afzender.json")
    naam = e(a["naam"]) if a.get("naam") else '<span class="invul">[naam van de maker: nog invullen]</span>'
    if a.get("contact"):
        c = a["contact"]
        href = c if re.match(r"^(https?:|mailto:)", c) else f"mailto:{c}"
        contact = f'<a href="{e(href)}">{e(a.get("contact_label") or c)}</a>'
    else:
        contact = '<span class="invul">[e-mailadres of formulier om een fout te melden: nog invullen]</span>'
    return naam, contact


def figuren_zin():
    from . import figuren as F
    s = F.statistiek()
    return (f"De figuren zijn getekend naar portretten: {s['kamerportret']} naar het officiële portret van de Tweede Kamer en "
            f"{s['ander_portret']} naar een andere foto, omdat er geen Kamerportret is (vooral bewindspersonen). "
            + (f"{s['geen_figuur']} sprekers hebben nog geen goedgekeurd figuur; zij krijgen een neutraal silhouet. " if s["geen_figuur"] else "")
            + "Het zijn tekeningen, geen foto's en geen karikaturen. Iedereen heeft hetzelfde neutrale gezicht.")


def zo_werken_we(variant_regels, root=""):
    """De vaste inhoud van 'Zo werken we'. variant_regels: lijst (kop, [regels]) voor selectie en volgorde in deze variant."""
    naam, contact = afzender()
    F = M.fracties()
    co = F["coalitie"]
    zetels = sorted(F["per"].values(), key=lambda f: (-f["zetels"], f["code"].lower()))
    fr_rijen = "".join(f'<li><b>{e(f["code"])}</b> <span>{e(f["naam"]) if f["naam"] != f["code"] else ""}</span> <span class="z">{f["zetels"]} {"zetel" if f["zetels"] == 1 else "zetels"} · {"coalitie" if f["coalitie"] else "oppositie"}</span></li>' for f in zetels)
    som = sum(f["zetels"] for f in zetels)
    regels_html = "".join(f'<h3>{e(k)}</h3><ul>' + "".join(f"<li>{r}</li>" for r in rs) + "</ul>" for k, rs in variant_regels)
    return f"""
<section id="wie"><h2>Wie maakt dit</h2>
<p>{NAAM} wordt gemaakt door {naam}. Het is geen site van de Tweede Kamer en hoort bij geen enkele partij.</p>
<p>Een fout gezien? Meld het via {contact}. Noem de pagina en wat er niet klopt; we verbeteren het en zetten op de pagina wat er veranderd is.</p></section>
<section id="hoe"><h2>Hoe een pagina ontstaat</h2>
<ul>
<li>Alles komt uit de open data van de Tweede Kamer: de verslagen, de video van Debat Direct, de moties en de stemuitslagen.</li>
<li>De samenvattingen, standpunten, vragen en uitleg van moeilijke woorden zijn geschreven door een AI-model. Een tweede AI-model leest ze daarna na tegen het verslag en verbetert ze. Onder elke tekst staat of en wanneer hij is nagelezen.</li>
<li>Citaten zijn letterlijk. Een script controleert bij het bouwen van de site dat elk getoond citaat woord voor woord in het verslag staat; anders komt het niet op de site. Waar een stuk is weggelaten, staat “…”.</li>
<li>Een letterlijk citaat herken je aan één vaste vorm. Alles wat deze site zelf schrijft, heeft die vorm niet.</li>
<li>Bij elk citaat staat een link naar de spreekbeurt in het verslag, waar het citaat gemarkeerd is, en naar het moment in de video. Ontbreekt de video bij één van de twee citaten, dan staat bij geen van beide een videoknop.</li>
<li>Het bouwen van de site kost geen AI: een script zet de bestaande teksten, citaten en gegevens op hun plek.</li>
<li>{e(figuren_zin())}</li>
</ul></section>
<section id="regels"><h2>Vaste regels voor selectie en volgorde</h2>
<p>Niets op deze site staat ergens omdat een redacteur het belangrijk vond. Elke keuze volgt een vaste regel:</p>
<ul>
<li><b>De vraag bovenaan een debat:</b> één neutrale zin van hooguit twaalf woorden. Hij komt uit de eerste bron die bestaat en past: de mondelinge vraag zelf (bij een vragenuur), de titel of het doel van het wetsvoorstel, het verzoek waarmee het debat werd aangevraagd, de agendatitel, of een vraag die sprekers van minstens drie fracties stelden en waarop een coalitiepartij of het kabinet inging.</li>
<li><b>Welke twee citaten:</b> uit de langste wisseling tussen twee sprekers die op elkaar reageren, tenzij die geen echte tegenstelling heeft of over een bijzaak gaat (minder dan 10% van de spreektijd); dan de volgende. Per spreker hooguit twee zinnen, zonder een voorbehoud weg te laten. Is er geen echte botsing, dan staat er één citaat en zeggen we dat erbij.</li>
<li><b>Volgorde van de twee citaten:</b> wie het eerst sprak, staat eerst. Zo kiest niemand wie het laatste woord krijgt. In een debat antwoordt het kabinet op vragen van de Kamer; daarom staat een minister vaak als tweede.</li>
<li><b>Welke kaart bij een lang debat:</b> lange debatten zijn in delen geknipt langs de rondes van het debat. Bovenaan het debat staat de kaart van het eerste deel waarin twee sprekers tegenover elkaar staan; elk deel heeft daarnaast zijn eigen pagina.</li>
<li><b>Welke debatten een kaart hebben:</b> alleen debatten van meer dan 2.500 gesproken woorden die geen tweeminutendebat, ordedebat of stemming zijn, en elk vragenuur. Andere debatten krijgen een eenvoudiger weergave met de titel en de sprekers.</li>
<li><b>Standpunten:</b> van elke fractie die sprak, in de volgorde waarin ze spraken, met het aantal zetels en of de fractie in de coalitie zit. Zo is te zien hoe groot een fractie is.</li>
<li><b>Moties:</b> een motie staat bij het debat waarin haar eerste indiener sprak. Eerst de aangenomen, dan de verworpen moties, dan die zonder uitslag in onze gegevens; daarbinnen op motienummer. Een uitslag staat er alleen als hij in de open data van de Kamer staat.</li>
<li><b>Fracties bij een stemming:</b> eerst de coalitie, dan de oppositie; daarbinnen de grootste fractie eerst. De zetels tellen we na met de lijst hieronder. Klopt de som niet, of komt hij niet op 150 uit, dan staat dat bij de uitslag.</li>
<li><b>Geen ranglijsten:</b> we tellen niet wie het vaakst of het langst sprak of interrumpeerde. Zulke tellingen zeggen weinig over het werk van een Kamerlid.</li>
</ul>
{regels_html}
</section>
<section id="wat-niet"><h2>Wat deze site (nog) niet laat zien</h2>
<ul>
<li>Alleen de debatten die in onze gegevens staan: plenaire debatten en een deel van de commissiedebatten. Veel werk van de Kamer gebeurt in commissies, schriftelijke vragen en overleg dat niet op deze site staat.</li>
<li>Stemmingen over wetsvoorstellen en amendementen, toezeggingen van ministers en de datum van een stemming staan nog niet in onze gegevens.</li>
<li>Een debat laat vooral zien waar Kamerleden het oneens zijn. De meeste moties worden met een ruime meerderheid aangenomen; kijk daarom ook naar de uitslagen.</li>
</ul></section>
<section id="fracties"><h2>Fracties en zetels</h2>
<p>Zetels volgens de open data van de Tweede Kamer (stand {M.datum_lang(F["stand"])}). Samen {som} zetels{"" if som == 150 else " (let op: niet 150)"}. Welke fracties de coalitie vormen staat niet in die data; dat houden we met de hand bij (stand {M.datum_lang(co["stand"])}): {e(", ".join(co["coalitie"]))}.</p>
<ul class="fractielijst">{fr_rijen}</ul></section>
<section id="begrippen"><h2>Begrippen</h2>{uitleg_lijst(list(UITLEG))}</section>
<section id="bronnen"><h2>Bronnen</h2><ul>
<li>Verslagen, moties en stemuitslagen: <a href="https://opendata.tweedekamer.nl/" rel="noopener">open data van de Tweede Kamer</a>.</li>
<li>Video: <a href="https://debatdirect.tweedekamer.nl/" rel="noopener">Debat Direct</a>, de videosite van de Tweede Kamer.</li>
<li>Deze site is gebouwd op {M.datum_lang(M.gebouwd_op())}.</li></ul></section>"""


# ------------------------------------------------------------------ sitemap en RSS

def sitemap(paden):
    rijen = "".join(f"<url><loc>{e(SITE + '/' + p)}</loc></url>" for p in paden)
    return f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rijen}</urlset>'


def rss(items, variant_naam=""):
    """items: [(titel, pad, beschrijving, iso-datum)] nieuwste eerst."""
    from email.utils import format_datetime
    from datetime import datetime, timezone
    def rfc(iso):
        dt = datetime.fromisoformat(iso[:19]) if len(iso) > 10 else datetime.fromisoformat(iso + "T12:00:00")
        return format_datetime(dt.replace(tzinfo=timezone.utc))
    it = "".join(f"<item><title>{e(t)}</title><link>{e(SITE + '/' + p)}</link><guid>{e(SITE + '/' + p)}</guid>"
                 f"<description>{e(b)}</description><pubDate>{rfc(dt)}</pubDate></item>" for t, p, b, dt in items)
    return (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{NAAM}</title><link>{SITE}/</link>'
            f'<description>{e(WERKZIN)}</description><language>nl</language>{it}</channel></rss>')


ROBOTS = "User-agent: *\nAllow: /\nSitemap: https://watzeidekamer.nl/sitemap.xml\n"


# ------------------------------------------------------------------ deelbeeld

def deelbeeld_html(d, css_vars, fig_root):
    """HTML van het deelbeeld (1200×630) van een debat: de vraag, twee citaten en figuren; anders titel en sprekers."""
    fonts = Path(__file__).resolve().parents[1] / "fonts"
    k = d.kaart
    if k and len(k.kaart["citaten"]) >= 1:
        cits = "".join(
            f'<div class="c"><img src="{fig_root}/{c["persoon"].fig if c["persoon"] else "fig/neutraal.svg"}"><div>'
            f'<p class="q">“{e(kort_citaat(c["citaat"], 150 if len(k.kaart["citaten"]) > 1 else 260))}”</p><p class="n">{e(c["naam"])} · {e(c["partij"] if len(c["partij"]) < 30 else "kabinet")}</p></div></div>'
            for c in k.kaart["citaten"][:2])
        midden = f'<h1>{e(k.kaart["vraag"])}</h1><div class="cits">{cits}</div>'
    else:
        ps = d.personen()[:8]
        figs = "".join(f'<img class="r" src="{fig_root}/{p.fig}">' for p in ps)
        midden = f'<h1>{e(d.titel)}</h1><div class="rij">{figs}</div>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:A;src:url(file://{fonts}/AtkinsonHyperlegible-Regular.ttf)}}
@font-face{{font-family:A;font-weight:700;src:url(file://{fonts}/AtkinsonHyperlegible-Bold.ttf)}}
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{font-family:A,sans-serif;background:{css_vars['bg']};color:#1d1b2e;box-sizing:border-box;padding:44px 56px;display:flex;flex-direction:column;gap:22px}}
.top{{display:flex;justify-content:space-between;font-size:24px;font-weight:700}}
.top span{{font-weight:400}}
h1{{font-size:{56 if len((k.kaart['vraag'] if k else d.titel)) < 70 else 46}px;line-height:1.08;margin:0;max-width:1080px}}
.cits{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:auto}}
.c{{background:#fff;border:3px solid #1d1b2e;border-radius:22px;padding:18px;display:flex;gap:16px;align-items:flex-start}}
.c img{{width:96px;height:96px;border-radius:50%;border:3px solid #1d1b2e;object-fit:cover;object-position:50% 0;background:#fff;flex:none}}
.q{{font-size:24px;line-height:1.25;margin:0}} .n{{font-size:20px;font-weight:700;margin:8px 0 0}}
.rij{{display:flex;gap:14px;margin-top:auto}} .r{{width:110px;height:110px;border-radius:50%;border:3px solid #1d1b2e;object-fit:cover;object-position:50% 0;background:#fff}}
</style></head><body><div class="top"><b>{NAAM}</b><span>{e(d.soort_label)} · {M.datum_lang(d.datum)}</span></div>{midden}</body></html>"""


def kort_citaat(c, n):
    c = citaat_weergave(c)
    if len(c) <= n:
        return c
    return c[:n].rsplit(" ", 1)[0] + " …"


def maak_deelbeelden(uit, debatten_, css_vars, extra=()):
    """Tekent per debat og/<slug>.png met Chromium (kern/schiet.js). Lukt dat niet, dan valt de site terug op og/site.png."""
    import subprocess, tempfile
    uit = Path(uit)
    (uit / "og").mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    taken = []
    for d in debatten_:
        h = tmp / f"{d.slug}.html"
        h.write_text(deelbeeld_html(d, css_vars, f"file://{uit.resolve()}"))
        taken.append({"html": str(h), "png": str((uit / "og" / f"{d.slug}.png").resolve())})
    site = tmp / "site.html"
    site.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:A;src:url(file://{Path(__file__).resolve().parents[1] / 'fonts'}/AtkinsonHyperlegible-Bold.ttf)}}
body{{margin:0;width:1200px;height:630px;background:{css_vars['bg']};font-family:A;display:flex;flex-direction:column;justify-content:center;padding:0 80px;box-sizing:border-box;color:#1d1b2e}}
h1{{font-size:92px;margin:0}} p{{font-size:40px;margin:20px 0 0}}</style></head><body><h1>{NAAM}</h1><p>{WERKZIN}</p></body></html>""")
    taken.append({"html": str(site), "png": str((uit / "og" / "site.png").resolve())})
    taken += list(extra)
    try:
        subprocess.run(["node", str(Path(__file__).with_name("schiet.js"))], input=json.dumps(taken), text=True,
                       check=True, capture_output=True, timeout=600)
        return True
    except Exception as x:  # geen Chromium: geen deelbeeld per debat
        print("deelbeelden overgeslagen:", x)
        return False
