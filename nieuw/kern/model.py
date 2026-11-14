"""Het datamodel voor de nieuwe site: leest data/ (alleen lezen) en nieuw/eigen/ en maakt er debatten,
delen, kaarten, moties, fracties en personen van. Geen AI, geen netwerk: alles volgt uit de bestanden.

Vaste regels (staan ook op "Zo werken we"):
- Een debat is alle agendapunten met hetzelfde ouder_id (lange debatten zijn in delen geknipt); anders één agendapunt.
- Kaart: data/proeftuin/botsing/<id>.json, versie a, of c als a een bijzaak is (zoals scripts/build.py kaart_versie()).
- Paginatekst: data/paginas/<id>.json, anders data/strips/<id>.json (alleen de waarde 'normaal').
- Een motie hoort bij het debat waarin haar eerste indiener sprak. Een motie die ook in andere agendapunten
  genoemd wordt (bijvoorbeeld bij Stemmingen of doordat een minister het nummer noemt), staat alleen bij dat debat.
"""
import json, re, unicodedata, urllib.parse
from datetime import datetime, date
from pathlib import Path
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
EIGEN = ROOT / "nieuw" / "eigen"
MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus",
           "september", "oktober", "november", "december"]
DAGEN = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
VOORLOPIG = {"Casco", "Ongecorrigeerd"}
# Makkelijke taal staat uit (besluit eigenaar). De teksten blijven in de data; zet op True om ze later te tonen.
MAKKELIJK = False

TUSSEN = {"van", "de", "der", "den", "het", "ter", "ten", "te", "in", "op", "'t", "la", "le", "du", "da", "di", "von", "vande"}


def lees(p):
    return json.loads(Path(p).read_text())


def norm(s):
    """Vergelijkbare tekst: gelijke aanhalingstekens en witruimte (zoals scripts/check.py)."""
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def slug(t, maxlen=70):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    if len(t) > maxlen:
        t = t[:maxlen].rsplit("-", 1)[0]
    return t


def datum_lang(iso, dag=False):
    j, m, d = iso[:10].split("-")
    s = f"{int(d)} {MAANDEN[int(m) - 1]} {j}"
    if dag:
        s = DAGEN[date(int(j), int(m), int(d)).weekday()] + " " + s
    return s


def tijd(iso):
    return (iso or "")[11:16]


def weergavenaam(naam):
    """'Elles Van Ark' -> 'Elles van Ark': tussenvoegsels na een voornaam met kleine letter.
    Een naam zonder voornaam ('Van der Plas') blijft zoals hij is."""
    if not naam:
        return naam
    delen = naam.split(" ")
    if len(delen) < 2:
        return naam
    uit = [delen[0]]
    for w in delen[1:]:
        uit.append(w.lower() if w.lower() in TUSSEN else w)
    # dubbele achternaam met koppelteken: 'Veldhoven-van der Meer' blijft
    return " ".join(uit)


def tekst(x):
    """Tekst in normale taal (oude bestanden hebben één string, nieuwe een dict per taalniveau)."""
    if isinstance(x, dict):
        return x.get("normaal") or x.get("makkelijk") or ""
    return x or ""


# ---------------------------------------------------------------- fracties en coalitie

@lru_cache(None)
def fracties():
    f = lees(DATA / "fracties.json")
    stand = sorted(f)[-1]
    co = lees(EIGEN / "coalitie.json")
    al = lees(EIGEN / "aliassen.json")["fractie"]
    rij = {k: {"code": k, "naam": v["naam"], "zetels": v["zetels"], "coalitie": k in co["coalitie"]} for k, v in f[stand].items()}
    return {"stand": stand, "per": rij, "alias": al, "coalitie": co, "totaal": sum(v["zetels"] for v in rij.values())}


def fractie(code):
    F = fracties()
    code = F["alias"].get(code, code)
    return F["per"].get(code)


# ---------------------------------------------------------------- personen en figuren

@lru_cache(None)
def _koppeling():
    return lees(DATA / "sprekers.json"), lees(DATA / "uiterlijk.json")


