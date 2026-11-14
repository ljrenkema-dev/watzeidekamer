"""Eigen controle van een gebouwde variant (wijzigt scripts/check.py en scripts/kaart.py niet).

Gebruik: python3 controle.py a [b c]
Controleert:
 1. elk agendapunt (deel) heeft een debatpagina en een verslagpagina;
 2. geen kapotte interne link of anker;
 3. elk getoond citaat (element met data-citaat="<deel-id>#<beurt>") staat letterlijk in die spreekbeurt van het verslag;
 4. elke getoonde uitslag (li.motie) klopt met data/moties, en de zetels per fractie kloppen met data/fracties.json;
 5. elk getoond zetelaantal bij een fractie klopt; de fractielijst telt op tot 150 (of de afwijking staat erbij);
 6. geen verouderende woorden of afgekorte datums, geen tellingen die tot een ranglijst uitnodigen;
 7. geen dubbele tekstblokken op één pagina.
"""
import re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
sys.path.insert(0, str(Path(__file__).resolve().parent))
from kern import model as M, stukken as S

NIEUW = Path(__file__).resolve().parent


class Ontleed(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.citaten, self.moties, self.blokken = [], set(), [], [], []
        self._stack, self._cit, self._mot, self._blok = [], None, None, None

    def handle_starttag(self, tag, a):
        a = dict(a)
        if "id" in a:
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k):
                self.links.append(a[k])
        self._stack.append(tag)
        if a.get("data-citaat"):
            self._cit = [a["data-citaat"], "", len(self._stack)]
        if tag == "li" and "motie" in (a.get("class") or "").split():
            self._mot = [a.get("id", ""), "", len(self._stack)]
        if tag in ("p", "li", "dd") and self._blok is None and not self._cit:
            self._blok = ["", len(self._stack), tag]

    def handle_endtag(self, tag):
        n = len(self._stack)
        if self._cit and n == self._cit[2]:
            self.citaten.append((self._cit[0], self._cit[1]))
            self._cit = None
        if self._mot and n == self._mot[2]:
            self.moties.append((self._mot[0], self._mot[1]))
            self._mot = None
        if self._blok and n == self._blok[1]:
            self.blokken.append(self._blok[0].strip())
            self._blok = None
        if self._stack:
            self._stack.pop()

    def handle_data(self, d):
        if self._cit:
            self._cit[1] += d
        if self._mot:
            self._mot[1] += d
        if self._blok:
            self._blok[0] += d


VERBODEN = [r"\bnieuw\b", r"\bgisteren\b", r"\bvandaag\b", r"\bmorgen\b", r"deze week", r"vorige week", r"nog niet gestemd",
            r"stemming verwacht", r"afloop van het debat", r"\bbinnenkort\b"]
AFGEKORT = r"\b\d{1,2} (jan|feb|mrt|apr|jun|jul|aug|sep|sept|okt|nov|dec)\b"
RANG = r"\d+\s+(spreekbeurten|interrupties|keer gesproken)"


