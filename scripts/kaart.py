"""Kaart zonder strip: voorwerk en controle, zonder taalmodel.
  python3 scripts/kaart.py voor <id>     → data/compact/kaart_<id>.txt: de 3 langste wisselingen (volledige tekst),
                                         partijen, afloop uit data/moties; het model kiest daaruit vraag en citaten.
  python3 scripts/kaart.py check <id>    → controleert data/proeftuin/botsing/<id>.json (letterlijke citaten, velden)
                                         en vult video, figuur, partijen en afloop aan."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402
from check import norm  # noqa: E402


def laad(pid):
    return json.loads((ROOT / "data" / "agendapunten" / f"{pid}.json").read_text())


def is_vz(b):
    return b["voorzitter"] or len(b["tekst"].split()) < 6  # korte ordezaken ("Afrondend.") tellen niet mee


def wisselingen(p):
    bs = [(i, b) for i, b in enumerate(p["beurten"]) if not is_vz(b)]
    uit, cur = [], []
    for i, b in bs:
        s = b["spreker"]["id"]
        if cur and s != cur[-1][1] and len({x[1] for x in cur} | {s}) <= 2:
            cur.append((i, s))
        else:
            if len(cur) >= 2:
                uit.append(cur)
            cur = [cur[-1], (i, s)] if cur and s != cur[-1][1] else [(i, s)]
    if len(cur) >= 2:
        uit.append(cur)
    return sorted(uit, key=lambda c: -len(c))


def wie(b):
    sp = b["spreker"]
    return f"{sp.get('naam') or sp['verslagnaam']} ({sp['fractie'] or sp.get('functie', '')})"


def partijen(p):
    return sorted({b["spreker"]["fractie"] for b in p["beurten"] if b["spreker"]["fractie"] and not b["voorzitter"]})


def afloop(pid):
    f = ROOT / "data" / "moties" / f"{pid}.json"
    ms = json.loads(f.read_text())["moties"] if f.exists() else []
    if not ms:
        return "Geen moties in dit debat in onze data; geen stemuitslag."
    regels = []
    for m in ms:
        u = m.get("uitslag")
        regels.append(f"motie {m['nummer']} ({', '.join(i['naam'] for i in m['indieners'][:1])}): "
                      + (f"{u['besluit'].rstrip('.').lower()} ({u['zetels_voor']}–{u['zetels_tegen']})" if u else "nog niet gestemd"))
    return "; ".join(regels)


def voor(pid):
    p = laad(pid)
    B = p["beurten"]
    v = p["vergadering"]
    regels = [f"DEBAT {pid} | {p['titel']} | {v['datum']} | {v['soort']}" + (f" | deel: {p['deel'].get('fase')}" if p.get("deel") else ""),
              f"OPENING VOORZITTER: {B[0]['tekst'][:600] if B else ''}",
              f"PARTIJEN DIE SPRAKEN ({len(partijen(p))}): {', '.join(partijen(p))}",
              f"AFLOOP (uit de motiedata, letterlijk overnemen): {afloop(pid)}", ""]
    w = wisselingen(p)
    if not w or len(w[0]) < 3:
        regels.append("GEEN ECHTE WISSELING (minder dan 3 beurten over en weer).")
    for n, c in enumerate(w[:3], 1):
        namen = " ↔ ".join(sorted({wie(B[i]) for i, _ in c}))
        regels.append(f"=== WISSELING {n}: {namen}, {len(c)} beurten (beurt {c[0][0]}–{c[-1][0]}) ===")
        for i, _ in c:
            regels.append(f"[{i}] {wie(B[i])} | {B[i]['rol']}\n{B[i]['tekst']}\n")
    uit = ROOT / "data" / "compact" / f"kaart_{pid}.txt"
    uit.parent.mkdir(parents=True, exist_ok=True)
    uit.write_text("\n".join(regels))
    print(f"{uit}: {len(uit.read_text().split())} woorden, {len(w)} wisselingen")


def check(pid):
    p = laad(pid)
    B = p["beurten"]
    f = ROOT / "data" / "proeftuin" / "botsing" / f"{pid}.json"
    k = json.loads(f.read_text())
    fouten = []
    for veld in ("kop", "vraag", "vraag_bron", "versies"):
        if not k.get(veld):
            fouten.append(f"veld '{veld}' ontbreekt")
    uiterlijk = json.loads((ROOT / "data" / "uiterlijk.json").read_text())
    koppeling = json.loads((ROOT / "data" / "sprekers.json").read_text())
    for naam, v in (k.get("versies") or {}).items():
        cs = v.get("citaten") or []
        if not 1 <= len(cs) <= 2:
            fouten.append(f"versie {naam}: 1 of 2 citaten nodig")
        for c in cs:
            i = c.get("beurt")
            if not isinstance(i, int) or not 0 <= i < len(B):
                fouten.append(f"versie {naam}: ongeldige beurt {i}"); continue
            for s in [x.strip() for x in c["citaat"].split(" … ")]:
                if len(s.split()) < 5 or norm(s) not in norm(B[i]["tekst"]):
                    fouten.append(f"versie {naam}, beurt {i}: niet letterlijk of korter dan 5 woorden: {s[:60]}")
            zinnen = len(re.findall(r"[.?!](?:\s|$)", c["citaat"]))
            if zinnen > 2:
                fouten.append(f"versie {naam}, beurt {i}: {zinnen} zinnen, hooguit 2")
            sp = B[i]["spreker"]
            c.update({"naam": sp.get("naam") or sp["verslagnaam"],
                      "partij": sp["fractie"] or (sp.get("functie") or "").replace("minister van Sociale Zaken en Werkgelegenheid", "minister van SZW"),
                      "video": build.video_link(p, i), "tijd": (B[i].get("begin") or "")[11:16]})
            sl = koppeling.get(sp["id"]); u = uiterlijk.get(sl or "")
            kk = {x: u[x] for x in build.KENMERKEN if x in u} if u else None
            if kk and build.manga(sl):
                kk["manga"] = build.manga(sl)
            c["figuur"] = {"id": sp["id"], "fractie": sp.get("fractie") or "", "u": kk}
    k["partijen_totaal"] = len(partijen(p))
    k.setdefault("afloop", afloop(pid))
    f.write_text(json.dumps(k, ensure_ascii=False, indent=1))
    print(f"{pid}: {'OK' if not fouten else str(len(fouten)) + ' fout(en)'}")
    for x in fouten:
        print("  FOUT", x)
    return not fouten


if __name__ == "__main__":
    {"voor": voor, "check": check}[sys.argv[1]](sys.argv[2])