def figuur_sleutel(spreker_id):
    """Sleutel van het goedgekeurde figuur, of None (dan een neutraal figuur)."""
    kop, uit = _koppeling()
    k = kop.get(spreker_id)
    if k and k in uit and uit[k].get("goedgekeurd"):
        return k
    return None


def manga_map(sleutel):
    m = (sleutel or "").replace(":", "-")
    return m if m and (ROOT / "site" / "manga" / m / "neutraal.webp").exists() else None


def uiterlijk(sleutel):
    return _koppeling()[1].get(sleutel) if sleutel else None


def figuur_bestand(spreker_id):
    """Pad (relatief aan de site) van het figuur van deze spreker."""
    k = figuur_sleutel(spreker_id)
    if not k:
        return "fig/neutraal.svg"
    m = manga_map(k)
    return f"fig/{m}.webp" if m else f"fig/{k.replace(':', '-')}.svg"


class Persoon:
    def __init__(self, sp):
        self.id = sp["id"]
        self.naam = weergavenaam(sp.get("naam") or sp.get("verslagnaam") or "")
        self.achternaam = sp.get("verslagnaam") or self.naam
        self.fractie_code = sp.get("fractie") or ""
        self.functie = sp.get("functie") or ""
        self.soort = sp.get("soort") or ""
        self.fig = figuur_bestand(self.id)

    @property
    def kabinet(self):
        return not self.fractie_code

    @property
    def fractie(self):
        return fractie(self.fractie_code) if self.fractie_code else None

    def rol_kort(self):
        """'PRO' of 'minister van Sociale Zaken en Werkgelegenheid'."""
        return self.fractie_code or self.functie

    def label_fractie(self):
        """'PRO · 20 zetels · oppositie', of 'kabinet'."""
        f = self.fractie
        if self.kabinet:
            return "kabinet"
        if not f:
            return self.fractie_code
        return f"{f['code']} · {f['zetels']} {'zetel' if f['zetels'] == 1 else 'zetels'} · {'coalitie' if f['coalitie'] else 'oppositie'}"


# ---------------------------------------------------------------- video (Debat Direct)

@lru_cache(None)
def debatdirect(basis_id):
    f = DATA / "debatdirect" / f"{basis_id[:36]}.json"
    return lees(f) if f.exists() else None


def video_beurt(punt, i):
    """Link naar het moment in Debat Direct waarop spreekbeurt i begint (zelfde regel als scripts/build.py:
    zelfde persoon, hooguit 90 seconden van de begintijd in het verslag), of None."""
    dd = debatdirect(punt["id"])
    b = punt["beurten"][i]
    if not dd or not b.get("begin"):
        return None
    t = datetime.fromisoformat(b["begin"][:19])
    beste = None
    for m in dd["momenten"]:
        if m["persoon"] != b["spreker"]["id"]:
            continue
        v = abs((datetime.fromisoformat(m["start"][:19]) - t).total_seconds())
        if v <= 90 and (beste is None or v < beste[0]):
            beste = (v, m)
    if not beste:
        return None
    m = beste[1]
    return f"{dd['url']}/markeringen?event={urllib.parse.quote(m['soort'] + m['start'], safe='')}"


# ---------------------------------------------------------------- moties

def _sprekers_van(punten):
    namen = set()
    for p in punten:
        for b in p["beurten"]:
            if not b["voorzitter"]:
                namen.add((b["spreker"].get("verslagnaam") or "").lower())
    return namen


def _achternaam_indiener(naam):
    if ")" in naam:
        return naam.split(") ")[-1]
    return " ".join(w for w in naam.split() if not w.endswith("."))


def _sprak(indiener, namen):
    a = _achternaam_indiener(indiener).lower()
    return any(a == n or a.endswith(" " + n) or n.endswith(" " + a) for n in namen if n)


def motie_omschrijving(m):
    """'over de verruiming van de hypotheekrenteaftrek ongedaan maken' (letterlijk uit het onderwerp van de Kamer)."""
    o = (m.get("onderwerp") or "").strip()
    k = re.match(r"^Motie van (?:het lid|de leden) .*? (over .*)$", o)
    return k.group(1) if k else o


