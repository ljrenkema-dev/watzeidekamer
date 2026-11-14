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
        if len(zin) > 300:
            zin = zin[:297].rsplit(" ", 1)[0].rstrip(",;:(") + " …"
        return zin
    return f"{d.soort_label} op {M.datum_lang(d.datum)}: {d.titel_agenda}. Met het letterlijke verslag" + (" en de moties." if d.moties else ".")


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


def fig(p, cls="fg", alt=False, root="", lui=True):
    """Figuur van een spreker. alt is leeg als de naam ernaast staat (anders wordt hij dubbel voorgelezen)."""
    if p is None:
        return f'<img class="{cls}" src="{root}fig/neutraal.svg" alt="" width="80" height="80">'
    a = f'Getekend figuur van {p.naam}' if alt else ""
    return f'<img class="{cls}" src="{root}{p.fig}" alt="{e(a)}" width="180" height="240"{" loading=lazy" if lui else ""} decoding="async">'


# ------------------------------------------------------------------ vaste uitleg

UITLEG = {
    "motie": ("Motie", "Een verzoek van de Tweede Kamer aan de regering. Wordt een motie aangenomen, dan vraagt de Kamer de regering iets te doen. Het is geen wet en geen besluit van de regering: de regering beslist zelf óf en hoe ze het verzoek uitvoert. Meestal voert ze een aangenomen motie uit; doet ze dat niet, dan moet ze dat aan de Kamer uitleggen. Een motie van wantrouwen is een bijzondere motie: de Kamer zegt daarmee het vertrouwen in een minister of het kabinet op."),
    "amendement": ("Amendement", "Een voorstel om een wetsvoorstel te veranderen. Wordt een amendement aangenomen, dan verandert de tekst van het wetsvoorstel."),
    "wet": ("Wetsvoorstel", "Een voorstel voor een nieuwe wet of een wijziging van een wet, zoals een begroting of het Belastingplan. De Tweede Kamer stemt erover; daarna stemt de Eerste Kamer. Pas als beide Kamers voor zijn, kan de wet ingaan."),
    "novelle": ("Novelle", "Een wijziging van een wetsvoorstel dat de Tweede Kamer al heeft aangenomen en dat bij de Eerste Kamer ligt. De Tweede Kamer moet zo'n wijziging eerst zelf behandelen en erover stemmen."),
    "eerste_kamer": ("Eerste Kamer", "Na de Tweede Kamer stemt ook de Eerste Kamer over elk wetsvoorstel. De Eerste Kamer kan een wetsvoorstel aannemen of verwerpen, maar niet veranderen. Over moties van de Tweede Kamer stemt de Eerste Kamer niet."),
    "oordeel": ("Oordeel van het kabinet", "Voor de stemming zegt de minister wat het kabinet van een motie vindt. 'Oordeel Kamer' betekent: het kabinet laat het aan de Kamer over. 'Ontraden' betekent: het kabinet raadt de Kamer aan tegen te stemmen. 'Ontijdig' betekent: het kabinet vindt het te vroeg. Soms noemt het kabinet een motie 'overbodig', omdat het gevraagde al gebeurt. Een indiener kan een motie ook 'aanhouden': dan komt ze voorlopig niet in stemming."),
    "stemming": ("Stemming", "De Kamer stemt meestal op dinsdag over de moties uit de week ervoor. Meestal stemt een fractie als geheel en tellen al haar zetels voor of tegen; een Kamerlid kan afwijken, maar onze gegevens tonen alleen de stem per fractie. Een motie is aangenomen als meer dan de helft van de uitgebrachte stemmen voor is; als iedereen meestemt, is dat 76 van de 150."),
    "coalitie": ("Coalitie en oppositie", ""),  # tekst: coalitie_uitleg()
    "plenair": ("Debat in de plenaire zaal", "Een debat in de grote zaal van de Tweede Kamer, waar alle Kamerleden mogen meedoen en waar ook gestemd wordt."),
    "commissie": ("Commissiedebat en wetgevingsoverleg", "Een debat in een kleinere zaal met de Kamerleden die over een onderwerp gaan. Een wetgevingsoverleg gaat over een wetsvoorstel, bijvoorbeeld een deel van de begroting. Hier wordt niet gestemd; moties uit een wetgevingsoverleg komen later in de plenaire zaal in stemming."),
    "tweeminuten": ("Tweeminutendebat", "Een kort debat na een commissiedebat. Elk Kamerlid heeft twee minuten, vooral om moties in te dienen. De minister zegt daarna wat het kabinet van de moties vindt."),
    "vragenuur": ("Vragenuur", "Elke dinsdag stellen Kamerleden mondelinge vragen aan ministers over actuele onderwerpen. Andere Kamerleden mogen aanvullende vragen stellen. Er worden geen moties ingediend en er wordt niet gestemd."),
    "stemmingen": ("Stemmingen", "Het moment in de plenaire zaal waarop de Kamer stemt over moties, amendementen en wetsvoorstellen. Kamerleden kunnen kort uitleggen waarom ze zo stemmen (een stemverklaring)."),
    "ordedebat": ("Ordedebat", "Een kort debat over de agenda zelf: wat de Kamer wanneer en in welke volgorde bespreekt."),
    "termijn": ("Eerste en tweede termijn", "Een debat heeft meestal twee rondes. In de eerste termijn spreken de Kamerleden en antwoordt het kabinet. In de tweede termijn reageren de Kamerleden kort, vaak met moties, en antwoordt het kabinet opnieuw. Soms volgt later een derde termijn, bijvoorbeeld als er iets nieuws is, zoals een amendement. Daardoor spreekt een minister vaak als laatste: dat volgt uit de vaste orde van een debat, niet uit wie gelijk heeft."),
    "voorlopig": ("Voorlopig verslag", "Het verslag van de Kamer verschijnt eerst als ongecorrigeerde versie. Sprekers kunnen daarna kleine verschrijvingen laten verbeteren. Citaten op deze site komen uit de versie die op het moment van bouwen beschikbaar was."),
}


