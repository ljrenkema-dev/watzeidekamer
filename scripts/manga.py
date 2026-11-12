"""Pilot: manga-figuren per politicus met Gemini. Gebruik:
  python3 scripts/manga.py                         # de 5 pilotpolitici, alle emoties en houdingen
  python3 scripts/manga.py --namen "Geert Wilders" --emoties neutraal,boos
  python3 scripts/manga.py --emoties neutraal --stijl zw,kleur      # stap 1 van de pilot: stijlen vergelijken
Stijlen: zw (zwart-wit met partijkleur als accent) en kleur (gekleurde manga). Uitvoer per stijl in data/manga/<stijl>/.

Werkt via het OpenAI-compatibele adres van Gemini; de API-sleutel zet de netwerkproxy erbij
(Authorization: Bearer). Er gaat GEEN portretfoto mee: de beschrijving komt uit data/uiterlijk.json.
Het neutrale beeld wordt daarna als voorbeeld meegestuurd voor de andere emoties.
Uitvoer: data/manga/<stijl>/<sleutel>/<emotie>.png en een logboek met de gebruikte prompts.
"""
import base64, json, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
MODEL = "gemini-3.1-flash-image"
PILOT = ["Geert Wilders", "Jesse Klaver", "Mona Keijzer", "Caroline van der Plas", "Don Ceder"]
EMOTIES = {
    "neutraal": "calm, attentive expression, mouth closed",
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
         "No text, no letters, no logos, no flags, no symbols.")
STIJLEN["kleur"] = ("Full-colour manga illustration in the style of a colour manga cover, clean confident ink lines, "
                    "soft cel shading with a few gradients, natural skin and hair colours, muted dark clothing with the tie or "
                    "scarf in the accent colour. Expressive but restrained eyes. Bust portrait, facing the viewer, turned slightly "
                    "to the right, plain white background, centred, the figure fills about 70% of the image height. Editorial "
                    "newspaper-comic feel, respectful, not a caricature: no exaggerated features. "
                    "No text, no letters, no logos, no flags, no symbols.")
STIJL = STIJLEN["zw"]
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


def beschrijving(u):
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


def vraag(berichten):
    body = json.dumps({"model": MODEL, "messages": berichten, "modalities": ["image", "text"]}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Authorization": "Bearer proxy-injected",
                                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.loads(r.read())


def zoek_beeld(obj):
    """Zoek een base64-afbeelding in het antwoord, waar die ook staat (data-URI of b64-veld)."""
    s = json.dumps(obj)
    m = re.search(r"data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=]{200,})", s)
    if m:
        return base64.b64decode(m.group(2))
    m = re.search(r'"(?:b64_json|data)"\s*:\s*"([A-Za-z0-9+/=]{200,})"', s)
    return base64.b64decode(m.group(1)) if m else None


def maak(sleutel, u, emoties, log, stijl="zw"):
    map_ = ROOT / "data" / "manga" / stijl / sleutel.replace(":", "-")
    map_.mkdir(parents=True, exist_ok=True)
    basis = f"{STIJLEN[stijl]}\n\nCharacter: {beschrijving(u)}"
    neutraal = map_ / "neutraal.png"
    for emo in ["neutraal"] + [e for e in emoties if e != "neutraal"]:
        if emo in HOUDINGEN:
            tekst_houding = HOUDINGEN[emo]
        else:
            tekst_houding = None
        if emo not in emoties and neutraal.exists():
            continue
        uit = map_ / f"{emo}.png"
        if uit.exists():
            continue
        tekst = f"{basis}\n{tekst_houding}" if tekst_houding else f"{basis}\nExpression: {EMOTIES[emo]}."
        inhoud = [{"type": "text", "text": tekst}]
        if emo != "neutraal" and neutraal.exists():
            inhoud = [{"type": "text", "text": "Draw exactly the same character as in this reference image, same face, hair, clothes, "
                                               "style and framing; only change the expression.\n\n" + tekst},
                      {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(neutraal.read_bytes()).decode()}}]
        try:
            antwoord = vraag([{"role": "user", "content": inhoud}])
        except urllib.error.HTTPError as e:
            fout = e.read().decode()[:400]
            log.append({"wie": u["naam"], "emotie": emo, "fout": f"HTTP {e.code}: {fout}"})
            print(f"  {u['naam']} {emo}: HTTP {e.code}")
            if e.code == 429:
                raise SystemExit("Quotum op (429). Zet betalen aan in Google AI Studio of probeer later opnieuw.")
            continue
        beeld = zoek_beeld(antwoord)
        if not beeld:
            (map_ / f"{emo}.antwoord.json").write_text(json.dumps(antwoord, ensure_ascii=False)[:20000])
            log.append({"wie": u["naam"], "emotie": emo, "fout": "geen afbeelding in het antwoord"})
            print(f"  {u['naam']} {emo}: geen afbeelding (antwoord bewaard)")
            continue
        uit.write_bytes(beeld)
        log.append({"wie": u["naam"], "emotie": emo, "stijl": stijl, "prompt": tekst, "model": MODEL})
        print(f"  {u['naam']} {emo}: {len(beeld) // 1024} kB")
        time.sleep(2)


def main(namen, emoties, stijlen):
    uiterlijk = json.loads((ROOT / "data" / "uiterlijk.json").read_text())
    log = []
    for naam in namen:
        sleutel, u = next(((k, v) for k, v in uiterlijk.items() if v["naam"] == naam), (None, None))
        if not u:
            print(f"onbekend: {naam}"); continue
        print(naam, "→", beschrijving(u))
        for stijl in stijlen:
            maak(sleutel, u, emoties, log, stijl)
    logpad = ROOT / "data" / "manga" / "log.json"
    oud = json.loads(logpad.read_text()) if logpad.exists() else []
    logpad.write_text(json.dumps(oud + log, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    a = sys.argv[1:]
    namen = a[a.index("--namen") + 1].split(",") if "--namen" in a else PILOT
    emoties = a[a.index("--emoties") + 1].split(",") if "--emoties" in a else list(EMOTIES) + list(HOUDINGEN)
    stijlen = a[a.index("--stijl") + 1].split(",") if "--stijl" in a else ["zw"]
    main(namen, emoties, stijlen)
