"""Variant A: de vergaderdag. Een agenda per dag, nieuwste dag eerst. Een debat met een kaart toont de botsing in de rij,
de moties met uitslag staan in een eigen rij eronder, een debat zonder kaart krijgt een rustige rij met titel en sprekers.
Een citaat is altijd een witte tekstballon met een staartje naar het figuur van de spreker."""
from kern import model as M, stukken as S
from kern.bouwen import Uitvoer

e = S.e
CSS = r"""
/* ---------- variant A: de vergaderdag ---------- */
.wrap{max-width:1080px;margin:0 auto;padding:0 max(16px,env(safe-area-inset-left)) 48px max(16px,env(safe-area-inset-right))}
.kop{display:flex;flex-wrap:wrap;align-items:center;gap:6px 20px;padding:16px 0;border-bottom:3px solid var(--ink)}
.logo{font-weight:700;font-size:24px;color:var(--ink);text-decoration:none;white-space:nowrap}
.logo mark{background:linear-gradient(transparent 60%,var(--hl) 60%);color:inherit;padding:0 .08em}
:root{--hl:#ffe066}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--hl:#8a6d00}}
:root[data-theme="dark"]{--hl:#8a6d00}
.werk{color:var(--muted);font-size:16px;flex:1 1 280px}
.kop nav{display:flex;gap:14px;flex-wrap:wrap;font-weight:700;font-size:16px}
.kop nav a[aria-current]{color:var(--ink);text-decoration-thickness:3px}
main{display:flex;flex-direction:column;gap:28px;padding-top:20px}
footer{margin-top:40px;border-top:2px solid var(--line);padding-top:16px;color:var(--muted);font-size:15px;display:flex;flex-direction:column;gap:6px;max-width:72ch}
.intro{display:flex;flex-direction:column;gap:6px;max-width:62ch}
.intro p{color:var(--muted);font-size:16px}
/* dag */
.dag{display:grid;grid-template-columns:190px 1fr;gap:0 28px;border-top:3px solid var(--ink);padding-top:18px}
.dat{position:sticky;top:8px;align-self:start}
.dat .wd{display:block;font-size:14px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
.dat .dn{display:block;font-size:56px;font-weight:700;line-height:1}
.dat .mj{display:block;font-size:18px}
.rijen{display:flex;flex-direction:column;min-width:0}
.rij{display:grid;grid-template-columns:62px 1fr;gap:4px 16px;padding:16px 0;border-bottom:1px solid var(--line);min-width:0}
.rij:last-child{border-bottom:0}
.rij.stem{padding-top:0;border-bottom:1px solid var(--line)}
.tijd{font-weight:700;font-variant-numeric:tabular-nums;color:var(--muted);padding-top:3px}
.rin{min-width:0;display:flex;flex-direction:column;gap:10px}
.rmeta{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;font-size:14px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
.chip{display:inline-block;font-size:13px;font-weight:700;letter-spacing:0;text-transform:none;border:1.5px solid var(--line);border-radius:999px;padding:0 9px;color:var(--muted)}
.agendat{font-size:15px;color:var(--muted)}
/* botsing */
.bk{background:var(--marker);color:#1d1b2e;border-radius:14px;padding:18px 20px;display:flex;flex-direction:column;gap:14px;min-width:0}
.bk a{color:#1d1b2e}
.bk .rmeta,.bk .agendat{color:#3a3410}
.bk .chip{border-color:#1d1b2e;color:#1d1b2e}
.vraag{font-size:clamp(1.45rem,3.2vw,2rem);font-weight:700;line-height:1.15}
.vraag a{text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:5px}
.duo{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:stretch}
.duo.een{grid-template-columns:1fr}
.spr{display:flex;flex-direction:column;min-width:0}
.ballon{position:relative;background:#fff;color:#1d1b2e;border:2.5px solid #1d1b2e;border-radius:24px;padding:14px 18px;margin:0 0 26px;flex:1}
.ballon p{margin:0;font-size:18px;line-height:1.42}
.ballon::before{content:"";position:absolute;left:26px;bottom:-25px;border-right:26px solid transparent;border-top:25px solid #1d1b2e}
.ballon::after{content:"";position:absolute;left:29.5px;bottom:-18px;border-right:18px solid transparent;border-top:18px solid #fff}
.wieb{display:flex;align-items:center;gap:12px;min-width:0}
.wieb .fg{width:68px;height:68px;border-color:#1d1b2e}
.naam{font-weight:700;display:block;line-height:1.25}
.rol{font-size:14px;display:block;line-height:1.3}
.bk .rol{color:#3a3410}
.links{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:10px;font-size:15px;font-weight:700}
.vid{display:inline-flex;align-items:center;gap:6px}
.bkvoet{display:flex;flex-wrap:wrap;gap:6px 18px;justify-content:space-between;align-items:baseline;font-size:15px}
.verder{font-weight:700;font-size:17px}
.geenb{font-size:15px;color:#3a3410}
/* terugval */
a.tv{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;justify-content:space-between;background:var(--tone);border-radius:14px;padding:14px 18px;color:var(--ink);text-decoration:none;min-width:0}
a.tv:hover .ttl{text-decoration:underline}
.tv>div:first-child{flex:1 1 300px;min-width:0;display:flex;flex-direction:column;gap:6px}
.ttl{font-size:20px;font-weight:700;line-height:1.25}
.stapel{display:flex;align-items:center}
.stapel .fg{width:40px;height:40px;margin-right:-9px}
.stapel .meer{margin-left:16px;font-size:14px;font-weight:700;color:var(--muted)}
/* stemrij */
details.st{border:2px solid var(--line);border-radius:12px;background:var(--panel)}
.st>summary{list-style:none;padding:10px 14px;display:flex;justify-content:space-between;gap:12px;align-items:center}
.st>summary::-webkit-details-marker{display:none}
.st>summary .pm{font-size:22px;line-height:1}
.st[open]>summary .pm{transform:rotate(45deg)}
.st ul{list-style:none;margin:0;padding:0 14px 12px;display:flex;flex-direction:column;gap:10px}
.st li{border-top:1px solid var(--line);padding-top:10px;display:flex;flex-direction:column;gap:5px;font-size:16px}
.st .meer{padding:0 14px 12px;font-size:15px}
/* debatpagina */
.krumel{font-size:15px;color:var(--muted)}
.dkop{display:flex;flex-direction:column;gap:8px}
.dkop h1{font-size:clamp(1.7rem,4.6vw,2.6rem)}
.dmeta{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;color:var(--muted);font-size:16px}
.afloop{display:grid;grid-template-columns:1fr;gap:16px;border-top:6px solid var(--ink);border-radius:0;padding:14px 18px;background:var(--tone)}
.afloop ul{margin:6px 0 0;padding-left:1.2em}
.bk a:focus-visible{outline-color:#1d1b2e}
.links a{padding:6px 0}
.links{gap:4px 16px}
.ook{color:#3a3410}
.ook a{font-weight:700}
.st ul.moties{padding:0 14px 14px}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .bk{background:#c9b24a}}
:root[data-theme="dark"] .bk{background:#c9b24a}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.afloop>div{display:flex;flex-direction:column;gap:8px;min-width:0}
.afloop h2{font-size:15px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.afloop .groot{font-size:19px;font-weight:700;line-height:1.35}
.blok{display:flex;flex-direction:column;gap:12px}
.blok>h2{font-size:24px}
ol.delen{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:8px}
ol.delen li{display:grid;grid-template-columns:auto 1fr;gap:2px 12px;align-items:baseline}
ol.delen .dn{font-weight:700;color:var(--muted);font-variant-numeric:tabular-nums}
ol.delen .df{grid-column:2;font-size:14px;color:var(--muted)}
ol.delen li[aria-current] a{color:var(--ink);font-weight:700}
.deelnav{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;border-top:2px solid var(--line);border-bottom:2px solid var(--line);padding:10px 0;font-weight:700}
.controle{display:flex;flex-direction:column;gap:6px;background:var(--tone);border-radius:12px;padding:14px 16px}
.kolommen{display:grid;grid-template-columns:minmax(0,62ch) minmax(0,1fr);gap:28px;align-items:start}
.zij{display:flex;flex-direction:column;gap:20px}
.zij h2{font-size:18px}
.zw{display:flex;flex-direction:column;gap:22px;max-width:72ch}
.zw section{display:flex;flex-direction:column;gap:8px}
.zw h2{font-size:24px;margin-top:6px}.zw h3{font-size:19px;margin-top:6px}
.zw ul{margin:0;padding-left:1.2em;display:flex;flex-direction:column;gap:6px}
main p,main li,main dd{max-width:62ch}
.krumel a,ol.delen a,.controle a,details summary,.links a{display:inline-block;padding-block:5px}
@media (max-width:820px){
  .dag{grid-template-columns:1fr;border-top:0;padding-top:0}
  .dat{display:flex;align-items:baseline;gap:8px;background:var(--tone);margin:0 -16px;padding:8px 16px;top:0;z-index:2}
  .dat .dn,.dat .mj{font-size:20px;display:inline}
  .dat .wd{font-size:20px;letter-spacing:0;text-transform:none;color:var(--ink);display:inline}
  .rij{grid-template-columns:1fr;gap:6px}
  .rij.stem .tijd{display:none}
  .duo{grid-template-columns:1fr;gap:12px}
  .afloop{grid-template-columns:1fr}
  .kolommen{grid-template-columns:1fr}
  .zij{position:static}
  .bk{padding:14px;gap:10px;margin:0 -4px}
  .kop{padding:10px 0;gap:4px 14px}
  .logo{font-size:21px}
  .werk{font-size:14px;flex-basis:100%;order:3}
  .kop nav{font-size:15px;gap:12px}
  .intro p{font-size:15px}
  .intro .langer{display:none}
  main{gap:20px;padding-top:12px}
  .ballon p{font-size:17px}
  .wieb .fg{width:56px;height:56px}
}
"""