def motie_verzoek(m):
    t = m.get("tekst") or ""
    k = t.find("verzoekt de regering")
    if k < 0:
        k = t.find("verzoekt het kabinet")
    if k < 0:
        return ""
    return " ".join(t[k:].replace("en gaat over tot de orde van de dag.", "").split()).rstrip(",")


def uitslag_controle(u):
    """Telt de zetels van de fracties voor en tegen na met data/fracties.json. Geeft (voor, tegen, afwijking-tekst)."""
    def som(lijst):
        s, onbekend = 0, []
        for c in lijst:
            f = fractie(c)
            if f:
                s += f["zetels"]
            else:
                onbekend.append(c)
        return s, onbekend
    v, ov = som(u.get("voor") or [])
    t, ot = som(u.get("tegen") or [])
    afw = []
    if ov or ot:
        afw.append("onbekende fractie: " + ", ".join(ov + ot))
    if v != u.get("zetels_voor") or t != u.get("zetels_tegen"):
        afw.append(f"volgens de fractielijst {v} voor en {t} tegen; volgens de uitslag {u.get('zetels_voor')} voor en {u.get('zetels_tegen')} tegen")
    if (u.get("zetels_voor") or 0) + (u.get("zetels_tegen") or 0) != fracties()["totaal"]:
        afw.append(f"voor en tegen samen {(u.get('zetels_voor') or 0) + (u.get('zetels_tegen') or 0)} zetels, niet {fracties()['totaal']}")
    return v, t, "; ".join(afw)


# ---------------------------------------------------------------- debatten en delen

class Deel:
    """Eén agendapunt (een heel debat, of één deel van een lang debat)."""

    def __init__(self, punt):
        self.punt = punt
        self.id = punt["id"]
        d = punt.get("deel") or {}
        self.nummer = d.get("nummer") or 1
        self.van = d.get("van") or 1
        self.fase = d.get("fase") or ""
        self.sprekers_kort = d.get("sprekers") or ""
        self.begin = punt.get("begin") or punt["vergadering"]["datum"]
        self.eind = punt.get("eind") or ""
        self.beurten = punt["beurten"]
        self.woorden = sum(len(b["tekst"].split()) for b in self.beurten if not b.get("voorzitter"))
        self.pagina = self._pagina()
        self.kaart = self._kaart()
        self.redactie = self._redactie()
        self.slug = None  # gezet door Debat

    def _pagina(self):
        for map_ in ("paginas", "strips"):
            f = DATA / map_ / f"{self.id}.json"
            if f.exists():
                s = lees(f)
                return {
                    "bron": f"data/{map_}/{self.id}.json",
                    "verslag_id": s.get("verslag_id"),
                    "titel": tekst(s.get("titel")),
                    "samenvatting": tekst(s.get("samenvatting")),
                    "kernpunten": [x for x in (s.get("kernpunten") or {}).get("normaal", [])] if isinstance(s.get("kernpunten"), dict) else (s.get("kernpunten") or []),
                    "sprekers": [{"id": x["id"], "standpunt": tekst(x.get("standpunt"))} for x in s.get("sprekers") or []],
                    "woorden": [{"woord": w["woord"], "uitleg": tekst(w["uitleg"])} for w in s.get("woorden") or []],
                    "actueel": s.get("verslag_id") == self.punt["vergadering"]["verslag_id"],
                }
        return None

    def _kaart(self):
        f = DATA / "proeftuin" / "botsing" / f"{self.id}.json"
        if not f.exists():
            return None
        K = lees(f)
        a = K["versies"]["a"]
        v = "c" if "c" in K["versies"] and re.search("bijzaak", a.get("aandeel_onderwerp") or "", re.I) else "a"
        x = K["versies"][v]
        cit = []
        for c in x["citaten"]:
            b = self.beurten[c["beurt"]] if 0 <= c["beurt"] < len(self.beurten) else None
            cit.append({
                "beurt": c["beurt"], "citaat": c["citaat"],
                "persoon": Persoon(b["spreker"]) if b else None,
                "naam": weergavenaam(c["naam"]), "partij": c["partij"],
                "video": c.get("video"), "tijd": c.get("tijd"),
            })
        alle_video = all(c["video"] for c in cit) and cit
        return {"bron": f"data/proeftuin/botsing/{self.id}.json", "versie": v,
                "vraag": x.get("vraag") or K["vraag"], "kop": K.get("kop"), "citaten": cit,
                "video": bool(alle_video), "geen_botsing": bool(K.get("geen_botsing")),
                "afloop_data": K.get("afloop_data") or {}}

    def _redactie(self):
        f = DATA / "redactie" / f"{self.id}.json"
        if not f.exists() or not self.pagina:
            return None
        r = lees(f)
        return {"datum": r.get("datum"), "zelfde_versie": r.get("verslag_id") == self.pagina["verslag_id"],
                "onafhankelijk": r.get("onafhankelijk")}

    @property
    def titel(self):
        """Inhoudelijke titel van dit deel: de paginatitel, anders de fase en de sprekers uit de data."""
        if self.pagina and self.pagina["titel"]:
            return self.pagina["titel"]
        if self.fase:
            return self.fase + (f": {self.sprekers_kort}" if self.sprekers_kort else "")
        return self.punt["titel"]

    def personen(self):
        """Sprekers in volgorde van eerste spreekbeurt (zonder voorzitter)."""
        gezien, uit = set(), []
        for b in self.beurten:
            if b["voorzitter"]:
                continue
            if b["spreker"]["id"] not in gezien:
                gezien.add(b["spreker"]["id"])
                uit.append(Persoon(b["spreker"]))
        return uit


