"""Variant B: onderwerpen door de tijd. De ingang is een onderwerp (bijvoorbeeld het Belastingplan): alle debatten
erover op één tijdlijn, met na elk debat de moties en hun uitslag. Debatten met dezelfde titel of moties in hetzelfde
Kamerstuk horen bij één onderwerp (vaste regel). Een citaat is altijd cursieve tekst achter een dikke streep, met het
figuur van de spreker bovenaan die streep."""
from kern import model as M, stukken as S
from kern.bouwen import Uitvoer
import a as A  # alleen vormvrije hulpstukken (stapel, delen-lijst, sprekerslijst, zijkolom)

e = S.e
CSS = r"""
/* ---------- variant B: onderwerpen door de tijd ---------- */
:root{--b:#0e5f63;--bl:#d8ecec;--cit:#1d1b2e}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--b:#7fd0cf;--bl:#163536;--cit:#f1f0f7}}
:root[data-theme="dark"]{--b:#7fd0cf;--bl:#163536;--cit:#f1f0f7}
.wrap{max-width:1000px;margin:0 auto;padding:0 max(16px,env(safe-area-inset-left)) 48px max(16px,env(safe-area-inset-right))}
.kop{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 22px;padding:18px 0 12px}
.logo{font-weight:700;font-size:22px;color:var(--ink);text-decoration:none}
.logo span{color:var(--b)}
.kop nav{display:flex;gap:6px 14px;flex-wrap:wrap;font-weight:700;font-size:16px;margin-left:auto}
.kop nav a{color:var(--ink);text-decoration:none;border-bottom:3px solid transparent}
.kop nav a[aria-current]{border-bottom-color:var(--b)}
.werk{flex-basis:100%;color:var(--muted);font-size:16px}
main{display:flex;flex-direction:column;gap:26px;padding-top:14px;border-top:1px solid var(--line)}
footer{margin-top:44px;border-top:1px solid var(--line);padding-top:14px;color:var(--muted);font-size:15px;display:flex;flex-direction:column;gap:6px;max-width:72ch}
h1{font-size:clamp(1.7rem,4.6vw,2.5rem)}
.sub{color:var(--muted);font-size:16px}
.lees p+p{margin-top:8px}
/* citaatvorm B */
.cit{display:flex;flex-direction:column;gap:8px;min-width:0}
.cit .fg{width:52px;height:52px;border-color:var(--cit)}
.cit .wieb{display:flex;align-items:center;gap:12px;padding-left:23px}
.cit blockquote{margin:0;border-left:7px solid var(--cit);padding:2px 0 2px 16px;font-size:19px;line-height:1.45}
.cit blockquote::before{content:"Letterlijk";display:block;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:2px}
.cit .wie{font-size:15px}
.cit .wie b{display:block;font-size:16px}
.cit .wie span{color:var(--muted)}
.cit .links{padding-left:23px;display:flex;flex-wrap:wrap;gap:4px 14px;font-size:15px;font-weight:700}
.paar{display:flex;flex-direction:column;gap:18px}
.vraag{font-size:clamp(1.3rem,3vw,1.75rem);line-height:1.2}
.vraag a{color:inherit;text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:5px}
.noot{font-size:15px;color:var(--muted)}
/* onderwerpkaarten op de voorpagina */
.lijst{display:flex;flex-direction:column;gap:22px;list-style:none;margin:0;padding:0}
.ok{border:2px solid var(--line);border-radius:16px;background:var(--panel);overflow:hidden}
.ok .okop{background:var(--bl);padding:14px 18px;display:flex;flex-direction:column;gap:4px}
.ok .okop h2{font-size:18px}
.ok .vraag{font-size:clamp(1.35rem,3vw,1.75rem)}
.ook{font-size:15px;color:var(--muted)}
.ok .okop h2 a{color:var(--ink);text-decoration:none}
.ok .okop h2 a:hover{text-decoration:underline}
.okin{padding:16px 18px;display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:20px}
.okin>div{display:flex;flex-direction:column;gap:12px;min-width:0}
.mini{list-style:none;margin:0;padding:10px 12px;display:flex;flex-direction:column;gap:8px;background:var(--tone);border-radius:10px}
.mini li{font-size:15px}
.mini b{display:block;font-size:14px;color:var(--muted)}
.tel{font-size:17px;font-weight:700}
.verder{font-weight:700}
/* tijdlijn */
ol.tijdlijn{list-style:none;margin:0;padding:0 0 0 26px;border-left:2px dotted var(--b);display:flex;flex-direction:column;gap:26px}
.tl{position:relative;display:flex;flex-direction:column;gap:12px;min-width:0}
.tl::before{content:"";position:absolute;left:-36px;top:3px;width:16px;height:16px;border-radius:50%;background:var(--b)}
.tl.mot::before{width:10px;height:10px;left:-33px;top:6px;background:var(--paper);border:2px solid var(--b)}
.tld{font-size:14px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--b)}
.tl h3{font-size:21px}
.tl h3 a{color:var(--ink)}
.kader{border:2px solid var(--line);border-radius:14px;padding:16px 18px;background:var(--panel);display:flex;flex-direction:column;gap:14px;min-width:0}
.stand{display:flex;flex-wrap:wrap;gap:8px;align-items:flex-start}
.stand div{background:var(--tone);border-radius:10px;padding:6px 12px;font-size:16px}
.stand b{font-size:22px}
details.ml summary{font-size:16px;color:var(--b)}
details.ml ul.moties{margin-top:10px}
.afloop{display:flex;flex-direction:column;gap:14px;border-top:5px solid var(--b);background:var(--panel);border-radius:0 0 14px 14px;padding:16px 18px;box-shadow:0 1px 0 var(--line)}
.afloop h2{font-size:15px;letter-spacing:.06em;text-transform:uppercase;color:var(--b)}
.afloop>div{display:flex;flex-direction:column;gap:8px}
.afloop .groot{font-size:19px;font-weight:700}
.krumel{font-size:15px;color:var(--muted)}
.dkop{display:flex;flex-direction:column;gap:8px}
.dmeta{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;color:var(--muted);font-size:16px}
.blok{display:flex;flex-direction:column;gap:12px;min-width:0}
.blok>h2{font-size:23px}
.kolommen{display:grid;grid-template-columns:minmax(0,62ch) minmax(0,1fr);gap:28px;align-items:start}
.zij{display:flex;flex-direction:column;gap:20px}
.zij h2{font-size:18px}
.controle{display:flex;flex-direction:column;gap:6px;background:var(--bl);border-radius:12px;padding:14px 16px}
ol.delen{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:8px}
ol.delen li{display:grid;grid-template-columns:auto 1fr;gap:2px 12px;align-items:baseline}
ol.delen .dn{font-weight:700;color:var(--muted)}
ol.delen .df{grid-column:2;font-size:14px;color:var(--muted)}
ol.delen li[aria-current] a{color:var(--ink);font-weight:700}
.deelnav{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:10px 0;font-weight:700}
.stapel{display:flex;align-items:center}
.stapel .fg{width:38px;height:38px;margin-right:-8px}
.stapel .meer{margin-left:14px;font-size:14px;font-weight:700;color:var(--muted)}
.stemrondes{display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0;margin:0}
.stemrondes a{display:inline-block;border:1.5px solid var(--line);border-radius:999px;padding:4px 12px;font-size:15px}
.zw{display:flex;flex-direction:column;gap:22px;max-width:72ch}
.zw section{display:flex;flex-direction:column;gap:8px}
.zw h2{font-size:24px;margin-top:6px}.zw h3{font-size:19px;margin-top:6px}
.zw ul{margin:0;padding-left:1.2em;display:flex;flex-direction:column;gap:6px}
@media (max-width:760px){
  .okin{grid-template-columns:1fr}
  .kolommen{grid-template-columns:1fr}
  .kop nav{margin-left:0;font-size:15px}
  .werk{font-size:14px}
  .kop{gap:4px 14px}
  .cit .fg{width:48px;height:48px}
  .tl .kader{margin-left:-18px}
  .lees .sub{display:none}
  .ok .okop{padding:10px 14px}
  .okin{padding:12px 14px}
  .cit blockquote{font-size:17px;padding-left:12px}
  .cit .wieb,.cit .links{padding-left:18px}
  ol.tijdlijn{padding-left:20px}
  .tl::before{left:-31px}.tl.mot::before{left:-28px}
}
"""


