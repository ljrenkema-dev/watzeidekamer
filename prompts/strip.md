# Opdracht: agendapunt omzetten naar makkelijke taal en een strip

Je krijgt één agendapunt uit een debat van de Tweede Kamer (`data/agendapunten/<id>.json`).
Schrijf `data/strips/<id>.json`. Draai daarna `python3 scripts/check.py <id>` en los elke fout op tot de check slaagt.

## Taal (B1)
- Korte zinnen, hooguit 12 woorden. Gewone woorden. Actieve vorm.
- Leg vaktermen uit in `woorden`.

## Juistheid (belangrijkst)
- Gebruik ALLEEN wat in de spreekbeurten staat. Verzin niets. Geen eigen mening. Neutraal naar alle partijen.
- Getallen, data en standpunten precies zoals in de tekst.
- `citaat` is LETTERLIJK overgenomen uit de tekst van de spreekbeurt(en) van die spreker. Je mag inkorten door stukken te verbinden met " … ". Elk stuk moet minstens 5 woorden zijn en letterlijk in de tekst staan (leestekens en hoofdletters precies zo).
- `spreker_id` is de `spreker.id` uit het agendapunt. Gebruik `null` voor de Verteller (inleiding of afsluiting); het citaat van de Verteller mag uit elke spreekbeurt komen.
- Neem in `sprekers` iedere fractie op die in dit agendapunt sprak (voorzitter niet meegerekend). Kies per fractie de hoofdspreker.
- Bewindspersonen (minister, staatssecretaris) tellen als spreker zonder fractie.

## Strip
- 4 tot 8 vakken, in de volgorde van het debat, met de belangrijkste momenten.
- `tekst`: makkelijke versie van het citaat in de ik-vorm van de spreker, hooguit 14 woorden.
- `emotie`: neutraal, blij, boos, bezorgd, verbaasd, denkend of vastberaden — wat past bij de toon van het citaat.
- Laat de belangrijkste tegenstellingen zien. Geef geen partij meer vakken dan nodig.

## Vorm
```json
{
  "agendapunt": "<id>",
  "verslag_id": "<vergadering.verslag_id uit het agendapunt>",
  "niveau": "B1",
  "titel": "vraag of korte zin, max 10 woorden",
  "samenvatting": "3-5 zinnen",
  "sprekers": [{"id": "<spreker.id>", "standpunt": "1-2 zinnen"}],
  "kernpunten": ["..."],
  "woorden": [{"woord": "...", "uitleg": "..."}],
  "strip": [{"spreker_id": "<id of null>", "emotie": "neutraal", "tekst": "...", "citaat": "..."}]
}
```
