"""Variant C: de kaart is de pagina. Gebouwd voor iemand die op een telefoon via een gedeelde kaart binnenkomt en de
voorpagina nooit ziet. Elke debatpagina begint met de kaart op schermvullende hoogte (de vraag, twee citaten, figuren),
gevolgd door korte genummerde hoofdstukken die elk één vraag beantwoorden, en eindigt met wie dit maakt. Onderaan staat
een vaste balk met Delen en Volgende debat. Een citaat is altijd een wit kaartje met het label "Letterlijk gezegd"."""
from kern import model as M, stukken as S
from kern.bouwen import Uitvoer
import a as A

e = S.e
CSS = r"""
/* ---------- variant C: de kaart is de pagina ---------- */
:root{--k:#1d1b2e;--kt:#fbfaf7;--geel:#ffe066}
body{padding-bottom:78px}
.wrap{max-width:720px;margin:0 auto;padding:0 max(14px,env(safe-area-inset-left)) 24px max(14px,env(safe-area-inset-right))}
/* de kaart */
.kaart{background:var(--k);color:var(--kt);min-height:100svh;margin:0 calc(-1*max(14px,env(safe-area-inset-left)));padding:14px max(14px,env(safe-area-inset-left)) 20px;display:flex;flex-direction:column;gap:14px}
@media (min-width:760px){.kaart{min-height:auto;margin:16px 0 0;border-radius:22px;padding:22px 26px}}
.kaart a{color:var(--kt)}
.kbalk{display:flex;justify-content:space-between;align-items:center;gap:10px;font-size:15px}
.kbalk .logo{font-weight:700;text-decoration:none;font-size:17px}
.kbalk .logo i{font-style:normal;color:var(--geel)}
.kmeta{font-size:14px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#c9c6dc}
.kaart h1{font-size:clamp(1.65rem,7vw,2.5rem);line-height:1.12;color:var(--geel)}
.kaart .agt{font-size:15px;color:#c9c6dc}
.cc{display:grid;grid-template-columns:60px minmax(0,1fr);gap:10px;align-items:start}
.cc .fg{width:60px;height:60px;border-color:var(--kt);border-width:2.5px}
.ckaart{background:#fff;color:#1d1b2e;border-radius:4px 18px 18px 18px;padding:10px 14px 12px;position:relative;min-width:0}
.ckaart .lab{display:inline-block;background:#1d1b2e;color:#fff;font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;border-radius:4px;padding:1px 8px;margin-bottom:6px}
.ckaart blockquote{margin:0;font-size:18px;line-height:1.42}
.ckaart .wie{margin-top:8px;font-size:15px;color:#3c3a50}
.ckaart .wie b{color:#1d1b2e}
.ckaart .ln{display:flex;flex-wrap:wrap;gap:4px 14px;margin-top:8px;font-size:15px;font-weight:700}
.ckaart .ln a{color:#2f3fb8}
.knoot{font-size:14px;color:#c9c6dc}
.sprekers{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px;list-style:none;padding:0;margin:0}
.sprekers li{display:flex;flex-direction:column;align-items:center;text-align:center;gap:4px;font-size:14px}
.sprekers .fg{width:64px;height:64px;border-color:var(--kt)}
.sprekers span{color:#c9c6dc}
.kafloop{margin-top:auto;background:rgba(255,255,255,.08);border-radius:14px;padding:12px 14px;display:flex;flex-direction:column;gap:4px}
.kafloop b{color:var(--geel)}
.kafloop a{font-weight:700}
/* hoofdstukken */
main{display:flex;flex-direction:column}
.hs{padding:26px 0;border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:12px;scroll-margin-top:8px}
.hs>h2{font-size:23px;display:flex;gap:10px;align-items:baseline}
.hs>h2 .nr{display:inline-grid;place-items:center;min-width:32px;height:32px;border-radius:50%;background:var(--ink);color:var(--paper);font-size:17px;flex:none}
.groot{font-size:19px;font-weight:700;line-height:1.35}
.noot{font-size:15px;color:var(--muted)}
.inhoudlijst{display:flex;flex-wrap:wrap;gap:8px;list-style:none;margin:0;padding:16px 0 0}
.inhoudlijst a{display:inline-block;border:1.5px solid var(--line);border-radius:999px;padding:4px 12px;font-size:15px;text-decoration:none;color:var(--ink)}
ol.delen{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:10px}
ol.delen li{display:grid;grid-template-columns:auto 1fr;gap:2px 12px;align-items:baseline}
ol.delen .dn{font-weight:700;color:var(--muted)}
ol.delen .df{grid-column:2;font-size:14px;color:var(--muted)}
ol.delen li[aria-current] a{color:var(--ink);font-weight:700}
.zelfde{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.zelfde a{display:flex;flex-direction:column;gap:2px;border:1.5px solid var(--line);border-radius:12px;padding:10px 14px;text-decoration:none;color:var(--ink);background:var(--panel)}
.zelfde a span{font-size:14px;color:var(--muted)}
.zelfde a b{font-size:17px}
.wat{background:var(--tone);border-radius:16px;padding:18px;margin-top:26px;display:flex;flex-direction:column;gap:8px;font-size:16px}
.wat h2{font-size:20px}
/* vaste balk */
.balk-onder{position:fixed;left:0;right:0;bottom:0;background:var(--panel);border-top:2px solid var(--ink);padding:8px max(14px,env(safe-area-inset-left)) calc(8px + env(safe-area-inset-bottom));display:flex;gap:10px;justify-content:center;z-index:5}
.balk-onder a,.balk-onder button{font:inherit;font-weight:700;font-size:16px;border-radius:999px;padding:8px 16px;border:2px solid var(--ink);background:var(--paper);color:var(--ink);text-decoration:none;cursor:pointer;flex:1;max-width:260px;text-align:center}
.balk-onder .vol{background:var(--ink);color:var(--paper)}
.gekopieerd{position:fixed;bottom:84px;left:50%;transform:translateX(-50%);background:var(--ink);color:var(--paper);padding:8px 14px;border-radius:8px;font-size:15px}
/* voorpagina: stapel kaarten */
.stapelk{display:flex;flex-direction:column;gap:18px;list-style:none;margin:0;padding:0}
.stapelk .kaart{min-height:auto;margin:0;border-radius:20px;padding:18px}
.stapelk h2{font-size:clamp(1.35rem,5.5vw,1.9rem);line-height:1.15;color:var(--geel)}
.stapelk h2 a{color:var(--geel);text-decoration:none}
.top{display:flex;flex-direction:column;gap:8px;padding:20px 0 14px}
.top .logo{font-size:26px;font-weight:700;color:var(--ink);text-decoration:none}
.dagkop{font-size:15px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);margin:14px 0 -6px}
.zw{display:flex;flex-direction:column;gap:22px;padding-top:18px}
.zw section{display:flex;flex-direction:column;gap:8px}
.zw h2{font-size:23px}.zw h3{font-size:19px}
.zw ul{margin:0;padding-left:1.2em;display:flex;flex-direction:column;gap:6px}
.verslag{padding-top:16px}
"""