def shell(titel, beschr, pad, root, inhoud, og=None, actief=""):
    nav = "".join(f'<a href="{root}{h}"{" aria-current=page" if h == actief else ""}>{t}</a>'
                  for h, t in (("index.html", "Onderwerpen"), ("moties.html", "Uitslagen"), ("zo-werken-we.html", "Zo werken we")))
    naam, contact = S.afzender()
    return (S.head(titel, beschr, pad, root, "style.css", og) +
            f'<body><a class="skip" href="#inhoud">Naar de inhoud</a><div class="wrap">'
            f'<header class="kop"><a class="logo" href="{root}index.html">Wat zei de <span>Kamer?</span></a>'
            f'<nav aria-label="Hoofdmenu">{nav}</nav><p class="werk">{S.WERKZIN}</p></header>{inhoud}'
            f'<footer><p>Gemaakt door {naam} met de open data van de Tweede Kamer. Geen officiële site van de Tweede Kamer.</p>'
            f'<p>Samenvattingen zijn geschreven door een AI-model en nagelezen tegen het verslag. Citaten zijn letterlijk en automatisch gecontroleerd. '
            f'De figuren zijn getekend naar portretten; het zijn geen foto\'s.</p>'
            f'<p>Fout gezien? Meld het via {contact}. · <a href="{root}zo-werken-we.html">Zo werken we</a> · <a href="{root}feed.xml">RSS</a></p></footer>'
            f'</div></body></html>')


