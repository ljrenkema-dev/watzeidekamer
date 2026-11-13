"""Compacte invoer voor de schrijver en de redacteuren: alleen wat nodig is om een strip te maken.
Per spreekbeurt: nummer, spreker (naam, fractie of functie, id), rol en de letterlijke tekst. Korte beurten van
de voorzitter (ordezaken) vallen weg. De tekst zelf wordt niet ingekort: citaten moeten letterlijk blijven.
Gebruik: python3 scripts/compact.py <id>   → schrijft data/compact/<id>.txt en meldt de besparing."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def compact(pid):
    punt = json.loads((ROOT / "data" / "agendapunten" / f"{pid}.json").read_text())
    v = punt["vergadering"]
    kop = [f"AGENDAPUNT {punt['id']} | {punt['titel']} | {v['datum']} | {v['soort']} | verslag_id {v['verslag_id']} | status {v['status']}"]
    if punt.get("deel"):
        d = punt["deel"]
        kop.append(f"DEEL {d['nummer']} van {d['van']} | fase: {d.get('fase', '')}")
    sprekers, regels = {}, []
    for i, b in enumerate(punt["beurten"]):
        sp = b["spreker"]
        if b.get("voorzitter") and len(b["tekst"].split()) < 40:
            continue  # korte ordezaken van de voorzitter
        sprekers[sp["id"]] = f"{sp.get('naam') or sp['verslagnaam']} ({sp['fractie'] or sp.get('functie', '')})"
        rol = "VOORZITTER" if b.get("voorzitter") else ("INTERRUPTIE" if b["rol"] == "interrumpant" else "")
        regels.append(f"\n[{i}] {sp['verslagnaam']} | {sp['fractie'] or sp.get('functie', '')} | id {sp['id']}{' | ' + rol if rol else ''}\n{b['tekst']}")
    mf = ROOT / "data" / "moties" / f"{pid}.json"
    moties = json.loads(mf.read_text()).get("moties", []) if mf.exists() else []
    kop.append("SPREKERS: " + "; ".join(f"{n} id {i}" for i, n in sprekers.items()))
    extra = []
    if moties:
        extra.append("\n\nMOTIES (uit de open data; NIET citeren in de strip, wel gebruiken voor samenvatting, kernpunten en standpunten):")
        for m in moties:
            wie = ", ".join(f"{i['naam']} ({i.get('fractie') or ''})" for i in m["indieners"])
            extra.append(f"- Motie {m['nummer']} van {wie} | oordeel kabinet: {m.get('oordeel_kabinet') or 'onbekend'}"
                         f" | uitslag: {(m.get('uitslag') or {}).get('besluit', 'nog niet bekend')}\n  {m['tekst']}")
    return "\n".join(kop + regels + extra)


if __name__ == "__main__":
    for pid in sys.argv[1:]:
        tekst = compact(pid)
        uit = ROOT / "data" / "compact" / f"{pid}.txt"
        uit.parent.mkdir(parents=True, exist_ok=True)
        uit.write_text(tekst)
        bron = (ROOT / "data" / "agendapunten" / f"{pid}.json").stat().st_size
        print(f"{pid}: {bron // 1024} kB json → {len(tekst.encode()) // 1024} kB tekst")