DEEL_JS = """<script>
(function(){var b=document.getElementById('deel');if(!b)return;b.addEventListener('click',function(){var u=location.href,t=document.title;
if(navigator.share){navigator.share({title:t,url:u}).catch(function(){});return;}
function klaar(){var m=document.createElement('div');m.className='gekopieerd';m.setAttribute('role','status');m.textContent='Link gekopieerd';document.body.appendChild(m);setTimeout(function(){m.remove()},2200);}
if(navigator.clipboard){navigator.clipboard.writeText(u).then(klaar,function(){prompt('Kopieer deze link',u)});}else{prompt('Kopieer deze link',u);}});})();
</script>"""


def volgorde():
    """Vaste volgorde voor 'Volgende debat': chronologisch van nieuw naar oud, zoals de voorpagina."""
    return [d for _, ds in M.dagen() for d in ds]


def shell(titel, beschr, pad, root, inhoud, og=None, volgende=None, balk=True):
    naam, contact = S.afzender()
    balk_html = ""
    if balk:
        vol = (f'<a class="vol" href="{volgende}">Volgende →</a>' if volgende else f'<a class="vol" href="{root}index.html">Alle debatten</a>')
        balk_html = f'<nav class="balk-onder" aria-label="Delen en verder"><button type="button" id="deel">Delen</button>{vol}</nav>'
    return (S.head(titel, beschr, pad, root, "style.css", og) +
            f'<body><a class="skip" href="#inhoud">Naar de inhoud</a><div class="wrap">{inhoud}</div>{balk_html}{DEEL_JS if balk else ""}</body></html>')


