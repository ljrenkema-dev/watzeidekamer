"""Proeftuin: vijf vaste testdebatten waarop we de schrijfopdracht verbeteren.
Bouwt tools/proeftuin/index.html (+ strip.js, style.css, manga-beelden) met per debat titel, samenvatting,
strip, standpunten en kernpunten, elk met een feedbackknop. Versies van de strips staan in
data/proeftuin/<versie>/<id>.json; de huidige site-strips zijn versie v1.
Gebruik: python3 scripts/proeftuin.py [versie] [vorige-versie]"""
import json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402

TEST = ["dd194a7c-3fbf-4bc5-b275-5f733e839dd6",            # vragenuur
        "4a7d6515-21f1-4641-91c6-80b547a7d1b9",            # box 3-novelle
        "be0a626e-43e2-48d7-8d1e-2c60fd372f02-d1",         # Belastingplan, Klaver en Paternotte
        "c0b2be4c-9cd7-4be6-9421-01b294be732d-d1",         # Buitenlandse Zaken, Gaza en Oekraïne
        "d00f02de-7aad-4972-8d85-b280b58511b7"]            # Sahel (commissie)
UIT = ROOT / "tools" / "proeftuin"


def varianten(versie, pid):
    """Alle strips van dit debat in deze versie: <id>.json en <id>__<opzet>.json."""
    map_ = ROOT / "data" / "proeftuin" / versie
    return sorted(map_.glob(f"{pid}*.json")) if map_.exists() else []


def lees_strip(versie, pid):
    f = ROOT / "data" / "proeftuin" / versie / f"{pid}.json"
    if not f.exists() and versie == "v1":
        f.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / "data" / "strips" / f"{pid}.json", f)
    return json.loads(f.read_text()) if f.exists() else None


def debat_data(pid, strip):
    punt = json.loads((ROOT / "data" / "agendapunten" / f"{pid}.json").read_text())
    html_, sprekers = build.debat(punt, strip)
    data = json.loads(re.search(r"window\.STRIP=(\{.*?\});renderStrip", html_, re.S).group(1).replace("<\\/", "</"))
    bekend = {b["spreker"]["id"]: b["spreker"] for b in punt["beurten"]}
    tw = lambda x: x if isinstance(x, dict) else {"normaal": x, "makkelijk": x}
    standpunten = [{"id": s["id"], "partij": bekend[s["id"]]["fractie"] or "Kabinet",
                    "naam": bekend[s["id"]].get("naam") or bekend[s["id"]]["verslagnaam"], "tekst": tw(s["standpunt"])}
                   for s in strip["sprekers"]]
    return {"id": pid, "agendapunt": punt["titel"], "datum": punt["vergadering"]["datum"], "soort": punt["vergadering"]["soort"],
            "titel": tw(strip["titel"]), "samenvatting": tw(strip["samenvatting"]), "kernpunten": tw(strip["kernpunten"]),
            "standpunten": standpunten, "strip": data, "onderwerpen": strip.get("onderwerpen") or [],
            "strip_onderwerp": strip.get("strip_onderwerp"), "opzet": strip.get("_opzet", "")}


def main(versie="v1", vorige=None):
    debatten = []
    for pid in TEST:
        bestanden = varianten(versie, pid)
        if not bestanden:  # nog niet opnieuw gemaakt: de vorige versie blijft staan
            s = lees_strip(vorige or "v1", pid)
            if not s:
                continue
            d = debat_data(pid, s); d["opzet"] = f"ongewijzigd ({vorige or 'v1'})"; debatten.append(d); continue
        for f in bestanden:
            s = json.loads(f.read_text())
            d = debat_data(pid, s)
            d["variant"] = f.stem
            if vorige and lees_strip(vorige, pid):
                d["vorige"] = debat_data(pid, lees_strip(vorige, pid))
            debatten.append(d)
    if UIT.exists():
        shutil.rmtree(UIT)
    UIT.mkdir(parents=True)
    for f in ("strip.js", "style.css"):
        shutil.copy(ROOT / "site" / f, UIT / f)
    nodig = {sp["uiterlijk"]["manga"] for d in debatten for sp in d["strip"]["sprekers"] if (sp.get("uiterlijk") or {}).get("manga")}
    for m in nodig:
        shutil.copytree(ROOT / "site" / "manga" / m, UIT / "manga" / m)
    sjabloon = (ROOT / "tools" / "proeftuin-sjabloon.html").read_text()
    (UIT / "index.html").write_text(sjabloon.replace("__VERSIE__", versie).replace(
        "__DATA__", json.dumps(debatten, ensure_ascii=False).replace("</", "<\\/")))
    print(f"proeftuin {versie}: {len(debatten)} debatten, {len(nodig)} manga-figuren → {UIT}")


if __name__ == "__main__":
    main(*(sys.argv[1:3] or ["v1"]))