def citaat(c, root, video, deel, kort=False):
    p = c["persoon"]
    rol = e(p.label_fractie() if p and p.fractie_code else c["partij"])
    links = [f'<a href="{root}verslag/{deel.slug}.html#b{c["beurt"]}">Lees in het verslag</a>']
    if video:
        links.insert(0, f'<a href="{e(c["video"])}" rel="noopener">▶ {e(c["tijd"].replace(":", "."))} uur · Bekijk dit moment (Debat Direct)</a>')
    return (f'<figure class="cit" style="margin:0"><blockquote data-citaat="{deel.id}#{c["beurt"]}">“{e(S.citaat_weergave(c["citaat"]))}”</blockquote>'
            f'<div class="wieb">{S.fig(p, "fg", root=root)}<figcaption class="wie"><b>{e(c["naam"])}</b><span>{rol}</span></figcaption></div>'
            + ("" if kort else f'<p class="links">{"".join(links)}</p>') + "</figure>")


def kaart(x, root, kop="h3", link=None, kort=False, ook_anker=None):
    k = x.kaart
    vraag = f'<a href="{link}">{e(k["vraag"])}</a>' if link else e(k["vraag"])
    paar = "".join(citaat(c, root, k["video"], x, kort) for c in k["citaten"])
    noot = ""
    if not kort:
        if len(k["citaten"]) < 2:
            noot = '<p class="noot">In dit debat stonden geen twee sprekers duidelijk tegenover elkaar; daarom één citaat.</p>'
        elif k["geen_botsing"]:
            noot = '<p class="noot">Deze twee sprekers waren het niet duidelijk oneens; ze lieten elk een eigen kant van het onderwerp zien.</p>'
        if k["video"]:
            noot += '<p class="noot">Videolinks openen Debat Direct, de site van de Tweede Kamer.</p>'
    ond = S.onderwerpen_regel(x)
    ook = S.ook_aan_het_woord(x, root, ook_anker) if ook_anker else ""
    return f'<{kop} class="vraag">{vraag}</{kop}>' + (f'<p class="noot">{e(ond)}</p>' if ond else "") + f'<div class="paar">{paar}</div>{noot}{ook}'