def controleer(variant):
    root = NIEUW / "uit" / variant
    fouten, waarsch = [], []
    paginas = {p.relative_to(root).as_posix(): p for p in root.rglob("*.html") if p.name != "_artifact.html"}
    ontleed = {}
    for rel, p in paginas.items():
        o = Ontleed()
        o.feed(p.read_text())
        ontleed[rel] = o

    # 1. elk deel een pagina
    for d in M.debatten():
        if f"debat/{d.slug}.html" not in paginas:
            fouten.append(f"geen debatpagina voor {d.slug}")
        for x in d.delen:
            for pre in ("debat", "verslag"):
                if f"{pre}/{x.slug}.html" not in paginas:
                    fouten.append(f"geen {pre}pagina voor {x.slug}")

    # 2. links
    for rel, o in ontleed.items():
        for l in o.links:
            u = urlparse(l)
            if u.scheme or l.startswith("//") or l.startswith("mailto:"):
                continue
            doel = (paginas[rel].parent / unquote(u.path)).resolve() if u.path else paginas[rel].resolve()
            if not doel.exists():
                fouten.append(f"{rel}: kapotte link {l}")
                continue
            if u.fragment and doel.suffix == ".html":
                drel = doel.relative_to(root.resolve()).as_posix()
                if u.fragment not in ontleed[drel].ids:
                    fouten.append(f"{rel}: anker #{u.fragment} ontbreekt in {drel}")

    # 3. citaten
    punten = M.laad()["punten"]
    n_cit = 0
    for rel, o in ontleed.items():
        for bron, t in o.citaten:
            n_cit += 1
            pid, _, beurt = bron.partition("#")
            if pid not in punten:
                fouten.append(f"{rel}: citaat met onbekend agendapunt {pid}")
                continue
            b = punten[pid]["beurten"][int(beurt)]
            t = re.sub(r"^[“\"]\s*|\s*[”\"]$", "", t.strip())
            t = re.sub(r"^…\s*", "", t)
            if not S.citaat_in_beurt(t, b["tekst"]):
                fouten.append(f"{rel}: citaat niet letterlijk in beurt {bron}: {t[:70]}")

    # 4. uitslagen
    alle = {}
    for f in (M.DATA / "moties").glob("*.json"):
        for m in M.lees(f)["moties"]:
            alle[f"motie-{m['dossier'].replace(' ', '')}-{m['nummer']}"] = m
    n_mot = 0
    for rel, o in ontleed.items():
        for mid, t in o.moties:
            n_mot += 1
            m = alle.get(mid)
            if not m:
                fouten.append(f"{rel}: motie {mid} niet in de data")
                continue
            u = m.get("uitslag")
            k = re.search(r"(Aangenomen|Verworpen): (\d+) zetels voor, (\d+) tegen", t)
            if u and u.get("besluit"):
                if not k:
                    fouten.append(f"{rel}: uitslag van {mid} niet getoond")
                elif (k.group(1).lower() != u["besluit"].rstrip(".").lower() or int(k.group(2)) != u["zetels_voor"]
                      or int(k.group(3)) != u["zetels_tegen"]):
                    fouten.append(f"{rel}: uitslag van {mid} wijkt af van de data")
                v, tg, afw = M.uitslag_controle(u)
                if afw and "Let op" not in t:
                    fouten.append(f"{rel}: afwijking in telling van {mid} niet getoond ({afw})")
            elif k:
                fouten.append(f"{rel}: uitslag getoond voor {mid} zonder uitslag in de data")
            for code, z in re.findall(r"([A-Za-z0-9][\w -]*?) \((\d+)(?:, coalitie)?\)", t):
                f = M.fractie(code.strip())
                if f and f["zetels"] != int(z):
                    fouten.append(f"{rel}: {code} heeft {z} zetels bij {mid}, data zegt {f['zetels']}")

    # 5. zetels bij fracties
    F = M.fracties()
    for rel, p in paginas.items():
        tekst_ = re.sub(r"<[^>]+>", " ", p.read_text())
        for code, z, rol in re.findall(r"([\w-]+(?: [\w-]+)?) · (\d+) zetels? · (coalitie|oppositie)", tekst_):
            f = M.fractie(code) or M.fractie(code.split(" ")[-1])
            if not f:
                fouten.append(f"{rel}: onbekende fractie {code}")
            elif f["zetels"] != int(z) or f["coalitie"] != (rol == "coalitie"):
                fouten.append(f"{rel}: {code} · {z} zetels · {rol} klopt niet")
    if F["totaal"] != 150:
        waarsch.append(f"fractielijst telt op tot {F['totaal']}, niet 150 (staat op Zo werken we)")

    # 6. verouderende woorden, afkortingen, ranglijsten (alleen zichtbare tekst buiten citaten en verslag)
    for rel, p in paginas.items():
        if rel.startswith("verslag/"):
            continue
        h = p.read_text()
        h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S)
        h = re.sub(r"<[^>]*data-citaat[^>]*>.*?</(blockquote|q|figure|div)>", " ", h, flags=re.S)
        h = re.sub(r"<head>.*?</head>", " ", h, flags=re.S)
        zicht = re.sub(r"<[^>]+>", " ", h)
        for pat in VERBODEN:
            for k in re.finditer(pat, zicht, re.I):
                omg = zicht[max(0, k.start() - 50):k.end() + 50].replace("\n", " ")
                waarsch.append(f"{rel}: '{k.group(0)}' in: …{omg}…")
        if re.search(AFGEKORT, zicht):
            fouten.append(f"{rel}: afgekorte datum: {re.search(AFGEKORT, zicht).group(0)}")
        if re.search(RANG, zicht):
            fouten.append(f"{rel}: telling die tot een ranglijst uitnodigt: {re.search(RANG, zicht).group(0)}")

    # 7. dubbele blokken
    for rel, o in ontleed.items():
        if rel.startswith("verslag/"):
            continue  # het verslag is letterlijk; daar herhalen sprekers zich soms
        gezien = {}
        for b in o.blokken:
            b = re.sub(r"\s+", " ", b)
            if len(b) < 60 or b.startswith("▶"):
                continue
            gezien[b] = gezien.get(b, 0) + 1
        for b, n in gezien.items():
            if n > 1:
                fouten.append(f"{rel}: tekst {n}× op de pagina: {b[:70]}")

    # 8. aanhalingen in tekst die de site toont (samenvattingen, standpunten): staan ze letterlijk in het debat?
    for d in M.debatten():
        for x in d.delen:
            if not x.pagina:
                continue
            tekst_ = x.pagina["samenvatting"] + " " + " ".join(s_["standpunt"] for s_ in x.pagina["sprekers"])
            alles = M.norm(" ".join(b["tekst"] for y in d.delen for b in y.beurten))
            for q in re.findall(r"[“\"]([^”\"“]{12,})[”\"]", tekst_):
                if M.norm(q) not in alles:
                    waarsch.append(f"debat/{x.slug}.html: aanhaling in de paginadata niet letterlijk in het verslag: '{q[:70]}'")

    return fouten, waarsch, {"paginas": len(paginas), "citaten": n_cit, "moties": n_mot}


if __name__ == "__main__":
    slecht = False
    for v in sys.argv[1:] or ["a", "b", "c"]:
        f, w, n = controleer(v)
        print(f"variant {v}: {n['paginas']} pagina's, {n['citaten']} citaten, {n['moties']} getoonde moties: "
              f"{'OK' if not f else f'{len(f)} fout(en)'}" + (f", {len(w)} waarschuwing(en)" if w else ""))
        for x in f[:60]:
            print("  FOUT  ", x)
        for x in w[:30]:
            print("  let op", x)
        slecht |= bool(f)
    sys.exit(1 if slecht else 0)
