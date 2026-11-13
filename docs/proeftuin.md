# Proeftuin: werkwijze per ronde

Vijf vaste testdebatten (`scripts/proeftuin.py`, lijst `TEST`). Artifact: https://claude.ai/artifact/HayjHBPatKQJhuzVi66PhY
Feedback staat in de artifact-database, collectie `feedback`, doc-id `<versie>__<debat>__<onderdeel>`.

## Een ronde
1. Lees de feedback van de huidige versie uit en verwerk wat terugkomt in `prompts/strip.md`, `prompts/redacteur.md` of `prompts/lessen.md`. Leg per opmerking vast wat ermee gedaan is (`data/proeftuin/<versie>/verwerkt.json`).
2. Maak de vijf strips opnieuw in `data/proeftuin/<nieuwe versie>/<id>.json` (niet in `data/strips/`).
3. `python3 scripts/check.py` moet ook voor de proefversie slagen: kopieer tijdelijk of controleer met dezelfde regels.
4. `python3 scripts/proeftuin.py <nieuwe versie> <vorige versie>` en publiceer naar dezelfde artifact-URL.

## Goedkopere opzet (te testen vanaf v2)
Per strip drie agents, zoals nu, maar:
- **Invoer**: `python3 scripts/compact.py <id>` → `data/compact/<id>.txt` (alleen spreekbeurten, zonder korte ordezaken; ca. 30% kleiner). De schrijver en de eerste lezer lezen dit bestand in plaats van de JSON.
- **Schrijver** en **eerste lezing**: lichter model (Sonnet). Eén keer schrijven, één keer `check.py`, alleen fouten herstellen.
- **Tweede lezing**: zwaar model (Opus), met de volledige bron.
- Vergelijk per ronde de kosten (sessiekosten voor en na) en de kwaliteit (feedback eigenaar, aantal bevindingen per lezing) met de dure opzet. Pas over als de kwaliteit gelijk blijft.