def stand(ms):
    a, v, o = S.moties_telling(ms)
    delen = [(a, "aangenomen"), (v, "verworpen"), (o, "zonder uitslag in onze gegevens")]
    return '<div class="stand">' + "".join(f'<div><b>{n}</b> {t}</div>' for n, t in delen if n) + "</div>"


def periode(o):
    a, b = o.debatten[0].datum, o.debatten[-1].datum
    return M.datum_lang(a) if a == b else f"{M.datum_lang(a)} tot en met {M.datum_lang(b)}"


def onderwerpen():
    return [o for o in M.onderwerpen() if not all(d.is_stemmingen for d in o.debatten)]


def home(U):
    kaarten = []
    for o in onderwerpen():
        href = f"onderwerp/{o.slug}.html"
        laatste_kaart = next((d.kaart for d in reversed(o.debatten) if d.kaart), None)
        links_ = (f'<div>{kaart(laatste_kaart, "", "h3", f"debat/{laatste_kaart.debat.slug}.html", kort=False)}</div>' if laatste_kaart else
                  f'<div><p>{e(o.debatten[-1].titel)}</p>{A.stapel(o.debatten[-1].personen(), "")}</div>')
        mini = "".join(f'<li><b>{M.datum_lang(d.datum)}</b>{e(d.soort_label)}' + (f", {len(d.delen)} delen" if len(d.delen) > 1 else "") + "</li>" for d in o.debatten)
        ms = o.moties
        mot = (f'<p class="tel">{len(ms)} {"motie" if len(ms) == 1 else "moties"} (verzoeken aan de regering)</p>{stand(ms)}' if ms else '<p class="sub">Geen moties in onze gegevens.</p>')
        kaarten.append(
            f'<li class="ok"><div class="okop"><p class="sub">{periode(o)} · {len(o.debatten)} {"debat" if len(o.debatten) == 1 else "debatten"}</p>'
            f'<h2><a href="{href}">{e(o.titel)}</a></h2></div><div class="okin">{links_}'
            f'<div><ol class="mini">{mini}</ol>{mot}<a class="verder" href="{href}">Bekijk de tijdlijn en hoe het afliep</a></div></div></li>')
    stem = [d for d in M.debatten() if d.is_stemmingen]
    stem_html = "".join(f'<li><a href="debat/{d.slug}.html">{M.datum_lang(d.datum, dag=True)}, {A.tijd_nl(d.begin)} uur</a></li>' for d in stem)
    inhoud = (f'<main id="inhoud"><div class="lees"><h1>Waar de Kamer over sprak</h1>'
              f'<p class="sub">Elk onderwerp met alle debatten erover op een tijdlijn, en hoe over de moties gestemd is. Het onderwerp waarover het laatst gedebatteerd is, staat bovenaan. '
              f'Wat letterlijk gezegd is, staat achter een dikke zwarte streep met het woord “Letterlijk” erboven.</p></div>'
              f'<ol class="lijst">{"".join(kaarten)}</ol>'
              f'<section class="blok"><h2>Stemmingsrondes</h2><p class="sub">De momenten waarop de Kamer stemde. De uitslag van elke motie staat bij het onderwerp waar ze bij hoort.</p><ul class="stemrondes">{stem_html}</ul></section></main>')
    U.schrijf("index.html", shell(f"{S.NAAM} Debatten uit de Tweede Kamer per onderwerp", S.WERKZIN + " Per onderwerp alle debatten op een tijdlijn, met de moties en de uitslag.",
                                  "", "", inhoud, actief="index.html"))