def wat_is_dit(root):
    naam, contact = S.afzender()
    return (f'<section class="wat" id="wat-is-dit"><h2>Wat is dit?</h2>'
            f'<p><b>{S.NAAM}</b> zet debatten uit de Tweede Kamer om in gewone taal, met de letterlijke woorden erbij. Gemaakt door {naam}; geen site van de Kamer of van een partij.</p>'
            f'<p>De samenvattingen zijn geschreven door een AI-model en nagelezen tegen het verslag. Elk citaat is automatisch gecontroleerd: het staat woord voor woord in het verslag. '
            f'De figuren zijn getekend naar portretten; het zijn geen foto\'s.</p>'
            f'<p>Fout gezien? Meld het via {contact}.</p>'
            f'<p><a href="{root}zo-werken-we.html">Zo werken we</a> · <a href="{root}index.html">Alle debatten</a> · <a href="{root}uitslagen.html">Alle uitslagen</a></p></section>')


def citaat(c, root, video, deel):
    p = c["persoon"]
    rol = e(p.label_fractie() if p and p.fractie_code else c["partij"])
    ln = [f'<a href="{root}verslag/{deel.slug}.html#b{c["beurt"]}">Lees in het verslag</a>']
    if video:
        ln.insert(0, f'<a href="{e(c["video"])}" rel="noopener">▶ {e(c["tijd"].replace(":", "."))} uur · Bekijk dit moment (Debat Direct)</a>')
    return (f'<figure class="cc" style="margin:0">{S.fig(p, "fg", root=root)}<div class="ckaart"><span class="lab">Letterlijk gezegd</span>'
            f'<blockquote data-citaat="{deel.id}#{c["beurt"]}">“{e(S.citaat_weergave(c["citaat"]))}”</blockquote>'
            f'<figcaption class="wie"><b>{e(c["naam"])}</b> · {rol}</figcaption><p class="ln">{"".join(ln)}</p></div></figure>')


def afloop_kort(d, root, hier=True):
    if d.is_vragenuur or d.is_stemmingen:
        t = S.afloop_tekst(d).split(". ")[0] + "."
    elif d.moties:
        a, v, o = S.moties_telling(d.moties)
        delen = [f"{a} aangenomen" if a else "", f"{v} verworpen" if v else "", f"{o} zonder uitslag in onze gegevens" if o else ""]
        t = f"{len(d.moties)} {'motie' if len(d.moties) == 1 else 'moties'}: " + ", ".join(x for x in delen if x) + "."
    else:
        t = "In onze gegevens staan geen moties bij dit debat."
    href = "#afloop" if hier else f"{root}debat/{d.slug}.html#afloop"
    return f'<div class="kafloop"><span>Hoe liep het af?</span><b>{e(t)}</b><a href="{href}">Lees verder ↓</a></div>'


def kaart(d, x, root, h="h1", link=None):
    """De kaart: soort en datum, vraag (of titel), twee citaten of de sprekers, en de korte afloop."""
    meta = f'{e(d.soort_label)} · {M.datum_lang(d.datum)}' + (f' · deel {x.nummer} van {x.van}' if x and x.van > 1 else "")
    kx = x.kaart if x and x.kaart else None
    bron = x if kx else None
    if not kx and (x is None) and d.kaart:
        bron = d.kaart
    if bron:
        k = bron.kaart
        titel = k["vraag"]
        inh = "".join(citaat(c, root, k["video"], bron) for c in k["citaten"])
        if len(k["citaten"]) < 2:
            inh += '<p class="knoot">In dit debat stonden geen twee sprekers duidelijk tegenover elkaar; daarom één citaat.</p>'
        elif k["geen_botsing"]:
            inh += '<p class="knoot">Deze twee waren het niet duidelijk oneens; ze lieten elk een eigen kant van het onderwerp zien.</p>'
        if k["video"]:
            inh += '<p class="knoot">Videolinks openen Debat Direct, de site van de Tweede Kamer.</p>'
        if x is None and bron.van > 1:
            inh = f'<p class="knoot">Uit deel {bron.nummer}: {e(bron.fase)}</p>' + inh
    else:
        titel = (x.titel if x else d.titel)
        ps = (x.personen() if x else d.personen())
        inh = ('<ul class="sprekers" aria-label="Sprekers">' + "".join(
            f'<li>{S.fig(p, "fg", root=root)}<b>{e(p.naam)}</b><span>{e(p.label_fractie() if p.fractie_code else p.functie)}</span></li>' for p in ps[:9])
               + "</ul>" + (f'<p class="knoot">en {len(ps) - 9} anderen</p>' if len(ps) > 9 else ""))
    kop = f'<a href="{link}">{e(titel)}</a>' if link else e(titel)
    agt = f'<p class="agt">{e(d.titel_agenda)}</p>' if d.titel_agenda.lower() not in titel.lower() and d.titel_agenda.lower() not in d.soort_label.lower() else ""
    return (f'<{h}>{kop}</{h}>' if h != "h1" else f'<h1>{kop}</h1>'), meta, agt, inh