def shell(titel, beschr, pad, root, inhoud, og=None, actief=""):
    nav = "".join(f'<a href="{root}{h}"{" aria-current=page" if h == actief else ""}>{t}</a>'
                  for h, t in (("index.html", "Agenda"), ("moties.html", "Moties en uitslagen"), ("zo-werken-we.html", "Zo werken we")))
    naam, contact = S.afzender()
    return (S.head(titel, beschr, pad, root, "style.css", og) +
            f'<body><a class="skip" href="#inhoud">Naar de inhoud</a><div class="wrap">'
            f'<header class="kop"><a class="logo" href="{root}index.html">Wat zei de <mark>Kamer?</mark></a>'
            f'<p class="werk">{S.WERKZIN}</p><nav aria-label="Hoofdmenu">{nav}</nav></header>'
            f'{inhoud}'
            f'<footer><p>Gemaakt door {naam} met de open data van de Tweede Kamer. Geen officiële site van de Tweede Kamer.</p>'
            f'<p>Samenvattingen zijn geschreven door een AI-model en nagelezen tegen het verslag. Citaten zijn letterlijk en automatisch gecontroleerd. '
            f'De figuren zijn getekend naar portretten; het zijn geen foto\'s.</p>'
            f'<p>Fout gezien? Meld het via {contact}. · <a href="{root}zo-werken-we.html">Zo werken we</a> · <a href="{root}feed.xml">RSS</a></p></footer>'
            f'</div></body></html>')


