"""Pilot: manga-figuren per politicus met Gemini. Gebruik:
  python3 scripts/manga.py                         # de 5 pilotpolitici, alle emoties en houdingen
  python3 scripts/manga.py --namen "Geert Wilders" --emoties neutraal,boos
  python3 scripts/manga.py --emoties neutraal --stijl zw,kleur      # stap 1 van de pilot: stijlen vergelijken
Stijlen: zw (zwart-wit met partijkleur als accent) en kleur (gekleurde manga). Uitvoer per stijl in data/manga/<stijl>/.

Werkt via de gewone Gemini-API (generateContent); de API-sleutel zet de netwerkproxy erbij in de
header x-goog-api-key (netwerksleutel in de omgeving 'watzeidekamer'). Standaard gaat er GEEN portretfoto mee: de
beschrijving komt uit data/manga/beschrijvingen.json of data/uiterlijk.json. Alleen voor wie in beschrijvingen.json een
veld 'toestemming_foto' van de eigenaar heeft, gaat het officiële portret (data/portret/, niet in git) mee als voorbeeld
voor het neutrale beeld. De foto komt nooit op de site of in git.
Het neutrale beeld wordt daarna als voorbeeld meegestuurd voor de andere emoties.
Uitvoer: data/manga/<stijl>/<sleutel>/<emotie>.png of .jpg en een logboek met de gebruikte prompts.
"""
import base64, json, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
MODEL = "gemini-3.1-flash-image"
PILOT = ["Geert Wilders", "Jesse Klaver", "Mona Keijzer", "Caroline van der Plas", "Don Ceder"]
EMOTIES = {
    "neutraal": "calm, attentive, serious expression, mouth closed, no smile, relaxed neutral lips",
    "vriendelijk": "calm, friendly expression with the person's natural slight smile",
    "blij": "a warm, genuine smile",
    "boos": "frowning, firm mouth, clearly displeased but not shouting",
    "bezorgd": "inner eyebrows slightly raised, a concerned look",
    "verbaasd": "eyebrows raised, mouth slightly open in surprise",
    "denkend": "looking slightly up and to the side, one hand near the chin, thinking",
    "vastberaden": "a determined look, set jaw, steady eyes",
}
# Houdingen naast de emoties. De strip gebruikt 'interruptie' voor een vak waarin iemand interrumpeert.
HOUDINGEN = {
    "interruptie": ("Same character, now standing at a simple free-standing microphone in an aisle, leaning slightly "
                    "forward, one hand raised in a speaking gesture, a determined, engaged expression. Waist-up framing "
                    "instead of a bust, the microphone on a plain stand, still a plain white background, nothing else in the scene."),
}
STIJLEN = {}
STIJLEN["zw"] = ("Black-and-white manga illustration, clean confident ink lines, classic seinen style, screentone shading, "
         "subtle hatching, no colour except a single small accent colour on the tie or scarf. Expressive but restrained eyes. "
         "Bust portrait, facing the viewer, turned slightly to the right, plain white background, centred, the figure fills "
         "about 70% of the image height. Editorial newspaper-comic feel, respectful, not a caricature: no exaggerated features. "
         "No text, no letters, no logos, no flags, no symbols. No border, no frame, no panel outline: the white background runs to the edges.")
STIJLEN["kleur"] = ("Full-colour manga illustration in the style of a colour manga cover, clean confident ink lines, "
                    "soft cel shading with a few gradients, natural skin and hair colours, muted dark clothing with the tie or "
                    "scarf in the accent colour. Expressive but restrained eyes. Bust portrait, facing the viewer, turned slightly "
                    "to the right, plain white background, centred, the figure fills about 70% of the image height. Editorial "
                    "newspaper-comic feel, respectful, not a caricature: no exaggerated features. "
                    "No text, no letters, no logos, no flags, no symbols. No border, no frame, no panel outline: the white background runs to the edges.")
STIJLEN["manga"] = ("Full-colour Japanese manga / anime character illustration, clean confident ink lines, cel shading with "
                    "soft highlights, manga proportions: slightly larger expressive eyes, simplified nose and mouth, stylised hair "
                    "with clear shapes. The character must still be clearly recognisable from the description: keep the face shape, "
                    "hairstyle, hair colour, glasses and facial hair exactly as described. Natural skin and hair colours, muted dark "
                    "clothing with the tie or scarf in the accent colour. Bust portrait, facing the viewer, turned slightly to the right, "
                    "pure white background (#FFFFFF), centred, the figure fills about 75% of the image height. Respectful, "
                    "not a caricature: no exaggerated features. No text, no letters, no logos, no flags, no symbols. "
                    "No border, no frame, no panel outline: the white background runs to the edges.")