SOORT_UITLEG = {
    "Plenair debat": "plenair debat",
    "Vragenuur": "vragenuur",
    "Stemmingen": "stemmingen",
    "Wetgevingsoverleg": "wetgevingsoverleg",
}


class Debat:
    def __init__(self, sleutel, delen, alle_ids):
        self.id = sleutel
        self.delen = sorted(delen, key=lambda d: d.nummer)
        p = self.delen[0].punt
        dd = p.get("deel") or {}
        self.titel_agenda = dd.get("ouder_titel") or p["titel"]
        self.onderwerp = p.get("onderwerp") or p["titel"]
        self.datum = p["vergadering"]["datum"]
        self.begin = min(d.begin for d in self.delen)
        self.vergadering = p["vergadering"]
        self.zaal = p["vergadering"].get("soort") or ""  # Plenair / Commissie
        self.soort = p.get("soort_activiteit") or ""
        self.van = dd.get("van") or 1
        verwacht = dd.get("ids") or [d.id for d in self.delen]
        self.ontbrekend = [(n, i) for n, i in enumerate(verwacht, 1) if i not in alle_ids]
        self.voorlopig = any(d.punt["vergadering"]["status"] in VOORLOPIG for d in self.delen)
        self.moties = []
        self.genoemde_moties = []  # bij Stemmingen: moties die daar genoemd zijn (horen bij een ander debat)
        self.slug = None

    # -- soort debat in gewone woorden
    @property
    def is_stemmingen(self):
        return "stemming" in self.soort.lower()

    @property
    def is_vragenuur(self):
        return "vragenuur" in self.soort.lower()

    @property
    def is_tweeminuten(self):
        return any("tweeminutendebat" in " ".join(b["tekst"] for b in d.beurten[:3] if b.get("voorzitter")).lower() for d in self.delen[:1])

    @property
    def soort_label(self):
        if self.is_tweeminuten:
            return "Tweeminutendebat"
        if self.soort == "Plenair debat":
            return "Debat in de plenaire zaal"
        if self.soort == "Wetgevingsoverleg":
            return "Wetgevingsoverleg (commissie)"
        return self.soort or self.zaal

    @property
    def over_wet(self):
        """Gaat het debat over een wetsvoorstel? Vaste regel op de titel (begroting, belastingplan, novelle, wet)."""
        return bool(re.search(r"begroting|belastingplan|novelle|\bwet", self.titel_agenda, re.I))

    @property
    def kaart(self):
        """De kaart van het debat (vaste regel): het eerste deel met een kaart met twee citaten en een botsing;
        anders het eerste deel met een kaart."""
        for d in self.delen:
            if d.kaart and len(d.kaart["citaten"]) >= 2 and not d.kaart["geen_botsing"]:
                return d
        for d in self.delen:
            if d.kaart:
                return d
        return None

    @property
    def titel(self):
        """Kop van het debat: bij één deel de paginatitel; bij delen de agendatitel."""
        if len(self.delen) == 1 and self.delen[0].pagina:
            return self.delen[0].pagina["titel"]
        return self.titel_agenda

    @property
    def vraag(self):
        k = self.kaart
        return k.kaart["vraag"] if k else None

    def personen(self):
        gezien, uit = set(), []
        for d in self.delen:
            for p in d.personen():
                if p.id not in gezien:
                    gezien.add(p.id)
                    uit.append(p)
        return uit

    @property
    def woorden(self):
        return sum(d.woorden for d in self.delen)

    def heeft_tekst(self):
        return any(d.pagina for d in self.delen)