# ------------------------------------------------------------------ onderdelen

def tijd_nl(iso):
    return M.tijd(iso).replace(":", ".")


def ballon(c, root, video, deel):
    p = c["persoon"]
    naam = e(c["naam"])
    rol = e(p.label_fractie() if p and p.fractie_code else c["partij"])
    links = [f'<a href="{root}verslag/{deel.slug}.html#b{c["beurt"]}">Lees in het verslag</a>']
    if video:
        links.insert(0, f'<a class="vid" href="{e(c["video"])}" rel="noopener">▶ {e(c["tijd"].replace(":", "."))} uur · Bekijk dit moment (Debat Direct)</a>')
    return (f'<div class="spr"><blockquote class="ballon" data-citaat="{deel.id}#{c["beurt"]}"><p>“{e(S.citaat_weergave(c["citaat"]))}”</p></blockquote>'
            f'<div class="wieb">{S.fig(p, "fg", root=root)}<div><span class="naam">{naam}</span><span class="rol">{rol}</span></div></div>'
            f'<div class="links">{"".join(links)}</div></div>')


def kaart_blok(x, root, kop="h3", link=None, toon_meta=None, noot=True, ook_anker=None):
    """De botsing: vraag en twee ballonnen. x = het deel met de kaart."""
    k = x.kaart
    duo = "".join(ballon(c, root, k["video"], x) for c in k["citaten"])
    vraag = f'<a href="{link}">{e(k["vraag"])}</a>' if link else e(k["vraag"])
    geen = ('<p class="geenb">In dit debat stonden geen twee sprekers duidelijk tegenover elkaar; daarom één citaat.</p>'
            if len(k["citaten"]) < 2 else
            '<p class="geenb">Deze twee sprekers waren het niet duidelijk oneens; ze lieten elk een eigen kant van het onderwerp zien.</p>' if k["geen_botsing"] else "")
    voet = '<span>Videolinks openen Debat Direct, de site van de Tweede Kamer.</span>' if k["video"] else ""
    ond = S.onderwerpen_regel(x)
    ook = S.ook_aan_het_woord(x, root, ook_anker) if ook_anker else ""
    return (f'{toon_meta or ""}<{kop} class="vraag">{vraag}</{kop}>'
            + (f'<p class="geenb">{e(ond)}</p>' if ond else "") +
            f'<div class="duo{" een" if len(k["citaten"]) < 2 else ""}">{duo}</div>{geen}'
            + (f'<div class="bkvoet">{voet}</div>' if voet else "") + ook)


