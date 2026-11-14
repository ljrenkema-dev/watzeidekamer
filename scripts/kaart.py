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


def afloop_data(pid):
    """Afloop uit de motie- en stemdata, steeds opnieuw berekend (nooit als vaste tekst bewaard).
    status: geen_moties | open (nog niet (helemaal) gestemd) | gestemd."""
    import datetime
    f = ROOT / "data" / "moties" / f"{pid}.json"
    ms = json.loads(f.read_text())["moties"] if f.exists() else []
    stand = datetime.date.today().isoformat()
    if not ms and "vragenuur" in laad(pid)["titel"].lower():
        return {"status": "geen_moties", "stand": stand, "kort": "Bij een vragenuur wordt niet gestemd.",
                "lang": "Bij een vragenuur wordt niet gestemd en worden geen moties ingediend.", "moties": []}
    if not ms:
        return {"status": "geen_moties", "stand": stand, "kort": "Geen moties in dit debat.",
                "lang": "In dit debat zijn geen moties ingediend.", "moties": []}
    rij, open_ = [], 0
    for m in ms:
        u = m.get("uitslag")
        wie = m["indieners"][0]["naam"] if m["indieners"] else "?"
        if u:
            rij.append({"nummer": m["nummer"], "wie": wie, "besluit": u["besluit"].rstrip("."), "voor": u["zetels_voor"], "tegen": u["zetels_tegen"]})
        else:
            open_ += 1
            rij.append({"nummer": m["nummer"], "wie": wie, "besluit": None})
    gestemd = [r for r in rij if r["besluit"]]
    n = len(rij)
    if not gestemd:
        kort = f"Van {'de motie' if n == 1 else f'de {n} moties'} staat nog geen uitslag in onze gegevens."
    elif open_:
        kort = f"Uitslag bekend van {len(gestemd)} van {n} moties: " + ", ".join(f"{r['nummer']} {r['besluit'].lower()}" for r in gestemd) + "."
    else:
        kort = "; ".join(f"Motie {r['nummer']} {r['besluit'].lower()} ({r['voor']}–{r['tegen']})" for r in gestemd) + "."
    lang = " ".join(f"Motie {r['nummer']} ({r['wie']}): " + (f"{r['besluit'].lower()}, {r['voor']} zetels voor en {r['tegen']} tegen." if r["besluit"] else "uitslag staat (nog) niet in onze gegevens.") for r in rij)
    return {"status": "gestemd" if not open_ else "open", "stand": stand, "kort": kort, "lang": lang, "moties": rij}


def afloop(pid):
    return afloop_data(pid)["lang"]


def bijwerken():
    """Voor de nachtelijke run: werk de afloop van alle kaarten bij en meld welke kaarten een nieuwe afloop kregen
    (die kunnen een vervolgpost krijgen: 'Zo stemde de Kamer')."""
    gewijzigd = []
    for f in sorted((ROOT / "data" / "proeftuin" / "botsing").glob("*.json")):
        k = json.loads(f.read_text())
        oud = (k.get("afloop_data") or {}).get("status")
        nieuw = afloop_data(f.stem)
        k["afloop_data"] = nieuw
        k["afloop"], k["afloop_kort"] = nieuw["lang"], nieuw["kort"]
        if oud and oud != nieuw["status"]:
            k.setdefault("afloop_historie", []).append({"van": oud, "naar": nieuw["status"], "datum": nieuw["stand"]})
            gewijzigd.append((f.stem, oud, nieuw["status"]))
        f.write_text(json.dumps(k, ensure_ascii=False, indent=1))
    for g in gewijzigd:
        print(f"nieuwe afloop: {g[0]} ({g[1]} → {g[2]}): vervolgpost 'Zo stemde de Kamer' mogelijk")
    print(f"{len(gewijzigd)} kaarten met een nieuwe afloop")


def voor(pid):
    p = laad(pid)
    B = p["beurten"]
    v = p["vergadering"]
    regels = [f"DEBAT {pid} | {p['titel']} | {v['datum']} | {v['soort']}" + (f" | deel: {p['deel'].get('fase')}" if p.get("deel") else ""),
              f"OPENING VOORZITTER: {B[0]['tekst'][:600] if B else ''}",
              f"PARTIJEN DIE SPRAKEN ({len(partijen(p))}): {', '.join(partijen(p))}",
              f"AFLOOP (alleen ter informatie; het script vult de afloop zelf in en werkt hem bij): {afloop(pid)}", ""]
    w = wisselingen(p)
    totaal = sum(len(b["tekst"].split()) for b in B if not is_vz(b)) or 1
    regels.append(f"TOTALE SPREEKTIJD (woorden, zonder voorzitter): {totaal}. Bijzaak = onderwerp met minder dan 10% daarvan "
                  f"({totaal // 10} woorden). Per beurt staat hieronder het aantal woorden.")
    if not w or len(w[0]) < 3:
        regels.append("GEEN ECHTE WISSELING (minder dan 3 beurten over en weer).")
    for n, c in enumerate(w[:3], 1):
        namen = " ↔ ".join(sorted({wie(B[i]) for i, _ in c}))
        wn = sum(len(B[i]["tekst"].split()) for i, _ in c)
        regels.append(f"=== WISSELING {n}: {namen}, {len(c)} beurten (beurt {c[0][0]}–{c[-1][0]}), {wn} woorden = {100 * wn // totaal}% van de spreektijd ===")
        for i, _ in c:
            regels.append(f"[{i}] {wie(B[i])} | {B[i]['rol']} | {len(B[i]['tekst'].split())} woorden\n{B[i]['tekst']}\n")
    regels.append("\nALLE BEURTEN (nummer, spreker, woorden, eerste regel) om de spreektijd per onderwerp te tellen:")
    for i, b in enumerate(B):
        if not is_vz(b):
            regels.append(f"[{i}] {wie(b)} | {len(b['tekst'].split())} w | {b['tekst'][:110]}")
    uit = ROOT / "data" / "compact" / f"kaart_{pid}.txt"
    uit.parent.mkdir(parents=True, exist_ok=True)
    uit.write_text("\n".join(regels))
    print(f"{uit}: {len(uit.read_text().split())} woorden, {len(w)} wisselingen")