def onderwerp_pagina(U, o):
    root = "../"
    items = []
    for d in o.debatten:
        href = f"{root}debat/{d.slug}.html"
        if d.kaart:
            inh = f'<div class="kader">{kaart(d.kaart, root, "h4", href)}</div>'
        else:
            inh = f'<div class="kader"><p><a href="{href}">{e(d.titel)}</a></p>{A.stapel(d.personen(), root)}</div>'
        delen = f" · {len(d.delen)} delen" if len(d.delen) > 1 else ""
        items.append(f'<li class="tl"><p class="tld">{M.datum_lang(d.datum, dag=True)} · {A.tijd_nl(d.begin)} uur</p>'
                     f'<h3><a href="{href}">{e(d.titel_agenda)}</a></h3><p class="sub">{e(d.soort_label)}{delen}</p>{inh}</li>')
        if d.moties:
            items.append(f'<li class="tl mot"><p class="tld">Moties uit dit debat</p><p>{e(S.afloop_tekst(d))}</p>'
                         f'<details class="ml"><summary>Alle {len(d.moties)} moties, met wie voor en tegen stemde</summary>{S.moties_lijst(d, root, "h4")}</details></li>')
    ms = o.moties
    wet = next((S.wet_zin(d) for d in o.debatten if S.wet_zin(d)), "")
    hoe = (f'<p class="groot">Over {len(ms)} {"motie" if len(ms) == 1 else "moties"} uit {"dit debat" if len(o.debatten) == 1 else "deze debatten"}:</p>{stand(ms)}' if ms
           else f'<p class="groot">{e(S.afloop_tekst(o.debatten[-1]))}</p>')
    if ms:
        hoe += '<p class="noot">Een aangenomen motie is een verzoek aan de regering, geen wet of besluit. De datum van de stemming staat niet in onze gegevens; daarom staan de moties na hun debat.</p>'
    if wet:
        hoe = f'<p class="groot">{e(wet)}</p>' + hoe.replace('class="groot"', 'class=""', 1)
    vragen = [(d, d.kaart.kaart["vraag"]) for d in o.debatten if d.kaart]
    dt = o.dossier_titels
    waar = ("".join(f'<p>Kamerstuk {e(k)}: {e(t)}.</p>' for k, t in dt.items() if t) if dt else f"<p>{e(o.debatten[-1].titel)}</p>")
    waar += f'<p class="sub">{len(o.debatten)} {"debat" if len(o.debatten) == 1 else "debatten"} op de tijdlijn hieronder; bij elk debat de vraag waar het om draaide.</p>'
    inhoud = (f'<main id="inhoud"><p class="krumel"><a href="{root}index.html">Onderwerpen</a></p>'
              f'<header class="dkop"><p class="dmeta">{periode(o)} · {len(o.debatten)} {"debat" if len(o.debatten) == 1 else "debatten"}'
              + (f' · Kamerstuk {e(", ".join(o.dossiers))}' if o.dossiers else "") + f'</p><h1>{e(o.titel)}</h1></header>'
              f'<section class="afloop" aria-label="Waar ging het om en hoe liep het af"><div><h2>Waar ging het om</h2>{waar}</div><div><h2>Hoe liep het af</h2>{hoe}</div></section>'
              f'<section class="blok"><h2>Tijdlijn</h2><p class="sub">Oudste eerst. Na elk debat de moties die erin zijn ingediend.</p><ol class="tijdlijn">{"".join(items)}</ol></section>'
              f'<section class="blok"><h2>Uitleg</h2>{S.uitleg_lijst(S.uitleg_voor(o.debatten[-1]))}</section></main>')
    U.schrijf(f"onderwerp/{o.slug}.html", shell(f"{o.titel} – {S.NAAM}", f"Alle debatten over {o.titel} op een tijdlijn, met de moties en de uitslag.",
                                                f"onderwerp/{o.slug}.html", root, inhoud, og=f"og/{o.debatten[-1].slug}.png"))