def stapel(personen, root, n=6):
    figs = "".join(S.fig(p, "fg", alt=False, root=root) for p in personen[:n])
    meer = f'<span class="meer">+{len(personen) - n}</span>' if len(personen) > n else ""
    namen = ", ".join(p.naam for p in personen)
    return f'<div class="stapel" role="img" aria-label="Sprekers: {e(namen)}">{figs}{meer}</div>'


def rmeta(d):
    delen = f'<span class="chip">{len(d.delen)} delen</span>' if len(d.delen) > 1 else ""
    voorl = ""
    return f'<div class="rmeta"><span>{e(d.soort_label)}</span>{delen}{voorl}</div>'


def stemrij(d, root):
    if not d.moties:
        return ""
    ms = [m for m in d.moties if S.motie_status(m)]
    a, v, o = S.moties_telling(d.moties)
    sam = ", ".join(x for x in (f"{a} aangenomen" if a else "", f"{v} verworpen" if v else "",
                                 f"{o} zonder uitslag in onze gegevens" if o else "") if x)
    items = "".join(
        f'<li><span>Motie {e(m["nummer"])} {e(M.motie_omschrijving(m))}: <b class="uitslag-{S.motie_status(m)}">{S.motie_status(m)}</b> '
        f'({m["uitslag"]["zetels_voor"]} zetels voor, {m["uitslag"]["zetels_tegen"]} tegen)</span></li>' for m in ms)
    if not ms:
        items = '<li>Van deze moties staat geen uitslag in onze gegevens.</li>'
    return (f'<div class="rij stem"><span class="tijd"></span><details class="st"><summary><span>Moties (verzoeken aan de regering) bij dit debat: <b>{len(d.moties)}</b> · {sam}</span>'
            f'<span class="pm" aria-hidden="true">+</span></summary><ul>{items}</ul>'
            f'<p class="meer"><a href="{root}debat/{d.slug}.html#moties">Wie stemde voor en tegen, en wat vroegen de moties?</a></p></details></div>')


def rij(d, root):
    href = f"{root}debat/{d.slug}.html"
    tijd_ = f'<span class="tijd">{tijd_nl(d.begin)}</span>'
    k = d.kaart
    if k and not d.is_stemmingen:
        agenda = f'<p class="agendat">{e(d.titel_agenda)}</p>' if d.titel_agenda.lower() not in (k.kaart["vraag"] or "").lower() else ""
        hoofd = (f'<div class="rij bots">{tijd_}<div class="rin"><div class="bk">{rmeta(d)}{agenda}'
                 f'{kaart_blok(k, root, "h3", href, noot=False)}<p class="ook">Aan het woord: {S.fracties_regel_debat(d.personen())}.</p>'
                 f'<a class="verder" href="{href}">Lees wat er gezegd is en hoe het afliep</a></div></div></div>')
    elif d.is_stemmingen:
        n = len(d.genoemde_moties)
        sub = (f"In stemverklaringen genoemd: " + ", ".join(f"motie {e(m['nummer'])} ({S.motie_status(m) or 'geen uitslag in onze gegevens'})" for m in d.genoemde_moties)
               if n else "Kamerleden zeiden kort waarom ze voor of tegen stemden. De uitslag staat niet in onze gegevens; uitslagen van moties staan bij hun debat.")
        hoofd = (f'<div class="rij">{tijd_}<div class="rin"><a class="tv" href="{href}"><div>{rmeta(d)}<span class="ttl">{e(d.titel)}</span>'
                 f'<span class="klein">{sub}</span></div>{stapel(d.personen(), root)}</a></div></div>')
    else:
        titel = d.titel
        hoofd = (f'<div class="rij">{tijd_}<div class="rin"><a class="tv" href="{href}"><div>{rmeta(d)}<span class="ttl">{e(titel)}</span>'
                 + (f'<span class="agendat">{e(d.titel_agenda)}</span>' if titel != d.titel_agenda else "")
                 + f'<span class="klein">Aan het woord: {S.fracties_regel_debat(d.personen())}.</span></div>{stapel(d.personen(), root, 4)}</a></div></div>')
    z = S.zelfde_titel_regel(d, root)
    if z:
        hoofd = hoofd.replace('</div></div></div>', f'{z}</div></div></div>', 1) if "rij bots" in hoofd else hoofd.replace('</a></div></div>', f'</a>{z}</div></div>', 1)
    return hoofd + stemrij(d, root)


