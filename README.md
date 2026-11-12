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