def kop(d, titel, root, x=None):
    o = getattr(d, "onderwerp_obj", None)
    kr = (f'<a href="{root}onderwerp/{o.slug}.html">{e(o.titel)}</a>' if o and not d.is_stemmingen and not d.is_vragenuur else f'<a href="{root}index.html">Onderwerpen</a>')
    if x:
        kr += f' › <a href="{root}debat/{d.slug}.html">{M.datum_lang(d.datum)}</a>'
    meta = [M.datum_lang(d.datum, dag=True), f"{A.tijd_nl(x.begin if x else d.begin)} uur", d.soort_label]
    return (f'<p class="krumel">{kr}</p><header class="dkop"><p class="dmeta">{" · ".join(e(m) for m in meta)}'
            f'{" <span class=voorl>voorlopig verslag</span>" if d.voorlopig else ""}</p><h1>{e(titel)}</h1></header>')


def afloop(d, root, waar, kop_waar="Waar ging het om", kop_hoe="Hoe liep het af", deel=False):
    hoe = S.hoe_liep_het_af(d, f"{root}debat/{d.slug}.html#moties" if d.moties else None, deel=deel)
    if d.moties and not deel:
        hoe = hoe.replace('</p>', '</p>' + stand(d.moties), 1) if not S.wet_zin(d) else hoe
    return f'<section class="afloop"><div><h2>{kop_waar}</h2>{waar}</div><div><h2>{kop_hoe}</h2>{hoe}</div></section>'


def tekst_deel(x, root, rest=""):
    uit = []
    if x.kaart:
        uit.append(f'<section class="blok kader">{kaart(x, root, "h2", ook_anker="#standpunten")}</section>')
    if x.pagina and rest:
        uit.append(f'<section class="blok"><h2>Meer over {"dit deel" if x.van > 1 else "dit debat"}</h2>{S.alineas(rest, x.pagina["woorden"])}</section>')
    if x.pagina:
        uit.append(S.oud_verslag(x))
        uit.append(f'<section class="blok" id="standpunten"><h2>Wat de sprekers zeiden</h2><p class="noot">Per spreker, in de volgorde waarin ze spraken, met het aantal zetels van de fractie en of die in de coalitie zit.</p>{S.standpunten(x, root)}</section>')
    else:
        uit.append(f'<section class="blok" id="standpunten"><h2>Wie spraken</h2><p class="noot">Voor {"dit deel" if x.van > 1 else "dit debat"} is geen samenvatting geschreven; het verslag staat er wel.</p>{A.sprekers_lijst(x, root)}</section>')
    return "".join(uit)


def moties_sectie(d, root):
    if not d.moties:
        return ""
    return (f'<section class="blok" id="moties"><h2>Moties</h2><p class="noot">Eerst de aangenomen, dan de verworpen moties, dan die zonder uitslag in onze gegevens.</p>'
            f'{S.moties_lijst(d, root, "h3")}</section>')


def buren(d, root):
    o = getattr(d, "onderwerp_obj", None)
    if not o or len(o.debatten) < 2:
        return ""
    i = o.debatten.index(d)
    v = o.debatten[i - 1] if i else None
    n = o.debatten[i + 1] if i + 1 < len(o.debatten) else None
    return (f'<nav class="deelnav" aria-label="Eerder en later in dit onderwerp">'
            + (f'<a href="{root}debat/{v.slug}.html">← Eerder: {M.datum_lang(v.datum)}</a>' if v else "<span></span>")
            + (f'<a href="{root}debat/{n.slug}.html">Later: {M.datum_lang(n.datum)} →</a>' if n else "<span></span>") + "</nav>")