def home(U):
    dagen = M.dagen()
    blokken = []
    for datum, ds in dagen:
        j, m, dg = datum.split("-")
        wd = M.DAGEN[__import__("datetime").date(int(j), int(m), int(dg)).weekday()]
        blokken.append(f'<section class="dag" aria-labelledby="d{datum}"><h2 class="dat" id="d{datum}"><span class="wd">{wd}</span> <span class="dn">{int(dg)}</span> '
                       f'<span class="mj">{M.MAANDEN[int(m) - 1]} {j}</span></h2><div class="rijen">{"".join(rij(d, "") for d in ds)}</div></section>')
    inhoud = (f'<main id="inhoud"><div class="intro"><h1 class="vh">Agenda van de Tweede Kamer</h1>'
              f'<p>Debatten per vergaderdag, nieuwste eerst. <span class="langer">Wat letterlijk gezegd is, staat in een witte ballon; tik op een vraag of titel voor de samenvatting, alle standpunten en de moties.</span></p></div>'
              + "".join(blokken) + "</main>")
    U.schrijf("index.html", shell(f"{S.NAAM} Debatten uit de Tweede Kamer in gewone taal", S.WERKZIN + " De debatten per vergaderdag, met de moties en hoe erover gestemd is.",
                                  "", "", inhoud, actief="index.html"))


def afloop_blok(d, root, waar_html, deel=False):
    """Compact blok direct onder de kop: één zin waar het om ging, één regel hoe het afliep. Details staan verderop (#afloop)."""
    hoe = f'<p class="groot">{e(S.hoe_kort(d))}</p><p><a href="#afloop">Meer over de afloop</a></p>'
    return (f'<section class="afloop" aria-label="Waar ging het om en hoe liep het af"><div><h2>{"Waar ging dit deel over" if deel else "Waar ging het om"}</h2>{waar_html}</div>'
            f'<div><h2>Hoe liep {"het debat" if deel else "het"} af</h2>{hoe}</div></section>')


def delen_lijst(d, root, huidig=None):
    rijen = []
    for x in d.delen:
        cur = ' aria-current="page"' if huidig is x else ""
        tekst_ = "" if x.pagina else ' · geen samenvatting, wel het verslag'
        kaart_ = ""
        if x.kaart and len(x.kaart["citaten"]) >= 1:
            kaart_ = " · citaten van " + " en ".join(
                f'{e(c["naam"])} ({e(c["persoon"].fractie_code + ", " + str(c["persoon"].fractie["zetels"]) + (", coalitie" if c["persoon"].fractie["coalitie"] else "") if c["persoon"] and c["persoon"].fractie else (c["persoon"].fractie_code if c["persoon"] and c["persoon"].fractie_code else "kabinet"))})'
                for c in x.kaart["citaten"])
        rijen.append(f'<li{cur}><span class="dn">{x.nummer}.</span><a href="{root}debat/{x.slug}.html">{e(x.titel)}</a>'
                     f'<span class="df">{e(x.fase_label)} · {tijd_nl(x.begin)} uur{tekst_}{kaart_}</span></li>')
    for n, i in d.ontbrekend:
        rijen.append(f'<li><span class="dn">{n}.</span><span>Dit deel ontbreekt in onze gegevens.</span></li>')
    return f'<ol class="delen">{"".join(rijen)}</ol>'


def kop(d, titel, root, x=None):
    meta = [M.datum_lang(d.datum, dag=True), f"{tijd_nl(x.begin if x else d.begin)} uur", d.soort_label] + ([x.fase_label] if x else [])
    voorl = ' <span class="voorl">voorlopig verslag</span>' if d.voorlopig else ""
    return (f'<p class="krumel"><a href="{root}index.html#d{d.datum}">Agenda van {M.datum_lang(d.datum, dag=True)}</a>'
            + (f' › <a href="{root}debat/{d.slug}.html">{e(d.titel_agenda)}</a>' if x else "") + "</p>"
            f'<header class="dkop"><div class="dmeta">{" · ".join(e(m) for m in meta)}{voorl}</div><h1>{e(titel)}</h1></header>')


