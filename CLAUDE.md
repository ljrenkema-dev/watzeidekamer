# Wat zei de Kamer? — instructies voor Claude

## Nachtelijke run
1. `python3 scripts/fetch.py <gisteren-7> <vandaag>` en daarna `python3 scripts/parse.py`.
2. Zoek agendapunten zonder strip, of waarvan de strip een ander `verslag_id` heeft dan het agendapunt (nieuwere versie van het verslag).
3. Maak voor elk zo'n agendapunt een strip volgens `prompts/strip.md`. Voorrang: plenaire debatten, daarna commissies. Sla agendapunten van soort "Stemmingen" en "Regeling van werkzaamheden" over.
4. Draai `python3 scripts/check.py <id>` tot 0 fouten. Lukt dat niet, laat de strip weg en noem het in de commit.
5. `python3 scripts/build.py`, commit `data/agendapunten`, `data/strips`, `data/vergaderingen.json` en `public/`, en push naar `main`.

## Regels
- Juistheid en neutraliteit gaan boven alles. Verzin nooit inhoud die niet in het verslag staat.
- Wijzig `scripts/check.py` niet om een strip erdoor te krijgen.