def debat_kaart(d, x, root):
    h1, meta, agt, inh = kaart(d, x, root)
    return (f'<header class="kaart"><div class="kbalk"><a class="logo" href="{root}index.html">Wat zei de <i>Kamer?</i></a><a href="#wat-is-dit">Wat is dit?</a></div>'
            f'<p class="kmeta">{meta}{" · voorlopig verslag" if d.voorlopig else ""}</p>{h1}{agt}{inh}{afloop_kort(d, root)}</header>')


def hs(nr, titel, inhoud, id_=""):
    return f'<section class="hs"{f" id={id_!r}" if id_ else ""}><h2><span class="nr" aria-hidden="true">{nr}</span>{e(titel)}</h2>{inhoud}</section>'


def hoofdstukken(d, x, root):
    """Genummerde hoofdstukken. x is het deel (of None voor de pagina van een debat in delen)."""
    uit = []
    n = 1
    hoe = f'<p class="groot">{e(S.afloop_tekst(d))}</p>'
    if d.moties:
        hoe += '<p class="noot">Een aangenomen motie is een verzoek aan de regering, geen wet of besluit.</p>'
        if x and d.van > 1:
            hoe += f'<p><a href="{root}debat/{d.slug}.html#afloop">Alle {len(d.moties)} moties, met wie voor en tegen stemde</a></p>'
        else:
            hoe += f'<details><summary>Alle {len(d.moties)} moties, met wie voor en tegen stemde</summary>{S.moties_lijst(d, root, "h3")}</details>'
    if S.wet_zin(d):
        hoe += f'<p class="noot">{e(S.wet_zin(d))}</p>'
    if x and d.van > 1 and d.moties:
        hoe = f'<p class="noot">De moties horen bij het hele debat, niet bij één deel.</p>' + hoe
    uit.append(hs(n, "Hoe liep het af", hoe, "afloop")); n += 1
    if x:
        waar = (S.alineas(x.pagina["samenvatting"], x.pagina["woorden"]) + S.oud_verslag(x) + S.nagelezen(x) if x.pagina else
                '<p>Voor dit deel is (nog) geen samenvatting geschreven. Op de kaart staan de sprekers; in het verslag lees je alles wat ze zeiden.</p>')
        uit.append(hs(n, "Waar ging het om", waar, "waar")); n += 1
        if x.pagina and x.pagina["sprekers"]:
            uit.append(hs(n, "Wat zeiden de anderen", '<p class="noot">Elke spreker, in de volgorde waarin ze spraken, met het aantal zetels van de fractie en of die in de coalitie zit.</p>'
                          + S.standpunten(x, root), "standpunten")); n += 1
    if d.van > 1:
        uit.append(hs(n, "Dit debat in delen", f'<p>Lange debatten zijn geknipt langs de rondes van het debat. {"Je leest nu deel " + str(x.nummer) + "." if x else "Elk deel heeft een eigen pagina."}</p>'
                      + A.delen_lijst(d, root, x), "delen")); n += 1
    controle = (f'<p>Alles wat er gezegd is, staat letterlijk in het verslag, met per spreekbeurt een link naar de video.</p>'
                + ("".join(f'<p><a href="{root}verslag/{y.slug}.html">Verslag van {"deel " + str(y.nummer) if d.van > 1 else "dit debat"}</a></p>' for y in ([x] if x else d.delen))))
    uit.append(hs(n, "Controleer het zelf", controle, "controle")); n += 1
    woorden = S.woordenlijst(x.pagina["woorden"]) if x and x.pagina else ""
    uitleg = (f'<h3>Moeilijke woorden</h3>{woorden}' if woorden else "") + S.uitleg_lijst(S.uitleg_voor(d))
    uit.append(hs(n, "Wat betekent dat", uitleg, "uitleg")); n += 1
    zelfde = [y for y in M.debatten() if y.datum == d.datum and y is not d]
    if zelfde:
        li = "".join(f'<li><a href="{root}debat/{y.slug}.html"><span>{A.tijd_nl(y.begin)} uur · {e(y.soort_label)}</span><b>{e(y.vraag or y.titel)}</b></a></li>' for y in zelfde)
        uit.append(hs(n, f"Ook op {M.datum_lang(d.datum, dag=True)}", f'<ul class="zelfde">{li}</ul>', "dag")); n += 1
    inhoudsopgave = '<ul class="inhoudlijst" aria-label="Op deze pagina">' + "".join(
        f'<li><a href="#{i}">{t}</a></li>' for i, t in (("afloop", "Hoe liep het af"), ("waar", "Waar ging het om"), ("standpunten", "Wat zeiden de anderen"),
                                                         ("delen", "Delen"), ("controle", "Controleer"), ("uitleg", "Uitleg"))
        if f'id="{i}"' in "".join(uit) or f"id='{i}'" in "".join(uit)) + "</ul>"
    return inhoudsopgave + "".join(uit)