def tekst_deel(x, root, met_kaart=True, rest=""):
    """Samenvatting, kaart (als dit deel er een heeft), standpunten, woorden en controle van één deel."""
    uit = []
    if x.kaart and met_kaart:
        uit.append(f'<section class="blok" aria-label="De botsing"><div class="bk">{kaart_blok(x, root, "h2", ook_anker="#standpunten")}</div></section>')
    if x.pagina and rest:
        uit.append(f'<section class="blok"><h2>Meer over {"dit deel" if x.van > 1 else "dit debat"}</h2>{S.alineas(rest, x.pagina["woorden"])}</section>')
    if x.pagina:
        uit.append(S.oud_verslag(x))
        uit.append(f'<section class="blok" id="standpunten"><h2>Wat de sprekers zeiden</h2><p class="klein">Per spreker, in de volgorde waarin ze spraken. Achter elke fractie het aantal zetels en of ze in de coalitie zit.</p>{S.standpunten(x, root)}</section>')
    else:
        uit.append(f'<section class="blok" id="standpunten"><h2>Wie spraken</h2><p>Voor {"dit deel" if x.van > 1 else "dit debat"} is geen samenvatting geschreven. '
                   f'Hieronder staan de sprekers; in het verslag lees je alles wat ze zeiden.</p>{sprekers_lijst(x, root)}</section>')
    return "".join(uit)


def sprekers_lijst(x, root):
    li = "".join(f'<li class="sp">{S.fig(p, "fg", root=root)}<div><p class="spn"><b>{e(p.naam)}</b> <span>{e(p.label_fractie() if p.fractie_code else p.functie)}</span></p></div></li>'
                 for p in x.personen())
    return f'<ul class="standpunten">{li}</ul>'


def zijkolom(d, x, root):
    """Begrippen, moeilijke woorden en controle."""
    woorden = S.woordenlijst(x.pagina["woorden"]) if x and x.pagina else ""
    uit = [f'<section class="controle"><h2>Controleer het zelf</h2>'
           + (f'<p><a href="{root}verslag/{x.slug}.html">Lees het hele verslag{" van dit deel" if x.van > 1 else ""}</a>, letterlijk en met de video per spreekbeurt.</p>' if x else "")
           + (S.nagelezen(x) if x else "")
           + ("" if x else '<p>Het letterlijke verslag per deel, met de video per spreekbeurt:</p><ul class="kern">'
              + "".join(f'<li><a href="{root}verslag/{y.slug}.html">Verslag van deel {y.nummer}</a></li>' for y in d.delen) + "</ul>")
           + "</section>"]
    if woorden:
        uit.append(f'<section><h2>Moeilijke woorden</h2>{woorden}</section>')
    uit.append(f'<section><h2>Uitleg</h2>{S.uitleg_lijst(S.uitleg_voor(d))}</section>')
    return f'<aside class="zij">{"".join(uit)}</aside>'


def moties_sectie(d, root, deel=False):
    """Sectie 'Hoe liep het af' met de uitleg (wet, termijn, stemmingsrondes) en alle moties."""
    lijst = ""
    if d.moties and not deel:
        lijst = ('<h3 id="moties">Moties</h3><p class="klein">Eerst de aangenomen, dan de verworpen moties, dan die zonder uitslag in onze gegevens. '
                 'Bij elke uitslag de fracties met hun zetels.</p>' + S.moties_lijst(d, root, "h4"))
    elif d.moties and deel:
        lijst = f'<p><a href="{root}debat/{d.slug}.html#moties">De {len(d.moties)} moties van het hele debat, met wie voor en tegen stemde</a></p>'
    return f'<section class="blok" id="afloop"><h2>Hoe liep {"het debat" if deel else "het"} af</h2>{S.hoe_lang(d, deel)}{lijst}</section>'


