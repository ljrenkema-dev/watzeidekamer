# Wat zei de Kamer? — instructies voor Claude

Site: watzeidekamer.nl. Debatten uit de Tweede Kamer in normale taal (standaard) en makkelijke taal (knop), met een anime-strip waarin elk vak het letterlijke citaat toont.

## Branches
- Werk en push op `claude/fase-1-proef`. **Push niet naar `main`** tot de eigenaar zegt dat de site live mag; `main` is de productiebranch van Cloudflare Pages.

## Nachtelijke run
1. `python3 scripts/fetch.py <vandaag-7-dagen> <vandaag>` en `python3 scripts/parse.py`.
2. `python3 scripts/koppel.py` — koppelt sprekers aan figuren. Sprekers zonder figuur krijgen een neutraal figuur; noem ze in het verslag van de run (een figuur maken gebeurt apart, met keuring door de eigenaar).
3. `python3 scripts/todo.py 10` — de agendapunten voor deze nacht (plenair eerst, nieuwste eerst; hooguit 10). Punten boven 25.000 woorden slaat het over: die moeten eerst opgeknipt worden.
4. Maak per agendapunt een strip volgens `prompts/strip.md` (beide taalniveaus). Gebruik per agendapunt een eigen subagent, hooguit 5 tegelijk.
5. **Redactieronde**: laat per strip een tweede, aparte subagent nalezen tegen het agendapunt: zegt elke tekstballon (normaal en makkelijk) alleen wat in het citaat van dat vak staat; zijn samenvatting, standpunten en kernpunten juist en neutraal; krijgt geen partij onevenredig veel ruimte. Hij verbetert alleen teksten, nooit citaten om ze kloppend te maken.
6. `python3 scripts/check.py <id>` tot 0 fouten. Lukt dat niet, verwijder de strip en noem het in het verslag.
7. `python3 scripts/build.py`, commit `data/` (zonder `data/raw/` en `data/portret/`, die staan in .gitignore) en `public/`, en push naar `claude/fase-1-proef`.
8. Eindig met een kort verslag: hoeveel strips gemaakt of vernieuwd, welke overgeslagen en waarom, sprekers zonder figuur, en wat er misging.

## Regels
- Juistheid en neutraliteit gaan boven alles. Verzin nooit inhoud die niet in het verslag staat.
- Wijzig `scripts/check.py` niet om een strip erdoor te krijgen.
- Portretfoto's komen nooit op de site of in git.
- Verander geen goedgekeurde figuren in `data/uiterlijk.json` zonder keuring door de eigenaar (zie `docs/prompt-avatars-optimaliseren.md`).
