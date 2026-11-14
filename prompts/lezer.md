# Opdracht: onafhankelijke lezing van een debatpagina en de kaart

Je leest de pagina (`data/paginas/<id>.json`, opdracht in `prompts/pagina.md`) en de botsingskaart (`data/proeftuin/botsing/<id>.json`, opdracht in `prompts/kaart.md`) van één agendapunt na. Je kent ze nog niet en je hebt ze niet geschreven. Juistheid en neutraliteit gaan boven alles.

Lees: `prompts/pagina.md`, `prompts/kaart.md` (vooral "Wat je kiest" en "Lezer"), `prompts/lessen.md`, het agendapunt `data/agendapunten/<id>.json` (alle beurten; index = beurtnummer) en, als die er is, `data/moties/<id>.json`.

## Pagina
1. **Samenvatting en kernpunten**: klopt elke bewering met het verslag? Niets toegevoegd, getallen precies, geen voorbehoud weggevallen, beweringen van één spreker als "volgens X"?
2. **Standpunten**: staat elke fractie die sprak erin, en komt elk standpunt overeen met wat die spreker zelf zei (niet wat een ander over hem zei)?
3. **Evenwicht**: krijgt geen kant meer ruimte of vriendelijker woorden dan de andere? Draai `python3 scripts/evenwicht.py <id>` als dat script met deze pagina werkt; anders tel je zelf de vermeldingen per fractie in samenvatting en kernpunten.
4. **Vorm**: bij een vragenuur of een debat dat een lijst afloopt een opsomming met "- " en onderwerpen; bij een deel van een debat alleen dat deel, zonder volgnummer.
5. **Moeilijke woorden**: juiste, neutrale uitleg.

## Kaart
Controleer de kaart volgens het deel "Lezer" in `prompts/kaart.md`: de bron van de vraag, de keuze van de wisseling (geen bijzaak, wie het eerst sprak bovenaan), letterlijke citaten zonder weggevallen voorbehoud, en of kaart en pagina elkaar niet tegenspreken.

## Lichte verwerking
Geeft `python3 scripts/zwaarte.py <id>` "licht" (ordedebat, stemmingen, tweeminutendebat of een kort debat), dan is er geen kaart: lees alleen de pagina na, punt 1, 2 en 4 hierboven. Zet in het verslag `"soort": "pagina (licht)"`.

## Uitvoer
Verbeter wat niet klopt direct in de bestanden. Draai daarna `python3 scripts/check_pagina.py <id>` en `python3 scripts/kaart.py check <id>` tot beide OK zijn. Schrijf `data/redactie/<id>.json`:
```json
{"agendapunt": "<id>", "verslag_id": "...", "datum": "<jjjj-mm-dd>", "onafhankelijk": true, "soort": "pagina+kaart",
 "oordeel": "akkoord | aangepast",
 "bevindingen": [{"waar": "samenvatting | standpunt <fractie> | kernpunt n | kaart ...", "ernst": "klein | middel | groot",
                  "was": "...", "nu": "...", "bron": "beurt n: '...'"}]}
```
Wijzig geen scripts en commit niets. Eindig met je bevindingen in het kort.