def debat_pagina(U, d):
    root = "../"
    og = f"og/{d.slug}.png"
    if len(d.delen) == 1 and d.van == 1:
        x = d.delen[0]
        eerste, rest = S.eerste_zin(x.pagina["samenvatting"]) if x.pagina else ("", "")
        waar = (S.alineas(eerste, x.pagina["woorden"]) + S.zelfde_titel_regel(d, root) if x.pagina else
                f'<p>{e(d.onderwerp)}.</p><p class="klein">Voor dit debat is geen samenvatting geschreven; het verslag staat er wel.</p>')
        hoofd = (kop(d, d.titel, root) +
                 f'<div class="kolommen"><div class="blok">{afloop_blok(d, root, waar)}{tekst_deel(x, root, rest=rest)}{moties_sectie(d, root)}</div>{zijkolom(d, x, root)}</div>')
    else:
        start, eind = tijd_nl(min(x.begin for x in d.delen)), tijd_nl(max(x.eind or x.begin for x in d.delen))
        k = d.kaart
        waar = (f'<p>Van {start} tot {eind} uur. {e(S.delen_zin(d))} <a href="#delen">Naar de delen</a></p>' + S.zelfde_titel_regel(d, root))
        kaart = (f'<section class="blok" aria-label="De botsing"><div class="bk"><div class="rmeta"><span>Uit deel {k.nummer}: {e(k.fase_label)}</span></div>{kaart_blok(k, root, "h2", ook_anker="#sprekers")}</div></section>' if k else "")
        hoofd = (kop(d, d.titel_agenda, root) +
                 f'<div class="kolommen"><div class="blok">{afloop_blok(d, root, waar)}{kaart}'
                 f'<section class="blok" id="delen"><h2>De delen van dit debat</h2>{delen_lijst(d, root)}</section>{moties_sectie(d, root)}'
                 f'<section class="blok" id="sprekers"><h2>Alle sprekers</h2>{sprekers_lijst_debat(d, root)}</section></div>{zijkolom(d, None, root)}</div>')
        for x in d.delen:
            deel_pagina(U, d, x)
    U.schrijf(f"debat/{d.slug}.html", shell(f"{d.titel} – {S.NAAM}", S.beschrijving(d), f"debat/{d.slug}.html", root,
                                            f'<main id="inhoud">{hoofd}</main>', og=og))


def sprekers_lijst_debat(d, root):
    li = "".join(f'<li class="sp">{S.fig(p, "fg", root=root)}<div><p class="spn"><b>{e(p.naam)}</b> <span>{e(p.label_fractie() if p.fractie_code else p.functie)}</span></p></div></li>'
                 for p in d.personen())
    return f'<p class="klein">In de volgorde waarin ze voor het eerst spraken.</p><ul class="standpunten">{li}</ul>'


def deel_pagina(U, d, x):
    root = "../"
    i = d.delen.index(x)
    vorige = d.delen[i - 1] if i > 0 else None
    volgende = d.delen[i + 1] if i + 1 < len(d.delen) else None
    nav = (f'<nav class="deelnav" aria-label="Vorige en volgende deel">'
           + (f'<a href="{vorige.slug}.html" aria-label="Vorig deel: {e(vorige.titel)}">← Deel {vorige.nummer}</a>' if vorige else "<span></span>")
           + f'<span>Deel {x.nummer} van {x.van}</span>'
           + (f'<a href="{volgende.slug}.html" aria-label="Volgend deel: {e(volgende.titel)}">Deel {volgende.nummer} →</a>' if volgende else "<span></span>") + "</nav>")
    eerste, rest = S.eerste_zin(x.pagina["samenvatting"]) if x.pagina else ("", "")
    waar = (f'<p class="groot">{e(x.titel)}</p>' if x.pagina else "") + (S.alineas(eerste, x.pagina["woorden"]) if x.pagina else
            '<p>Voor dit deel is geen samenvatting geschreven. Hieronder staan de sprekers; het verslag staat er wel.</p>') + S.zelfde_titel_regel(d, root)
    afloop = afloop_blok(d, root, waar, deel=True)
    inhoud = (kop(d, f"{d.titel_agenda}, deel {x.nummer} van {x.van}", root, x) + nav +
              f'<div class="kolommen"><div class="blok">{afloop}{tekst_deel(x, root, rest=rest)}{moties_sectie(d, root, deel=True)}'
              f'<section class="blok"><h2>Alle delen van dit debat</h2>{delen_lijst(d, root, x)}</section></div>{zijkolom(d, x, root)}</div>' + nav)
    U.schrijf(f"debat/{x.slug}.html", shell(f"{x.titel} – {d.titel_agenda} (deel {x.nummer}) – {S.NAAM}", S.beschrijving(d, x),
                                            f"debat/{x.slug}.html", root, f'<main id="inhoud">{inhoud}</main>', og=f"og/{d.slug}.png"))