STIJL = STIJLEN["zw"]
FOTO_PROMPT = ("Redraw the person in this photo as a manga character. Keep the likeness: face shape, eyes and their size, "
               "eyebrows, nose, mouth and the lines around it, hairline, hairstyle including the exact shape and messiness of "
               "the hair ends, and apparent age. Do not make the person younger or prettier, and do not exaggerate any feature: "
               "respectful, not a caricature.\n\n{stijl}\nKeep their real clothing, but make the tie or scarf {kleur}. "
               "Calm expression with the person's natural slight smile. Remove the lapel pin. "
               "No text, no letters, no logos, no flags.")
BESCHRIJVINGEN = ROOT / "data" / "manga" / "beschrijvingen.json"
HAAR = {"zwart": "black", "donkerbruin": "dark brown", "bruin": "brown", "lichtbruin": "light brown", "blond": "blond",
        "platinablond": "platinum-blond", "rood": "red", "grijs": "grey", "wit": "white"}
KAPSEL = {"kort": "short", "kort-scheiding": "short with a side parting", "kort-kuif": "short with a combed-back quiff",
          "kort-stekels": "short and slightly spiky", "kort-golf": "short and wavy", "kort-krul": "short and curly",
          "opgeschoren": "very short, buzzed", "kort-kort": "cropped very short", "kort-dun": "short and thinning",
          "kort-inham": "short with a receding hairline", "kaal": "bald", "kaal-rand": "bald on top with hair at the sides",
          "kaal-krul": "bald on top with curly hair at the sides", "half-lang": "shoulder-length", "half-lang-krul": "shoulder-length and curly",
          "half-lang-golf": "shoulder-length and wavy", "lang": "long and straight", "lang-krul": "long and curly",
          "vlechten": "long braids", "staart": "tied back in a ponytail", "knot": "tied up in a bun"}
LEEFTIJD = {"jong": "in their thirties", "midden": "in their forties or fifties", "ouder": "in their sixties"}
HUID = {"licht": "light skin", "middel": "medium skin", "donker": "dark skin"}
BRIL = {"geen": "no glasses", "rechthoek": "rectangular glasses", "rond": "round glasses"}
BAARD = {"geen": "clean-shaven", "stoppel": "light stubble", "kort": "a short, neat beard"}
ACCENT = {"PVV": "dark blue", "PRO": "red", "Lid Keijzer": "teal", "BBB": "green", "ChristenUnie": "light blue",
          "VVD": "orange", "D66": "green", "CDA": "green", "JA21": "navy", "SP": "red", "DENK": "turquoise",
          "PvdD": "dark green", "SGP": "orange", "FVD": "dark red", "50PLUS": "purple", "Volt": "purple",
          "Groep Markuszower": "dark grey"}


def beschrijving(u, sleutel=None):
    """Eigen beschrijving naar het portret (data/manga/beschrijvingen.json) als die er is, anders uit de kenmerken."""
    if sleutel and BESCHRIJVINGEN.exists():
        eigen = json.loads(BESCHRIJVINGEN.read_text()).get(sleutel)
        if eigen and eigen.get("beschrijving"):
            kleur = ACCENT.get(u.get("fractie") or "", "dark grey")
            return "A fictional Dutch politician. " + eigen["beschrijving"].replace("the accent colour", f"{kleur}")
    return beschrijving_kenmerken(u)


def foto_toegestaan(sleutel):
    """Portret mag mee naar Gemini als de eigenaar dat voor deze persoon heeft goedgekeurd en het portret lokaal staat."""
    eigen = json.loads(BESCHRIJVINGEN.read_text()).get(sleutel, {}) if BESCHRIJVINGEN.exists() else {}
    pad = ROOT / "data" / "portret" / (sleutel.replace(":", "-") + ".jpg")
    return pad if eigen.get("toestemming_foto") and pad.exists() else None