def debat_pagina(U, d):
    root = "../"
    if len(d.delen) == 1 and d.van == 1:
        x = d.delen[0]
        eerste, rest = S.eerste_alinea(x.pagina["samenvatting"]) if x.pagina else ("", "")
        waar = (S.alineas(eerste, x.pagina["woorden"]) if x.pagina else f'<p>{e(d.onderwerp)}.</p>')
        hoofd = (kop(d, d.titel, root) + buren(d, root) +
                 f'<div class="kolommen"><div class="blok">{afloop(d, root, waar)}{tekst_deel(x, root, rest)}{moties_sectie(d, root)}</div>{A.zijkolom(d, x, root)}</div>')
    else:
        k = d.kaart
        waar = (f'<p>Dit debat is in {d.van} delen geknipt, langs de rondes van het debat; <a href="#delen">elk deel heeft een eigen samenvatting</a>.</p>')
        kk = f'<section class="blok kader"><p class="tld">Uit deel {k.nummer}: {e(k.fase)}</p>{kaart(k, root, "h2", ook_anker="#sprekers")}</section>' if k else ""
        hoofd = (kop(d, d.titel_agenda, root) + buren(d, root) +
                 f'<div class="kolommen"><div class="blok">{afloop(d, root, waar)}{kk}<section class="blok" id="delen"><h2>De delen van dit debat</h2>{A.delen_lijst(d, root)}</section>{moties_sectie(d, root)}'
                 f'<section class="blok" id="sprekers"><h2>Alle sprekers</h2>{A.sprekers_lijst_debat(d, root)}</section></div>{A.zijkolom(d, None, root)}</div>')
        for x in d.delen:
            deel_pagina(U, d, x)
    U.schrijf(f"debat/{d.slug}.html", shell(f"{d.titel} – {S.NAAM}", S.beschrijving(d), f"debat/{d.slug}.html", root,
                                            f'<main id="inhoud">{hoofd}</main>', og=f"og/{d.slug}.png"))


def deel_pagina(U, d, x):
    root = "../"
    i = d.delen.index(x)
    v = d.delen[i - 1] if i else None
    n = d.delen[i + 1] if i + 1 < len(d.delen) else None
    nav = (f'<nav class="deelnav" aria-label="Vorige en volgende deel">' + (f'<a href="{v.slug}.html">← Deel {v.nummer}</a>' if v else "<span></span>")
           + f'<span>Deel {x.nummer} van {x.van}</span>' + (f'<a href="{n.slug}.html">Deel {n.nummer} →</a>' if n else "<span></span>") + "</nav>")
    eerste, rest = S.eerste_alinea(x.pagina["samenvatting"]) if x.pagina else ("", "")
    waar = (S.alineas(eerste, x.pagina["woorden"]) if x.pagina else
            '<p>Voor dit deel is geen samenvatting geschreven. Hieronder staan de sprekers; het verslag staat er wel.</p>')
    inhoud = (kop(d, x.titel, root, x) + f'<p class="dmeta">Deel {x.nummer} van {x.van} · {e(x.fase)}</p>' + nav +
              f'<div class="kolommen"><div class="blok">{afloop(d, root, waar, "Waar ging dit deel over", "Hoe liep het debat af", deel=True)}{tekst_deel(x, root, rest)}'
              f'<section class="blok"><h2>Alle delen van dit debat</h2>{A.delen_lijst(d, root, x)}</section></div>{A.zijkolom(d, x, root)}</div>' + nav)
    U.schrijf(f"debat/{x.slug}.html", shell(f"{x.titel} – {d.titel_agenda} (deel {x.nummer}) – {S.NAAM}", S.beschrijving(d, x),
                                            f"debat/{x.slug}.html", root, f'<main id="inhoud">{inhoud}</main>', og=f"og/{d.slug}.png"))


def verslag_paginas(U, d):
    for x in d.delen:
        body = S.verslag_body(x, "../", f"../debat/{x.slug}.html", "Terug naar de samenvatting")
        U.schrijf(f"verslag/{x.slug}.html", shell(f"Verslag: {d.titel_agenda}{f' (deel {x.nummer})' if x.van > 1 else ''} – {S.NAAM}",
                                                  f"Het letterlijke verslag van {d.titel_agenda}, {M.datum_lang(d.datum)}.",
                                                  f"verslag/{x.slug}.html", "../", body, og=f"og/{d.slug}.png"))


