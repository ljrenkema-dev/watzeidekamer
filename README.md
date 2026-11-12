# Wat zei de Kamer?

Debatten uit de Tweede Kamer in normale taal, met een anime-strip waarin elk vak het letterlijke citaat toont. Site: watzeidekamer.nl (Cloudflare Pages, map `public/`).

## Hoe het werkt

1. `scripts/fetch.py VAN TOT` haalt vergaderingen en het nieuwste verslag op via de open data van de Tweede Kamer (`gegevensmagazijn.tweedekamer.nl`). Ruwe XML komt in `data/raw/` (niet in git).
2. `scripts/parse.py` knipt elk verslag op in agendapunten met spreekbeurten: `data/agendapunten/<id>.json`.
3. Claude schrijft per agendapunt `data/strips/<id>.json` volgens `prompts/strip.md`.
4. `scripts/check.py <id>` controleert of elk citaat letterlijk bij die spreker staat. Een strip met fouten wordt niet gepubliceerd.
5. `scripts/build.py` bouwt de statische site in `public/`.

Alleen de Python-standaardbibliotheek, geen afhankelijkheden.

## Cloudflare Pages

- Build command: leeg
- Output directory: `public`
- Productie-branch: `main`

## Corpus per politicus

`scripts/corpus.py` schrijft alle gesproken tekst per spreker naar `data/corpus/<naam>.jsonl.gz` (één regel per spreekbeurt, letterlijk uit het verslag, met datum, agendapunt, rol en fractie) en een overzicht in `data/corpus/index.json`. Bedoeld voor analyses; het staat niet op de site. Het corpus wordt elke run opnieuw opgebouwd uit `data/agendapunten/`, zodat gecorrigeerde verslagen de oude tekst vervangen.

Voorbeeld:
```python
import gzip, json
beurten = [json.loads(r) for r in gzip.open("data/corpus/geert-wilders.jsonl.gz", "rt")]
```

## Procedure, presentie en verzoeken

- `data/procedure/<id>.json`: opening, mededelingen, regeling van werkzaamheden en sluiting. Met `aanwezig` en `kamerleden_aanwezig` (presentielijst uit de opening), `afgemeld` (berichten van verhindering), `voorzitter`, `griffier` en alle spreekbeurten.
- `data/verzoeken/<id>.json`: per regeling van werkzaamheden de verzoeken (wie, wat, onderwerp), elke reactie met oordeel (steun, geen steun, alleen brief, onduidelijk) en letterlijk citaat, en de uitkomst volgens de voorzitter. Gecontroleerd met `scripts/verzoeken_check.py`.

