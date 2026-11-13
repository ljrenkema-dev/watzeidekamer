# Wat zei de Kamer? — instructies voor Claude

Site: watzeidekamer.nl. Debatten uit de Tweede Kamer in normale taal (standaard) en makkelijke taal (knop), met een anime-strip waarin elk vak het letterlijke citaat toont.

## Branches
- Werk en push op `claude/fase-1-proef`. **Push niet naar `main`** tot de eigenaar zegt dat de site live mag; `main` is de productiebranch van Cloudflare Pages.

## Nachtelijke run
**Proefperiode (sinds 13 november 2026): alleen data, geen nieuwe strips.** We verbeteren de schrijfopdracht eerst op vijf testdebatten in de proeftuin (`scripts/proeftuin.py`, `data/proeftuin/`). Doe tot de eigenaar iets anders zegt alleen stap 1, 2, 6b en 7 (ophalen, koppelen, verzoeken, corpus, bouwen, committen) en sla stap 3 tot en met 6 over. Bestaande strips blijven staan; werk alleen hun `verslag_id` bij als het verslag een nieuwe versie kreeg met ongewijzigde spreekbeurten (en draai dan `check.py`). Noem in het verslag van de run hoeveel nieuwe agendapunten er klaarstaan voor later.

1. `python3 scripts/fetch.py <vandaag-7-dagen> <vandaag>` en `python3 scripts/parse.py`. Daarna `python3 scripts/debatdirect.py`: haalt per debat de spreekmomenten uit Debat Direct op (`data/debatdirect/`), zodat elk citaat linkt naar het moment in de video. Lukt dat niet, ga dan door; de strip werkt ook zonder videolink. Daarna `python3 scripts/moties.py`: haalt de in de debatten genoemde moties op (indieners, tekst, oordeel kabinet) en werkt stemuitslagen bij (`data/moties/`). Vereist `pdftotext` (poppler-utils).
2. `python3 scripts/koppel.py` — koppelt sprekers aan figuren. Sprekers zonder figuur krijgen een neutraal figuur; noem ze in het verslag van de run (een figuur maken gebeurt apart, met keuring door de eigenaar).
3. `python3 scripts/todo.py 10` — de agendapunten voor deze nacht (plenair eerst, nieuwste eerst; hooguit 10). `parse.py` knipt debatten boven 16.000 woorden al in delen (`<id>-d1`, `-d2`, …) langs spreekbeurten en fases (inbreng Kamer, antwoord kabinet, tweede termijn); elk deel krijgt een eigen strip. Delen van één debat staan in `todo.py` bij elkaar; maak ze bij voorkeur in dezelfde nacht.
4. Maak per agendapunt een strip volgens `prompts/strip.md` (beide taalniveaus). Gebruik per agendapunt een eigen subagent, hooguit 5 tegelijk.
5. **Redactie in twee lezingen**, elk door een eigen, nieuwe subagent die de strip nog niet kent. Start de schrijver en beide lezers **vanuit de hoofdsessie** als drie aparte subagents, na elkaar; een subagent kan zelf geen subagents starten en mag zijn eigen werk niet als onafhankelijke lezing nalezen:
   - **Eerste lezing**: volgens `prompts/redacteur.md`. Leest na tegen het agendapunt (ballon tegen citaat, samenvatting en standpunten, neutraliteit, ruimte per partij met `scripts/evenwicht.py`), verbetert teksten en schrijft `data/redactie/<id>.json`.
   - **Tweede lezing**: volgens het deel "Tweede lezing" in `prompts/redacteur.md`. Zoekt wat de eerste lezing miste en controleert vooral de wijzigingen van de eerste redacteur, verwerkt wat klopt en legt het vast onder `tweede_lezing` in hetzelfde redactieverslag.
   Op **zondag** doet de redacteur ook de wekelijkse controle van de hele site (zie het einde van `prompts/redacteur.md`), ook in twee lezingen.
   **Leren van fouten**: draai daarna `python3 scripts/lessen.py`. Zie je een fout die nog niet in `prompts/lessen.md` staat en die in deze run twee keer of vaker voorkwam (of één keer met ernst "groot"), voeg dan een les toe of breid een bestaande les uit, met een echt voorbeeld (fout → goed). Gaat een bestaande les steeds weer mis, maak hem dan scherper. Houd de lijst op hooguit 15 lessen. Noem de wijziging in het verslag van de run.
6. `python3 scripts/check.py <id>` tot 0 fouten. Lukt dat niet, verwijder de strip en noem het in het verslag.
6b. **Verzoeken**: voor elke regeling van werkzaamheden in `data/procedure/` (met Kamerlid-spreekbeurten) waarvoor nog geen `data/verzoeken/<id>.json` is, of waarvan het verslag een nieuwere versie heeft: één subagent volgens `prompts/verzoeken.md`, daarna `python3 scripts/verzoeken_check.py <id>` tot 0 fouten. Draai `python3 scripts/zetels.py` en `python3 scripts/verzoeken_overzicht.py`; staat er bij een verzoek "past bij zetels: nee", controleer dan de reacties en de uitkomst opnieuw tegen het verslag. Niet op de site; voor analyses.
7. `python3 scripts/corpus.py` (alle gesproken tekst per politicus in `data/corpus/`, voor analyses; niet op de site). Dan `python3 scripts/build.py`, commit `data/` (zonder `data/raw/` en `data/portret/`, die staan in .gitignore) en `public/`, en push naar `claude/fase-1-proef`.
8. Eindig met een kort verslag: hoeveel strips gemaakt of vernieuwd, welke overgeslagen en waarom, sprekers zonder figuur, en wat er misging.

## Regels
- Juistheid en neutraliteit gaan boven alles. Verzin nooit inhoud die niet in het verslag staat.
- Wijzig `scripts/check.py` niet om een strip erdoor te krijgen.
- Portretfoto's komen nooit op de site of in git.
- Verander geen goedgekeurde figuren in `data/uiterlijk.json` zonder keuring door de eigenaar (zie `docs/prompt-avatars-optimaliseren.md`).