def volgende_van(d):
    v = volgorde()
    i = v.index(d)
    return v[i + 1] if i + 1 < len(v) else None


def debat_pagina(U, d):
    root = "../"
    vol = volgende_van(d)
    vhref = f"{root}debat/{vol.slug}.html" if vol else None
    if len(d.delen) == 1 and d.van == 1:
        x = d.delen[0]
        inhoud = debat_kaart(d, x, root) + f'<main id="inhoud">{hoofdstukken(d, x, root)}</main>' + wat_is_dit(root)
    else:
        inhoud = debat_kaart(d, None, root) + f'<main id="inhoud">{hoofdstukken(d, None, root)}</main>' + wat_is_dit(root)
        for x in d.delen:
            deel_pagina(U, d, x, vhref)
    U.schrijf(f"debat/{d.slug}.html", shell(f"{d.vraag or d.titel} – {S.NAAM}", S.beschrijving(d), f"debat/{d.slug}.html", root, inhoud,
                                            og=f"og/{d.slug}.png", volgende=vhref))


def deel_pagina(U, d, x, vhref):
    root = "../"
    i = d.delen.index(x)
    n = d.delen[i + 1] if i + 1 < len(d.delen) else None
    volgende = f"{n.slug}.html" if n else vhref
    inhoud = debat_kaart(d, x, root) + f'<main id="inhoud">{hoofdstukken(d, x, root)}</main>' + wat_is_dit(root)
    U.schrijf(f"debat/{x.slug}.html", shell(f"{x.kaart['vraag'] if x.kaart else x.titel} – {d.titel_agenda} (deel {x.nummer}) – {S.NAAM}",
                                            S.beschrijving(d, x), f"debat/{x.slug}.html", root, inhoud, og=f"og/{d.slug}.png",
                                            volgende=volgende))


def verslag_paginas(U, d):
    for x in d.delen:
        body = S.verslag_body(x, "../", f"../debat/{x.slug}.html", "Terug naar de kaart")
        U.schrijf(f"verslag/{x.slug}.html", shell(f"Verslag: {d.titel_agenda}{f' (deel {x.nummer})' if x.van > 1 else ''} – {S.NAAM}",
                                                  f"Het letterlijke verslag van {d.titel_agenda}, {M.datum_lang(d.datum)}.",
                                                  f"verslag/{x.slug}.html", "../", body, og=f"og/{d.slug}.png", balk=False))