@lru_cache(None)
def laad():
    punten = {}
    for f in sorted((DATA / "agendapunten").glob("*.json")):
        p = lees(f)
        punten[p["id"]] = p
    groepen = {}
    for p in punten.values():
        k = (p.get("deel") or {}).get("ouder_id") or p["id"]
        groepen.setdefault(k, []).append(Deel(p))
    debatten = [Debat(k, v, set(punten)) for k, v in groepen.items()]
    debatten.sort(key=lambda d: d.begin, reverse=True)

    # slugs: datum + agendatitel; bij botsing een volgnummer
    gezien = {}
    for d in sorted(debatten, key=lambda d: d.begin):
        s = f"{d.datum}-{slug(d.titel_agenda, 60)}"
        n = gezien.get(s, 0) + 1
        gezien[s] = n
        d.slug = s if n == 1 else f"{s}-{tijd(d.begin).replace(':', '')}"
        for x in d.delen:
            x.slug = d.slug if len(d.delen) == 1 and d.van == 1 else f"{d.slug}-deel-{x.nummer}"
            x.debat = d

    # moties: per motie-id het debat waarin de eerste indiener sprak (stemmingen niet meegeteld)
    per_punt = {}
    for f in sorted((DATA / "moties").glob("*.json")):
        m = lees(f)
        per_punt[m["agendapunt"]] = m["moties"]
    debat_van_punt = {x.id: d for d in debatten for x in d.delen}
    toegewezen = {}
    for pid, ms in per_punt.items():
        d = debat_van_punt.get(pid)
        if not d:
            continue
        namen = _sprekers_van([x.punt for x in d.delen])
        for m in ms:
            if d.is_stemmingen:
                d.genoemde_moties.append(m)
                continue
            if m["indieners"] and _sprak(m["indieners"][0]["naam"], namen):
                if m["id"] not in toegewezen:
                    toegewezen[m["id"]] = (d, m)
    for mid, (d, m) in toegewezen.items():
        d.moties.append(m)
    for d in debatten:
        d.moties.sort(key=lambda m: (m["dossier"], int(re.sub(r"\D", "", m["nummer"]) or 0)))
        uniek = {}
        for m in d.genoemde_moties:
            uniek[m["id"]] = m
        d.genoemde_moties = sorted(uniek.values(), key=lambda m: int(re.sub(r"\D", "", m["nummer"]) or 0))
    motie_debat = {mid: d for mid, (d, m) in toegewezen.items()}
    return {"debatten": debatten, "punten": punten, "motie_debat": motie_debat}


def debatten():
    return laad()["debatten"]


def motie_debat(mid):
    return laad()["motie_debat"].get(mid)


def dagen():
    """[(datum, [debatten op begintijd])], nieuwste dag eerst."""
    per = {}
    for d in debatten():
        per.setdefault(d.datum, []).append(d)
    return [(k, sorted(v, key=lambda d: d.begin)) for k, v in sorted(per.items(), reverse=True)]


def gebouwd_op():
    return date.today().isoformat()


def bron_verslag(deel):
    return f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag({deel.punt['vergadering']['verslag_id']})/resource"