def coalitie_uitleg():
    F = M.fracties()
    co = F["coalitie"]["coalitie"]
    z = F["coalitie_zetels"]
    t = (f"De coalitie zijn de fracties die het kabinet steunen. Op {M.datum_lang(F['coalitie']['stand'])} zijn dat {', '.join(co[:-1])} en {co[-1]}, "
         f"samen {z} van de {F['totaal']} zetels. De andere fracties heten oppositie.")
    if z < 76:
        t += (" Omdat de coalitie geen 76 zetels heeft, is dit een minderheidskabinet: voor een meerderheid zijn bij elke stemming ook stemmen "
              "van andere fracties nodig. Daarom verschilt de meerderheid per stemming; bij elke uitslag staat welke fracties voor stemden.")
    return t


UITLEG["coalitie"] = ("Coalitie en oppositie", coalitie_uitleg())


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
        if "novelle" in d.titel_agenda.lower():
            k.append("novelle")
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
    """'D66 (26, coalitie), PVV (19), VVD (22, coalitie)': grootste fractie eerst, bij gelijk op naam; de coalitie gemarkeerd."""
    fs, onb = [], []
    for c in lijst:
        f = M.fractie(c)
        (fs.append(f) if f else onb.append(c))
    uit = [f"{e(f['code'])} ({f['zetels']}{', coalitie' if f['coalitie'] else ''})" for f in sorted(fs, key=lambda f: (-f["zetels"], f["code"].lower()))]
    return ", ".join(uit + [e(x) + " (onbekend)" for x in onb])