def home(U):
    kaarten = []
    for datum, ds in M.dagen():
        kaarten.append(f'<li class="dagkop">{M.datum_lang(datum, dag=True)}</li>')
        for d in reversed(ds):  # binnen een dag: laatst begonnen eerst, zodat de hele stapel nieuw naar oud loopt
            href = f"debat/{d.slug}.html"
            h, meta, agt, inh = kaart(d, None, "", "h2", href)
            kaarten.append(f'<li><article class="kaart"><p class="kmeta">{meta}</p>{h}{agt}{inh}{afloop_kort(d, "", hier=False)}</article></li>')
    inhoud = (f'<header class="top"><a class="logo" href="index.html">Wat zei de Kamer?</a><p>{S.WERKZIN} Elke kaart is één debat: de vraag, wie er tegenover elkaar stonden en hoe het afliep. Tik op een vraag voor het hele verhaal.</p></header>'
              f'<main id="inhoud"><ol class="stapelk">{"".join(kaarten)}</ol></main>' + wat_is_dit(""))
    U.schrijf("index.html", shell(f"{S.NAAM} Debatten uit de Tweede Kamer in gewone taal", S.WERKZIN, "", "", inhoud, balk=False))


def uitslagen(U):
    ds = [d for d in volgorde() if d.moties]
    alle = [m for d in ds for m in d.moties]
    a, v, o = S.moties_telling(alle)
    blok = "".join(f'<section class="hs"><h2><a href="debat/{d.slug}.html">{e(d.vraag or d.titel)}</a></h2><p class="noot">{e(d.titel_agenda)} · {M.datum_lang(d.datum)}</p>'
                   f'<p class="groot">{e(S.afloop_tekst(d))}</p><details><summary>Alle moties</summary>{S.moties_lijst(d, "", "h3")}</details></section>' for d in ds)
    inhoud = (f'<header class="top"><a class="logo" href="index.html">Wat zei de Kamer?</a><h1>Alle uitslagen</h1>'
              f'<p>{len(alle)} moties uit de debatten op deze site: {a} aangenomen, {v} verworpen{f", van {o} staat geen uitslag in onze gegevens" if o else ""}. Nieuwste debat eerst.</p>'
              f'<p class="noot">{e(S.UITLEG["motie"][1])} Per partij of Kamerlid zien hoe er gestemd is? Dat kan op <a href="https://partijgedrag.nl/" rel="noopener">Partijgedrag.nl</a>.</p></header>'
              f'<main id="inhoud">{blok}</main>' + wat_is_dit(""))
    U.schrijf("uitslagen.html", shell(f"Alle uitslagen – {S.NAAM}", "Alle moties uit de debatten op deze site, met de uitslag.", "uitslagen.html", "", inhoud, balk=False))


def zo_werken_we(U):
    regels = [("In deze variant", [
        "<b>Elke debatpagina begint met de kaart</b>: de vraag, twee citaten met figuren en in één regel hoe het afliep. Een debat zonder kaart toont de titel en de figuren van de sprekers.",
        "<b>Daarna vaste hoofdstukken</b>, altijd in dezelfde volgorde: hoe liep het af, waar ging het om, wat zeiden de anderen, de delen, controleer het zelf, wat betekent dat, en de andere debatten van dezelfde dag.",
        "<b>Volgende debat</b> volgt de volgorde van de voorpagina: nieuwste dag eerst, binnen een dag het laatst begonnen debat eerst. Bij een debat in delen gaat Volgende eerst door de delen.",
        "<b>Een citaat</b> is altijd een wit kaartje met het label \"Letterlijk gezegd\", met het figuur van de spreker ernaast. Tekst die deze site zelf schrijft, staat nooit in zo'n kaartje.",
    ])]
    inhoud = (f'<header class="top"><a class="logo" href="index.html">Wat zei de Kamer?</a></header>'
              f'<main id="inhoud" class="zw"><h1>Zo werken we</h1><p>{S.WERKZIN}</p>{S.zo_werken_we(regels)}</main>')
    U.schrijf("zo-werken-we.html", shell(f"Zo werken we – {S.NAAM}", "Wie deze site maakt, hoe de teksten ontstaan en welke vaste regels we volgen.",
                                         "zo-werken-we.html", "", inhoud, balk=False))


def bouw():
    U = Uitvoer("c")
    home(U)
    for d in M.debatten():
        debat_pagina(U, d)
        verslag_paginas(U, d)
    uitslagen(U)
    zo_werken_we(U)
    items = [(d.vraag or d.titel, f"debat/{d.slug}.html", S.beschrijving(d), d.begin) for d in M.debatten()]
    U.afronden(CSS, items, "#ffe066")
    return U


if __name__ == "__main__":
    U = bouw()
    print("C gebouwd:", len(U.paden), "pagina's in", U.dir)
