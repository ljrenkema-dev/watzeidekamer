"""Controleer een strip tegen de bron. Gebruik: python3 scripts/check.py <agendapunt_id> [...]

Fouten (exit 1): citaat niet letterlijk bij die spreker, onbekende spreker, verkeerde vorm.
Waarschuwingen: fractie ontbreekt in 'sprekers', lange tekst in een vak.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EMOTIES = {"neutraal", "blij", "boos", "bezorgd", "verbaasd", "denkend", "vastberaden"}


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def check(pid):
    punt = json.loads((ROOT / "data" / "agendapunten" / f"{pid}.json").read_text())
    strip = json.loads((ROOT / "data" / "strips" / f"{pid}.json").read_text())
    fouten, waarsch = [], []
    per_spreker, alles = {}, []
    for b in punt["beurten"]:
        per_spreker.setdefault(b["spreker"]["id"], []).append(norm(b["tekst"]))
        alles.append(norm(b["tekst"]))
    bekend = {b["spreker"]["id"]: b["spreker"] for b in punt["beurten"]}

    if strip.get("agendapunt") != pid:
        fouten.append("veld 'agendapunt' klopt niet")
    if strip.get("verslag_id") != punt["vergadering"]["verslag_id"]:
        fouten.append("verslag_id hoort bij een andere versie van het verslag")
    vakken = strip.get("strip", [])
    if not 4 <= len(vakken) <= 8:
        fouten.append(f"{len(vakken)} vakken; moet 4 tot 8 zijn")
    for i, v in enumerate(vakken, 1):
        sid = v.get("spreker_id")
        if sid is not None and sid not in bekend:
            fouten.append(f"vak {i}: onbekende spreker_id {sid}")
            continue
        if v.get("emotie") not in EMOTIES:
            fouten.append(f"vak {i}: emotie '{v.get('emotie')}' niet toegestaan")
        bron = alles if sid is None else per_spreker[sid]
        for stuk in re.split(r"\s*(?:…|\.\.\.)\s*", norm(v.get("citaat", ""))):
            if not stuk:
                continue
            if len(stuk.split()) < 5:
                fouten.append(f"vak {i}: citaatstuk te kort: '{stuk}'")
            elif not any(stuk in t for t in bron):
                wie = "de tekst" if sid is None else bekend[sid]["naam"]
                fouten.append(f"vak {i}: niet letterlijk gevonden bij {wie}: '{stuk[:80]}'")
        for niv, maxw in (("normaal", 20), ("makkelijk", 16)):
            t = (v.get("tekst") or {}).get(niv, "") if isinstance(v.get("tekst"), dict) else ""
            if not t.strip():
                fouten.append(f"vak {i}: tekst '{niv}' ontbreekt")
            elif len(t.split()) > maxw:
                waarsch.append(f"vak {i}: tekst '{niv}' is lang ({len(t.split())} woorden)")
    for veld in ("titel", "samenvatting", "kernpunten"):
        for niv in ("normaal", "makkelijk"):
            if not (strip.get(veld) or {}).get(niv) if isinstance(strip.get(veld), dict) else True:
                fouten.append(f"{veld}: versie '{niv}' ontbreekt")
    for s in strip.get("sprekers", []):
        if s.get("id") not in bekend:
            fouten.append(f"sprekers: onbekende id {s.get('id')}")
        st = s.get("standpunt")
        if not isinstance(st, dict) or not st.get("normaal") or not st.get("makkelijk"):
            fouten.append(f"sprekers: standpunt van {s.get('id')} mist een taalniveau")
    genoemd = {bekend[s["id"]]["fractie"] for s in strip.get("sprekers", []) if s.get("id") in bekend}
    sprak = {b["spreker"]["fractie"] for b in punt["beurten"] if not b["voorzitter"] and b["spreker"]["fractie"]}
    for f in sorted(sprak - genoemd):
        waarsch.append(f"fractie {f} sprak maar staat niet in 'sprekers'")
    return fouten, waarsch


if __name__ == "__main__":
    slecht = False
    for pid in sys.argv[1:]:
        f, w = check(pid)
        print(f"{pid}: {'OK' if not f else f'{len(f)} fout(en)'}" + (f", {len(w)} waarschuwing(en)" if w else ""))
        for x in f: print("  FOUT  " + x)
        for x in w: print("  let op " + x)
        slecht |= bool(f)
    sys.exit(1 if slecht else 0)