def verslag_paginas(U, d):
    for x in d.delen:
        body = S.verslag_body(x, "../", f"../debat/{x.slug}.html", "Terug naar de samenvatting")
        U.schrijf(f"verslag/{x.slug}.html", shell(f"Verslag: {d.titel_agenda}{f' (deel {x.nummer})' if x.van > 1 else ''} – {S.NAAM}",
                                                  f"Het letterlijke verslag van {d.titel_agenda}, {M.datum_lang(d.datum)}.",
                                                  f"verslag/{x.slug}.html", "../", body, og=f"og/{d.slug}.png"))


def moties_pagina(U):
    ds = [d for d in M.debatten() if d.moties]
    alle = [m for d in ds for m in d.moties]
    a, v, o = S.moties_telling(alle)
    blokken = "".join(
        f'<section class="blok"><h2><a href="debat/{d.slug}.html">{e(d.titel_agenda)}</a></h2><p class="klein">{M.datum_lang(d.datum, dag=True)} · {e(d.soort_label)}</p>'
        f'<details class="st"><summary><span>{e(S.afloop_tekst(d))}</span><span class="pm" aria-hidden="true">+</span></summary>{S.moties_lijst(d, "", "h3")}</details></section>' for d in ds)
    inhoud = (f'<main id="inhoud"><header class="dkop"><h1>Moties en uitslagen</h1></header>'
              f'<div class="lees"><p>Alle moties uit de debatten op deze site, per debat, nieuwste debat eerst. Samen {len(alle)} moties: {a} aangenomen, {v} verworpen'
              f'{f", van {o} staat geen uitslag in onze gegevens" if o else ""}.</p>'
              f'<details><summary>Wat is een motie en hoe wordt gestemd?</summary><p class="klein">{e(S.UITLEG["motie"][1])} {e(S.UITLEG["stemming"][1])}</p>'
              f'<p class="klein">Per Kamerlid of partij zien hoe er gestemd is? Dat kan op <a href="https://partijgedrag.nl/" rel="noopener">Partijgedrag.nl</a>, een site van anderen.</p></details></div>'
              f'{blokken}</main>')
    U.schrijf("moties.html", shell(f"Moties en uitslagen – {S.NAAM}", "Alle moties uit de debatten op deze site, met de uitslag en de zetels per fractie.",
                                   "moties.html", "", inhoud, actief="moties.html"))


def zo_werken_we(U):
    regels = [("In deze variant", [
        "<b>Agenda:</b> nieuwste vergaderdag eerst; binnen een dag in de volgorde waarin de debatten begonnen.",
        "<b>Een rij per debat:</b> een lang debat in delen is één rij, op het begintijdstip van het eerste deel.",
        "<b>Rij met kaart:</b> een debat met een kaart toont de vraag en de twee citaten, en daaronder alle fracties die spraken, met hun zetels. Andere debatten tonen de titel en dezelfde regel met fracties.",
        "<b>Een deel van een lang debat</b> heeft als kop de agendatitel met het deelnummer; de inhoudelijke titel van het deel staat in de delenlijst en boven de samenvatting.",
        "<b>Binnen een dag</b> staan de debatten in de volgorde waarin ze begonnen, zoals een agenda. Debatten met dezelfde agendatitel op verschillende dagen (zoals het Belastingplan) verwijzen naar elkaar.",
        "<b>Rij met moties:</b> direct onder elk debat waarin moties zijn ingediend, met de uitslagen die in onze gegevens staan.",
        "<b>Een citaat</b> staat altijd in een witte ballon met een staartje naar het figuur van de spreker. Alles wat deze site zelf schrijft, staat nooit in zo'n ballon.",
    ])]
    inhoud = f'<main id="inhoud" class="zw"><h1>Zo werken we</h1><p class="lees">{S.WERKZIN} Hier lees je wie deze site maakt, hoe een pagina ontstaat en welke vaste regels we volgen.</p>{S.zo_werken_we(regels)}</main>'
    U.schrijf("zo-werken-we.html", shell(f"Zo werken we – {S.NAAM}", "Wie deze site maakt, hoe de teksten ontstaan en welke vaste regels we volgen.",
                                         "zo-werken-we.html", "", inhoud, actief="zo-werken-we.html"))


def bouw():
    U = Uitvoer("a")
    home(U)
    for d in M.debatten():
        debat_pagina(U, d)
        verslag_paginas(U, d)
    moties_pagina(U)
    zo_werken_we(U)
    items = [(d.titel, f"debat/{d.slug}.html", S.beschrijving(d), d.begin) for d in M.debatten()]
    U.afronden(CSS, items, "#ffe066")
    return U


if __name__ == "__main__":
    U = bouw()
    print("A gebouwd:", len(U.paden), "pagina's in", U.dir)