def indieners(m):
    uit = []
    for i in m["indieners"]:
        n = re.sub(r"^(?:[A-Z][a-z]?\.)+\s*(?:\(([^)]+)\)\s*)?", lambda k: (k.group(1) + " ") if k.group(1) else "", i["naam"])
        if n[:1].islower():
            n = n[0].upper() + n[1:]  # 'van Baarle' zonder voornaam wordt 'Van Baarle'
        f = M.fractie(i.get("fractie") or "")
        fr = (f["code"] + (", coalitie" if f["coalitie"] else "")) if f else (i.get("fractie") or "")
        uit.append(f"{e(n)} ({e(fr)})" if fr else e(n))
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
    wie_ = ind[0] if len(ind) == 1 else ", ".join(ind[:-1]) + " en " + ind[-1]
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
    ok = m.get("oordeel_kabinet")
    if ok and ok.lower() == "aangehouden":
        oordeel = '<p class="oordeel"><b>Aangehouden</b> door de indiener: komt voorlopig niet in stemming. Oordeel van het kabinet: niet in onze gegevens.</p>'
    else:
        oordeel = f'<p class="oordeel">Oordeel van het kabinet: {e(ok) if ok else "niet in onze gegevens"}</p>'
    if M.motie_wantrouwen(m):
        oordeel = '<p class="oordeel"><b>Motie van wantrouwen</b></p>' + oordeel
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
    """Korte zin over de moties (zonder verouderende woorden). Bij een wetsvoorstel staat wet_zin() ervoor."""
    if d.is_vragenuur:
        return "Bij een vragenuur worden geen moties ingediend en wordt niet gestemd."
    if d.is_stemmingen:
        return ("In deze vergadering stemde de Kamer. De uitslagen staan niet in onze gegevens; lees in het verslag wat er gezegd is. "
                "De uitslag van een motie staat, als we die hebben, bij het debat waarin ze is ingediend.")
    ms = d.moties
    if not ms:
        return "In onze gegevens staan geen moties bij dit debat."
    a, v, o = moties_telling(ms)
    n = len(ms)
    zinnen = [f"{n} {'motie' if n == 1 else 'moties'} (verzoeken aan de regering)."]
    if a or v:
        delen = ([f"{a} aangenomen"] if a else []) + ([f"{v} verworpen"] if v else [])
        zinnen.append("Uitslag: " + " en ".join(delen) + ".")
    if o:
        zinnen.append("Van deze motie staat geen uitslag in onze gegevens." if n == 1 else
                      ("Van deze moties staat geen uitslag in onze gegevens." if o == n else f"Van {o} staat geen uitslag in onze gegevens."))
    return " ".join(zinnen)


def wet_zin(d):
    """Bij een wetsvoorstel: wat er met de wet zelf gebeurt (vaste tekst; de uitslag staat niet in onze gegevens)."""
    if not d.over_wet:
        return ""
    return ("Dit debat ging over een wetsvoorstel. Of de Tweede Kamer het wetsvoorstel en de amendementen aanneemt, staat niet in onze gegevens. "
            "Na de Tweede Kamer stemt de Eerste Kamer over het wetsvoorstel.")


def termijn_zin(d):
    """Lang debat zonder tweede termijn in onze gegevens: zeg dat het debat daar niet af is."""
    if d.van > 1 and not M.heeft_tweede_termijn(d) and not d.is_stemmingen and not d.moties and not M.zelfde_titel(d):
        return "De tweede termijn van dit debat staat niet in onze gegevens; die kan op een andere dag zijn. Moties worden meestal in de tweede termijn ingediend."
    return ""


def zelfde_titel_regel(d, root=""):
    """Vaste koppeling tussen dagen van één debat: andere debatten met dezelfde agendatitel."""
    z = M.zelfde_titel(d)
    if not z:
        return ""
    def link(x):
        return (f'<a href="{root}debat/{x.slug}.html">{M.datum_lang(x.datum, dag=True)}</a>'
                + (f" ({len(x.moties)} {'motie' if len(x.moties) == 1 else 'moties'})" if x.moties else ""))
    eerder = [x for x in z if x.begin < d.begin]
    later = [x for x in z if x.begin > d.begin]
    uit = []
    if eerder:
        uit.append("Eerder over hetzelfde agendapunt: " + ", ".join(link(x) for x in eerder) + ".")
    if later:
        uit.append("Later over hetzelfde agendapunt: " + ", ".join(link(x) for x in later) + ".")
    return f'<p class="zelfde-titel">{" ".join(uit)}</p>'


def eerste_alinea(t):
    """(eerste alinea, rest) van een samenvatting: de eerste alinea staat bovenaan, de rest verderop."""
    regels = [r for r in (t or "").split("\n") if r.strip()]
    if not regels:
        return "", ""
    return regels[0], "\n".join(regels[1:])