def moties_pagina(U):
    blokken = []
    alle = []
    for o in onderwerpen():
        ds = [d for d in o.debatten if d.moties]
        if not ds:
            continue
        alle += o.moties
        blokken.append(f'<section class="blok"><h2><a href="onderwerp/{o.slug}.html">{e(o.titel)}</a></h2>{stand(o.moties)}'
                       + "".join(f'<details class="ml"><summary>{M.datum_lang(d.datum)}: {e(d.soort_label)} ({len(d.moties)} moties)</summary>{S.moties_lijst(d, "", "h3")}</details>' for d in ds)
                       + "</section>")
    a, v, o_ = S.moties_telling(alle)
    inhoud = (f'<main id="inhoud"><h1>Moties en uitslagen</h1><div class="lees"><p>Alle moties per onderwerp, onderwerp met de laatste activiteit eerst. Samen {len(alle)} moties: {a} aangenomen, {v} verworpen'
              f'{f", van {o_} staat geen uitslag in onze gegevens" if o_ else ""}.</p><p class="noot">{e(S.UITLEG["motie"][1])}</p>'
              f'<p class="noot">Per Kamerlid of partij zien hoe er gestemd is? Dat kan op <a href="https://partijgedrag.nl/" rel="noopener">Partijgedrag.nl</a>.</p></div>{"".join(blokken)}</main>')
    U.schrijf("moties.html", shell(f"Moties en uitslagen – {S.NAAM}", "Alle moties per onderwerp, met de uitslag en de zetels per fractie.",
                                   "moties.html", "", inhoud, actief="moties.html"))


def zo_werken_we(U):
    regels = [("In deze variant", [
        "<b>Onderwerpen:</b> debatten met dezelfde agendatitel horen bij één onderwerp (\"Voortzetting\" telt niet mee), en debatten waarvan moties bij hetzelfde Kamerstuk horen ook. Verzameldossiers (zoals de Raad Buitenlandse Zaken, klimaatbeleid, Afrikabeleid en de hoofdstukken van de begroting) verbinden geen debatten. Een vragenuur en stemmingen zijn nooit samen één onderwerp.",
        "<b>Volgorde van onderwerpen:</b> het onderwerp waarover het laatst gedebatteerd is, staat bovenaan.",
        "<b>Tijdlijn:</b> oudste debat eerst; na elk debat de moties die erin zijn ingediend. Omdat de datum van de stemming niet in onze gegevens staat, staat een uitslag bij het debat en niet op de dag van de stemming.",
        "<b>Op de voorpagina</b> toont elk onderwerp de kaart van het laatste debat met een kaart; anders de titel en de sprekers van het laatste debat.",
        "<b>Een citaat</b> staat altijd achter een dikke zwarte streep met het woord “Letterlijk” erboven, met het figuur van de spreker ernaast. Tekst die deze site zelf schrijft, staat nooit achter zo'n streep.",
    ])]
    inhoud = f'<main id="inhoud" class="zw"><h1>Zo werken we</h1><p class="lees">{S.WERKZIN}</p>{S.zo_werken_we(regels)}</main>'
    U.schrijf("zo-werken-we.html", shell(f"Zo werken we – {S.NAAM}", "Wie deze site maakt, hoe de teksten ontstaan en welke vaste regels we volgen.",
                                         "zo-werken-we.html", "", inhoud, actief="zo-werken-we.html"))


def bouw():
    U = Uitvoer("b")
    home(U)
    for o in onderwerpen():
        onderwerp_pagina(U, o)
    for d in M.debatten():
        debat_pagina(U, d)
        verslag_paginas(U, d)
    moties_pagina(U)
    zo_werken_we(U)
    items = [(d.titel, f"debat/{d.slug}.html", S.beschrijving(d), d.begin) for d in M.debatten()]
    U.afronden(CSS, items, "#d8ecec")
    return U


if __name__ == "__main__":
    U = bouw()
    print("B gebouwd:", len(U.paden), "pagina's in", U.dir)