def aandeel(pid, patroon):
    """Aandeel spreektijd van een onderwerp: woorden in de zinnen die het onderwerp noemen (regex, hoofdletterongevoelig),
    gedeeld door alle woorden zonder de voorzitter. Op zinsniveau, omdat één beurt vaak meer onderwerpen heeft."""
    p = laad(pid)
    tot = sum(len(b["tekst"].split()) for b in p["beurten"] if not is_vz(b)) or 1
    rx = re.compile(patroon, re.I)
    w, beurten = 0, []
    for i, b in enumerate(p["beurten"]):
        if is_vz(b):
            continue
        zinnen = [z for z in re.split(r"(?<=[.?!])\s+", b["tekst"]) if rx.search(z)]
        if zinnen:
            w += sum(len(z.split()) for z in zinnen); beurten.append(i)
    pct = round(100 * w / tot)
    print(f"{pct}% ({w} van {tot} woorden) in beurten {beurten[:12]}{'…' if len(beurten) > 12 else ''}"
          + (" → BIJZAAK (onder 10%)" if pct < 10 else ""))
    return pct, beurten


def check(pid):
    p = laad(pid)
    B = p["beurten"]
    f = ROOT / "data" / "proeftuin" / "botsing" / f"{pid}.json"
    k = json.loads(f.read_text())
    fouten = []
    for veld in ("kop", "vraag", "vraag_bron", "versies"):
        if not k.get(veld):
            fouten.append(f"veld '{veld}' ontbreekt")
    if k.get("vraag") and len(k["vraag"].split()) > 12:
        fouten.append(f"vraag heeft {len(k['vraag'].split())} woorden, hooguit 12")
    for naam, v in (k.get("versies") or {}).items():
        if "vraag" in v:
            fouten.append(f"versie {naam}: geen eigen 'vraag' in een versie; de vraag staat alleen op kaartniveau")
    uiterlijk = json.loads((ROOT / "data" / "uiterlijk.json").read_text())
    koppeling = json.loads((ROOT / "data" / "sprekers.json").read_text())
    for naam, v in (k.get("versies") or {}).items():
        cs = v.get("citaten") or []
        if not v.get("aandeel_onderwerp"):
            fouten.append(f"versie {naam}: 'aandeel_onderwerp' ontbreekt (geschat % spreektijd van het onderwerp, met de beurten waarop dat steunt)")
        beurten = [c.get("beurt") for c in cs]
        if len(beurten) == 2 and all(isinstance(x, int) for x in beurten) and beurten[0] > beurten[1]:
            fouten.append(f"versie {naam}: wie het eerst sprak staat bovenaan (beurt {beurten[1]} komt vóór {beurten[0]})")
        if not 1 <= len(cs) <= 2:
            fouten.append(f"versie {naam}: 1 of 2 citaten nodig")
        for c in cs:
            i = c.get("beurt")
            if not isinstance(i, int) or not 0 <= i < len(B):
                fouten.append(f"versie {naam}: ongeldige beurt {i}"); continue
            kern = re.sub(r"^…\s*|\s*…$", "", c["citaat"].strip())  # een weglating aan begin of eind mag, zichtbaar met "…"
            for s in [x.strip() for x in kern.split(" … ")]:
                if len(s.split()) < 5 or norm(s) not in norm(B[i]["tekst"]):
                    fouten.append(f"versie {naam}, beurt {i}: niet letterlijk of korter dan 5 woorden: {s[:60]}")
            zinnen = len(re.findall(r"[.?!](?:\s+(?![—–-])|$)", c["citaat"]))  # "? —" midden in een zin telt niet
            if zinnen > 2:
                fouten.append(f"versie {naam}, beurt {i}: {zinnen} zinnen, hooguit 2")
            sp = B[i]["spreker"]
            c.update({"naam": sp.get("naam") or sp["verslagnaam"],
                      "partij": sp["fractie"] or (sp.get("functie") or ""),  # voluit; de sociale beelden korten zelf in
                      "video": build.video_link(p, i), "tijd": (B[i].get("begin") or "")[11:16]})
            sl = koppeling.get(sp["id"]); u = uiterlijk.get(sl or "")
            kk = {x: u[x] for x in build.KENMERKEN if x in u} if u else None
            if kk and build.manga(sl):
                kk["manga"] = build.manga(sl)
            c["figuur"] = {"id": sp["id"], "fractie": sp.get("fractie") or "", "u": kk}
    k["partijen_totaal"] = len(partijen(p))
    ad = afloop_data(pid)  # altijd uit de data, nooit uit de schrijver
    k["afloop_data"], k["afloop"], k["afloop_kort"] = ad, ad["lang"], ad["kort"]
    f.write_text(json.dumps(k, ensure_ascii=False, indent=1))
    print(f"{pid}: {'OK' if not fouten else str(len(fouten)) + ' fout(en)'}")
    for x in fouten:
        print("  FOUT", x)
    return not fouten


if __name__ == "__main__":
    if sys.argv[1] == "bijwerken":
        bijwerken()
    elif sys.argv[1] == "aandeel":
        aandeel(sys.argv[2], sys.argv[3])
    else:
        {"voor": voor, "check": check}[sys.argv[1]](sys.argv[2])