def fracties_regel_debat(personen):
    """'SP (3), VVD (22), … en het kabinet': alle fracties die spraken, in spreekvolgorde."""
    gezien, frs = set(), []
    for p in personen:
        if p.fractie_code and p.fractie_code not in gezien:
            gezien.add(p.fractie_code)
            f = p.fractie
            frs.append(f"{e(p.fractie_code)} ({f['zetels']}{', coalitie' if f['coalitie'] else ''})" if f else e(p.fractie_code))
    kab = any(p.kabinet for p in personen)
    return ", ".join(frs) + (" en het kabinet" if kab and frs else ("het kabinet" if kab else ""))


def ook_aan_het_woord(x, root="", anker="#standpunten"):
    """Vaste regel onder een kaart: alle fracties die in dit (deel van het) debat spraken, in spreekvolgorde, met zetels."""
    gezien, frs = set(), []
    for p in x.personen():
        if p.fractie_code and p.fractie_code not in gezien:
            gezien.add(p.fractie_code)
            f = p.fractie
            frs.append(f"{e(p.fractie_code)} ({f['zetels']}{', coalitie' if f['coalitie'] else ''})" if f else e(p.fractie_code))
    kab = any(p.kabinet for p in x.personen())
    if not frs:
        return ""
    return (f'<p class="ook">Aan het woord in {"dit deel" if x.van > 1 else "dit debat"}: {", ".join(frs)}{" en het kabinet" if kab else ""}. '
            f'<a href="{anker}">Wat zeiden zij?</a></p>')


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
    Volgorde: zoals in de paginatekst (de volgorde waarin ze spraken). Heeft de pagina onderwerpen (vragenuur), dan per onderwerp."""
    if not x.pagina or not x.pagina["sprekers"]:
        return ""
    per = {p.id: p for p in x.personen()}
    sp = {s_["id"]: s_ for s_ in x.pagina["sprekers"]}

    def kaartje(s_):
        p = per.get(s_["id"])
        if not p:
            return ""
        n, r = wie(p)
        return (f'<li class="sp">{fig(p, "fg", root=root)}<div><p class="spn"><b>{n}</b> <span>{r}</span></p>'
                f'<p>{link_woorden(e(s_["standpunt"]), x.pagina["woorden"])}</p></div></li>')
    if x.pagina.get("onderwerpen"):
        uit, gehad = [], set()
        for o in x.pagina["onderwerpen"]:
            li = "".join(kaartje(sp[i]) for i in o["sprekers"] if i in sp)
            gehad |= set(o["sprekers"])
            uit.append(f'<h3 class="sph">{e(o["titel"])}</h3><ul class="{cls}">{li}</ul>')
        rest = "".join(kaartje(s_) for s_ in x.pagina["sprekers"] if s_["id"] not in gehad)
        return "".join(uit) + (f'<ul class="{cls}">{rest}</ul>' if rest else "")
    return f'<ul class="{cls}">' + "".join(kaartje(s_) for s_ in x.pagina["sprekers"]) + "</ul>"


def onderwerpen_regel(x):
    """Bij een vragenuur: de onderwerpen uit de paginadata, zodat de kaart niet voor het hele vragenuur lijkt te staan."""
    if not x.pagina or not x.pagina.get("onderwerpen"):
        return ""
    t = [o["titel"] for o in x.pagina["onderwerpen"]]
    return f"In dit vragenuur {len(t)} onderwerpen: " + "; ".join(t) + "."


def kernpunten(x):
    if not x.pagina or not x.pagina["kernpunten"]:
        return ""
    return "<ul class=\"kern\">" + "".join(f"<li>{link_woorden(e(k), x.pagina['woorden'])}</li>" for k in x.pagina["kernpunten"]) + "</ul>"


def nagelezen(x):
    r = x.redactie
    if not x.pagina:
        return ""
    if not r:
        return '<p class="klein">Tekst geschreven door een AI-model; niet nagelezen.</p>'
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
        tijd_ = M.tijd(b.get("begin")).replace(":", ".")
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
            f'</span></header>{tekst_html}</article>')
    status = ("Dit is het <b>voorlopige</b> verslag: sprekers kunnen nog kleine verschrijvingen laten verbeteren."
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
            + (f"{s['geen_figuur']} sprekers hebben geen goedgekeurd figuur; zij krijgen een neutraal silhouet. Heeft één van de twee sprekers op een kaart geen figuur, dan krijgen beide het silhouet. " if s["geen_figuur"] else "")
            + "Het zijn tekeningen, geen foto's en geen karikaturen. Iedereen heeft hetzelfde neutrale gezicht.")


def zo_werken_we(variant_regels, root=""):
    """De vaste inhoud van 'Zo werken we'. variant_regels: lijst (kop, [regels]) voor selectie en volgorde in deze variant."""
    naam, contact = afzender()
    F = M.fracties()
    co = F["coalitie"]
    zetels = sorted(F["per"].values(), key=lambda f: (-f["zetels"], f["code"].lower()))
    fr_rijen = "".join(f'<li><b>{e(f["code"])}</b> <span>{e(f["naam"]) if f["naam"] != f["code"] else ""}</span> <span class="z">{f["zetels"]} {"zetel" if f["zetels"] == 1 else "zetels"} · {"coalitie" if f["coalitie"] else "oppositie"}</span></li>' for f in zetels)
    som = sum(f["zetels"] for f in zetels)
    alle = [m for d in M.debatten() for m in d.moties]
    a_, v_, o_ = moties_telling(alle)
    motietal = (f"van de {a_ + v_} moties met een uitslag in onze gegevens zijn er {a_} aangenomen en {v_} verworpen." if a_ + v_ else "")
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
<li><b>Bij een vragenuur:</b> de kaart gaat over de eerste mondelinge vraag, tenzij die fractie in de weken ervoor al vaak op een kaart stond; dan de volgende vraag (spreidingsregel). De andere vragen staan als onderwerpen op de pagina.</li>
<li><b>Welke twee citaten:</b> uit de langste wisseling tussen twee sprekers die op elkaar reageren, tenzij die geen echte tegenstelling heeft of over een bijzaak gaat (minder dan 10% van de spreektijd); dan de volgende. Per spreker hooguit twee zinnen, zonder een voorbehoud weg te laten. Is er geen echte botsing, dan staat er één citaat en zeggen we dat erbij.</li>
<li><b>Volgorde van de twee citaten:</b> wie het eerst sprak, staat eerst. Zo kiest niemand wie het laatste woord krijgt. In een debat antwoordt het kabinet op vragen van de Kamer; daarom staat een minister vaak als tweede.</li>
<li><b>Welke kaart bij een lang debat:</b> lange debatten zijn in delen geknipt langs de rondes van het debat. Bovenaan het debat staat de kaart van het eerste deel waarin twee sprekers tegenover elkaar staan; elk deel heeft daarnaast zijn eigen pagina.</li>
<li><b>Welke debatten een kaart hebben:</b> een kaart wordt gemaakt bij een debat van meer dan 2.500 gesproken woorden dat geen tweeminutendebat, ordedebat of stemming is, en bij elk vragenuur. In de proefperiode heeft niet elk debat een kaart; kaarten die eerder bij een tweeminutendebat zijn gemaakt, blijven staan. Een kaart bij een ordedebat tonen we niet: dat gaat over de agenda. Een debat zonder kaart krijgt de titel en de figuren van de sprekers.</li>
<li><b>Standpunten:</b> van elke fractie die sprak, in de volgorde waarin ze spraken, met het aantal zetels; bij een coalitiefractie staat "coalitie". Zo is te zien hoe groot een fractie is. Onder elke kaart staan alle fracties die in dat debat spraken, met hun zetels.</li>
<li><b>Moties:</b> een motie staat bij het debat waarin haar eerste indiener sprak. Eerst de aangenomen, dan de verworpen moties, dan die zonder uitslag in onze gegevens; daarbinnen op motienummer. Een uitslag staat er alleen als hij in de open data van de Kamer staat.</li>
<li><b>Fracties bij een stemming:</b> per kant (voor, tegen) één lijst, de grootste fractie eerst, bij gelijk aantal op naam. Bij een coalitiefractie staat "coalitie". De zetels tellen we na met de lijst hieronder. Klopt de som niet, of komt hij niet op 150 uit, dan staat dat bij de uitslag.</li>
<li><b>Geen ranglijsten:</b> we tellen niet wie het vaakst of het langst sprak of interrumpeerde. Zulke tellingen zeggen weinig over het werk van een Kamerlid.</li>
</ul>
{regels_html}
</section>
<section id="wat-niet"><h2>Wat deze site niet laat zien</h2>
<ul>
<li>Alleen de debatten die in onze gegevens staan: plenaire debatten en een deel van de commissiedebatten. Veel werk van de Kamer gebeurt in commissies, schriftelijke vragen en overleg dat niet op deze site staat.</li>
<li>Stemmingen over wetsvoorstellen en amendementen, toezeggingen van ministers en de datum van een stemming staan niet in onze gegevens.</li>
<li>Een debat laat vooral zien waar Kamerleden het oneens zijn. Kijk daarom ook naar de uitslagen: {motietal}</li>
</ul></section>
<section id="fracties"><h2>Fracties en zetels</h2>
<p>Zetels volgens de open data van de Tweede Kamer (stand {M.datum_lang(F["stand"])}). Samen {som} zetels{"" if som == 150 else " (let op: niet 150)"}. Welke fracties de coalitie vormen staat niet in die data; dat houden we met de hand bij (stand {M.datum_lang(co["stand"])}): {e(", ".join(co["coalitie"]))}.</p>
<ul class="fractielijst">{fr_rijen}</ul></section>
<section id="begrippen"><h2>Begrippen</h2>{uitleg_lijst(list(UITLEG))}</section>
<section id="bronnen"><h2>Bronnen</h2><ul>
<li>Verslagen, moties en stemuitslagen: <a href="https://opendata.tweedekamer.nl/" rel="noopener">open data van de Tweede Kamer</a>.</li>
<li>Wil je per Kamerlid of partij zien hoe er gestemd is? Dat kan op Partijgedrag.nl, een site van anderen (niet van ons en niet van de Kamer).</li>
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
        from zoneinfo import ZoneInfo
        dt = datetime.fromisoformat(iso[:19]) if len(iso) > 10 else datetime.fromisoformat(iso + "T12:00:00")
        return format_datetime(dt.replace(tzinfo=ZoneInfo("Europe/Amsterdam")))
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


def hoe_liep_het_af(d, link_moties=None, deel=False):
    """Vaste inhoud van 'Hoe liep het af': eerst de wet (als het om een wetsvoorstel ging), dan de moties."""
    uit = []
    if wet_zin(d):
        uit.append('<p class="groot">Over het wetsvoorstel zelf: uitslag niet in onze gegevens.</p>')
        uit.append(f'<p>{"Moties uit dit debat: " if d.moties else ""}{e(afloop_tekst(d))}</p>')
        uit.append('<p class="klein">Over het wetsvoorstel en de amendementen stemt de Kamer apart; na de Tweede Kamer stemt de Eerste Kamer.</p>')
    else:
        uit.append(f'<p class="groot">{e(afloop_tekst(d))}</p>')
    if termijn_zin(d):
        uit.append(f'<p class="klein">{e(termijn_zin(d))}</p>')
    if d.moties:
        uit.append('<p class="klein">Een aangenomen motie is een verzoek aan de regering, geen wet of besluit. De regering beslist zelf óf en hoe ze het uitvoert.</p>')
        if link_moties:
            uit.append(f'<p><a href="{link_moties}">{"Alle" if len(d.moties) > 1 else "De"} {len(d.moties)} {"moties" if len(d.moties) > 1 else "motie"}'
                       f'{" en wie voor of tegen stemde" if any(motie_status(m) for m in d.moties) else ""}</a></p>')
    if deel and d.moties:
        uit.insert(0, '<p class="klein">De moties horen bij het hele debat, niet bij één deel.</p>')
    return "".join(uit)


def stemmingen_regel(d, root=""):
    """Bij een debat: de stemmingsrondes waarvan de voorzitter de agendatitel van dit debat aankondigde (vaste regel)."""
    ss = M.stemmingen_bij().get(d.id) or []
    if not ss:
        return ""
    li = "".join(f'<li><a href="{root}debat/{s.slug}.html">Stemmingen van {M.datum_lang(s.datum, dag=True)}, {M.tijd(s.begin).replace(":", ".")} uur</a>: '
                 f'{"een stemming over een motie bij" if "over een motie" in M.stemming_onderwerp(s) else "de stemming over"} {e(stemming_titel(s).replace("Stemmingen: ", "het "))}</li>' for s in ss)
    return (f'<div class="stemrondes-d"><p><b>Stemmingen over dit onderwerp</b> (de voorzitter kondigde ze zo aan):</p><ul>{li}</ul>'
            f'<p class="klein">De uitslag staat niet in onze gegevens; in het verslag lees je wat Kamerleden bij hun stem zeiden.</p></div>')


def stemming_titel(d):
    """Titel van een stemmingen-agendapunt: met het onderwerp uit de aankondiging als dat er is."""
    o = M.stemming_onderwerp(d)
    k = re.search(r"het ([A-Z][^,:]*\d{4})", o) or re.search(r"(Belastingplan \d{4})", o)
    return f"Stemmingen: {k.group(1)}" if k else "Stemmingen"


def eerste_zin(t):
    """(eerste zin, rest van de tekst) van een samenvatting."""
    t = (t or "").strip()
    if not t:
        return "", ""
    eerste_regel, _, overige = t.partition("\n")
    delen = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"'])", eerste_regel, maxsplit=1)
    zin = delen[0]
    rest = ((delen[1] if len(delen) > 1 else "") + ("\n" + overige if overige else "")).strip()
    return zin, rest


def hoe_kort(d):
    """Eén korte regel voor 'Hoe liep het af' bovenaan (de details staan verderop)."""
    if d.is_vragenuur:
        return "Bij een vragenuur wordt niet gestemd."
    if d.is_stemmingen:
        return "De Kamer stemde. Lees in het verslag wat er gezegd is."
    t = "Over het wetsvoorstel zelf: uitslag niet in onze gegevens. " if d.over_wet else ""
    if d.moties:
        a, v, o = moties_telling(d.moties)
        delen = [f"{a} aangenomen" if a else "", f"{v} verworpen" if v else "", f"{o} zonder uitslag in onze gegevens" if o else ""]
        t += f"{len(d.moties)} {'motie' if len(d.moties) == 1 else 'moties'}: " + ", ".join(x for x in delen if x) + "."
    else:
        t += "Geen moties in onze gegevens."
    return t


def hoe_lang(d, deel=False):
    """De uitleg bij de afloop (zonder de telling te herhalen): wet, termijn, stemmingsrondes, wat een motie is."""
    uit = []
    if deel and d.moties:
        uit.append('<p class="klein">De moties horen bij het hele debat, niet bij één deel.</p>')
    if wet_zin(d):
        uit.append(f'<p>{e(wet_zin(d))}</p>')
    if d.is_stemmingen or d.is_vragenuur:
        uit.append(f'<p>{e(afloop_tekst(d))}</p>')
    if termijn_zin(d):
        uit.append(f'<p class="klein">{e(termijn_zin(d))}</p>')
    if begin_zin(d) and d.van == 1:
        uit.append(f'<p class="klein">{e(begin_zin(d))}</p>')
    uit.append(stemmingen_regel(d, "../"))  # pagina's staan altijd een map diep
    if d.moties:
        uit.append('<p>Een aangenomen motie is een verzoek aan de regering, geen wet of besluit. De regering beslist zelf óf en hoe ze het uitvoert.</p>')
    return "".join(uit)


def begin_zin(d):
    return ("Het begin van dit debat valt buiten onze gegevens (bijvoorbeeld de eerste termijn op een eerdere dag); "
            "het staat wel in de verslagen van de Tweede Kamer.") if M.begin_ontbreekt(d) else ""


def delen_zin(d):
    n_tekst = sum(1 for y in d.delen if y.pagina)
    zin = ("Elk deel heeft een eigen pagina met een samenvatting." if n_tekst == d.van else
           "Voor geen van de delen is een samenvatting geschreven; het verslag staat er wel." if n_tekst == 0 else
           f"Van {n_tekst} van de {d.van} delen is een samenvatting; van alle delen staat het verslag er.")
    return f"Het debat is in {d.van} delen geknipt, langs de rondes van het debat. {zin}" + (" " + begin_zin(d) if begin_zin(d) else "")