def beschrijving_kenmerken(u):
    wie = "a man" if u.get("gezicht") == "m" else "a woman"
    haar = ("bald head" if u.get("kapsel") == "kaal"
            else f"{HAAR.get(u.get('haarkleur'), 'brown')} hair, {KAPSEL.get(u.get('kapsel'), 'short')}")
    kleur = ACCENT.get(u.get("fractie") or "", "dark grey")
    kleding = (f"wearing a dark suit with a {kleur} tie" if u.get("gezicht") == "m"
               else f"wearing a dark blazer with a small {kleur} scarf")
    delen = [f"A fictional Dutch politician {LEEFTIJD.get(u.get('leeftijd'), '')}, {wie}", haar,
             BRIL.get(u.get("bril"), "no glasses")]
    if u.get("gezicht") == "m":
        delen.append(BAARD.get(u.get("baard"), "clean-shaven"))
    delen += [HUID.get(u.get("huid"), "light skin"), kleding]
    return ", ".join(d for d in delen if d) + "."


def vraag(delen):
    """Gewone Gemini-API (generateContent). De sleutel zet de netwerkproxy in de header x-goog-api-key."""
    body = json.dumps({"contents": [{"role": "user", "parts": delen}],
                       "generationConfig": {"responseModalities": ["IMAGE", "TEXT"],
                                            "imageConfig": {"aspectRatio": "3:4"}}}).encode()
    req = urllib.request.Request(URL.format(model=MODEL), data=body,
                                 headers={"x-goog-api-key": "proxy-injected", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.loads(r.read())


def zoek_beeld(antwoord):
    """Eerste afbeelding in het antwoord: (bytes, extensie) of (None, None)."""
    for c in antwoord.get("candidates", []):
        for d in (c.get("content") or {}).get("parts", []):
            inl = d.get("inlineData") or d.get("inline_data")
            if inl and inl.get("data"):
                mime = inl.get("mimeType") or inl.get("mime_type") or "image/png"
                return base64.b64decode(inl["data"]), {"image/jpeg": "jpg", "image/webp": "webp"}.get(mime, "png")
    return None, None


def bestaand(map_, emo):
    return next(iter(sorted(map_.glob(f"{emo}.*[gp]"))), None)


def maak(sleutel, u, emoties, log, stijl="zw"):
    """Volgorde: met portretfoto eerst 'vriendelijk' (naar de foto, met de eigen lichte glimlach), dan 'neutraal'
    (zelfde figuur, zonder lach) met 'vriendelijk' als voorbeeld; daarna de andere emoties met 'neutraal' als voorbeeld."""
    map_ = ROOT / "data" / "manga" / stijl / sleutel.replace(":", "-")
    map_.mkdir(parents=True, exist_ok=True)
    basis = f"{STIJLEN[stijl]}\n\nCharacter: {beschrijving(u, sleutel)}"
    met_foto = bool(foto_toegestaan(sleutel))
    eerst = (["vriendelijk"] if met_foto else []) + ["neutraal"]
    for emo in eerst + [e for e in emoties if e not in eerst]:
        if emo not in emoties and bestaand(map_, emo):
            continue
        if bestaand(map_, emo):
            continue
        tekst_houding = HOUDINGEN.get(emo)
        tekst = f"{basis}\n{tekst_houding}" if tekst_houding else f"{basis}\nExpression: {EMOTIES[emo]}."
        delen = [{"text": tekst}]
        foto = foto_toegestaan(sleutel) if emo == "vriendelijk" else None
        if foto:
            tekst = FOTO_PROMPT.format(stijl=STIJLEN[stijl], kleur=ACCENT.get(u.get("fractie") or "", "dark grey"))
            delen = [{"text": tekst}, {"inlineData": {"mimeType": "image/jpeg",
                                                      "data": base64.b64encode(foto.read_bytes()).decode()}}]
        ref = bestaand(map_, "vriendelijk" if emo == "neutraal" else "neutraal")
        if emo == "neutraal" and ref and ref.stem == "vriendelijk":
            # Alleen de uitdrukking aanpassen; geen tekstbeschrijving, die kan botsen met het beeld (bijv. een bril toevoegen).
            tekst = ("Edit this image. Keep exactly the same person, face shape, eyes, hair, glasses or no glasses, facial hair, "
                     "clothing, colours, drawing style, framing and white background. Change only the facial expression: "
                     f"{EMOTIES['neutraal']}. Do not add or remove anything else: no glasses, accessories, text or frame "
                     "unless they are already in the image.")
        if not foto and ref:
            mime = "image/jpeg" if ref.suffix == ".jpg" else "image/png"
            delen = [{"text": tekst if tekst.startswith("Edit this image") else
                      "Draw exactly the same character as in this reference image, same face, hair, clothes, "
                      "style and framing; only change what is described below.\n\n" + tekst},
                     {"inlineData": {"mimeType": mime, "data": base64.b64encode(ref.read_bytes()).decode()}}]
        antwoord = None
        for poging in range(6):  # bij een tijdelijke limiet (429) of een antwoord zonder beeld: wachten en opnieuw
            try:
                antwoord = vraag(delen)
            except urllib.error.HTTPError as e:
                if e.code == 429 and poging < 5:
                    print(f"  {u['naam']} {emo}: limiet (429), wacht {60 * (poging + 1)} s"); time.sleep(60 * (poging + 1)); continue
                antwoord = e
                break
            if zoek_beeld(antwoord)[0] or poging >= 2:
                break
            print(f"  {u['naam']} {emo}: geen afbeelding, opnieuw"); time.sleep(5)
        try:
            if isinstance(antwoord, urllib.error.HTTPError):
                raise antwoord
        except urllib.error.HTTPError as e:
            fout = e.read().decode()[:400]
            log.append({"wie": u["naam"], "emotie": emo, "stijl": stijl, "fout": f"HTTP {e.code}: {fout}"})
            print(f"  {u['naam']} {emo}: HTTP {e.code}")
            if e.code in (401, 403):
                raise SystemExit("Sleutel geweigerd (401/403). Staat de netwerksleutel op de header x-goog-api-key?")
            if e.code == 429:
                raise SystemExit("Quotum op (429). Probeer later opnieuw.")
            continue
        beeld, ext = zoek_beeld(antwoord)
        if not beeld:
            (map_ / f"{emo}.antwoord.json").write_text(json.dumps(antwoord, ensure_ascii=False)[:20000])
            log.append({"wie": u["naam"], "emotie": emo, "stijl": stijl, "fout": "geen afbeelding in het antwoord"})
            print(f"  {u['naam']} {emo}: geen afbeelding (antwoord bewaard)")
            continue
        uit = map_ / f"{emo}.{ext}"
        uit.write_bytes(beeld)
        log.append({"wie": u["naam"], "emotie": emo, "stijl": stijl, "prompt": tekst, "model": MODEL,
                    "portretfoto_meegestuurd": bool(foto)})
        print(f"  {u['naam']} {emo}: {len(beeld) // 1024} kB")
        time.sleep(2)


def main(namen, emoties, stijlen, logpad=None):
    uiterlijk = json.loads((ROOT / "data" / "uiterlijk.json").read_text())
    log = []
    logpad = logpad or ROOT / "data" / "manga" / "log.json"
    for naam in namen:
        sleutel, u = next(((k, v) for k, v in uiterlijk.items() if v["naam"] == naam), (None, None))
        if not u:
            print(f"onbekend: {naam}"); continue
        print(naam, "→", beschrijving(u, sleutel)[:140])
        for stijl in stijlen:
            maak(sleutel, u, emoties, log, stijl)
        oud = json.loads(logpad.read_text()) if logpad.exists() else []
        logpad.write_text(json.dumps(oud + log, ensure_ascii=False, indent=1))
        log = []


if __name__ == "__main__":
    a = sys.argv[1:]
    namen = a[a.index("--namen") + 1].split(",") if "--namen" in a else PILOT
    if "--alle" in a:  # iedereen met een figuur, behalve de pilot; --deel i/n verdeelt het werk over n processen
        # alleen wie een lokaal portret en toestemming heeft; de rest wordt gemeld
        alle_u = json.loads((ROOT / "data" / "uiterlijk.json").read_text())
        alle = sorted(v["naam"] for k, v in alle_u.items() if foto_toegestaan(k))
        overgeslagen = sorted(v["naam"] for k, v in alle_u.items() if not foto_toegestaan(k) and v["naam"] not in PILOT)
        if overgeslagen and ("--deel" not in a or a[a.index("--deel") + 1].startswith("1/")):
            print("zonder portret of toestemming, overgeslagen:", ", ".join(overgeslagen))
        namen = [n for n in alle if n not in PILOT]
        if "--deel" in a:
            i, n = map(int, a[a.index("--deel") + 1].split("/"))
            namen = namen[i - 1::n]
    logpad = Path(a[a.index("--log") + 1]) if "--log" in a else None
    emoties = a[a.index("--emoties") + 1].split(",") if "--emoties" in a else list(EMOTIES) + list(HOUDINGEN)
    stijlen = a[a.index("--stijl") + 1].split(",") if "--stijl" in a else ["zw"]
    main(namen, emoties, stijlen, logpad)
