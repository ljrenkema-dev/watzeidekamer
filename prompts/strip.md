# Opdracht: agendapunt samenvatten in twee taalniveaus en een strip maken

Je krijgt één agendapunt uit een debat van de Tweede Kamer (`data/agendapunten/<id>.json`).
Schrijf `data/strips/<id>.json`. Draai daarna `python3 scripts/check.py <id>` en los elke fout op tot de check slaagt.

## Twee taalniveaus
Elke tekst schrijf je twee keer, onder `normaal` en `makkelijk`. Beide versies zeggen inhoudelijk hetzelfde.
- **normaal** (standaard op de site): heldere, gewone taal zoals een goede nieuwssite. Zinnen tot ongeveer 20 woorden. Houd getallen, nuances en wie-wat-vindt precies. Geen jargon zonder uitleg.
- **makkelijk**: korte zinnen van hooguit 12 woorden, alledaagse woorden, actieve vorm. Voor laaggeletterden en mensen die Nederlands leren.

## Juistheid (belangrijkst)
- Gebruik ALLEEN wat in de spreekbeurten staat. Verzin niets. Geen eigen mening. Neutraal naar alle partijen.
- Getallen, data en standpunten precies zoals in de tekst, in beide versies.
- `citaat` is LETTERLIJK overgenomen uit de tekst van de spreekbeurt(en) van die spreker. Je mag inkorten door stukken te verbinden met " … ". Elk stuk moet minstens 5 woorden zijn en letterlijk in de tekst staan (leestekens en hoofdletters precies zo).
- De `tekst` in een stripvak zegt niets wat niet in het citaat van dat vak staat.
- `spreker_id` is de `spreker.id` uit het agendapunt. Gebruik `null` voor de Verteller (inleiding of afsluiting); het citaat van de Verteller mag uit elke spreekbeurt komen.
- Neem in `sprekers` iedere fractie op die in dit agendapunt sprak (voorzitter niet meegerekend). Kies per fractie de hoofdspreker.
- Bewindspersonen (minister, staatssecretaris) tellen als spreker zonder fractie.
- `woorden` legt vaktermen uit. Gebruik zo veel mogelijk de uitleg uit het debat zelf; algemene kennis alleen als die vaststaat en neutraal is.

## Strip
- 4 tot 8 vakken, in de volgorde van het debat, met de belangrijkste momenten.
- `tekst`: wat de spreker in dat vak zegt, in de ik-vorm, normaal hooguit 18 woorden, makkelijk hooguit 14.
- `emotie`: neutraal, blij, boos, bezorgd, verbaasd, denkend of vastberaden — wat past bij de toon van het citaat.
- Laat de belangrijkste tegenstellingen zien. Geef geen partij meer vakken dan nodig.

## Vorm
```json
{
  "agendapunt": "<id>",
  "verslag_id": "<vergadering.verslag_id uit het agendapunt>",
  "titel": {"normaal": "max 12 woorden", "makkelijk": "max 10 woorden"},
  "samenvatting": {"normaal": "3-5 zinnen", "makkelijk": "3-5 korte zinnen"},
  "sprekers": [{"id": "<spreker.id>", "standpunt": {"normaal": "1-2 zinnen", "makkelijk": "1-2 korte zinnen"}}],
  "kernpunten": {"normaal": ["..."], "makkelijk": ["..."]},
  "woorden": [{"woord": "...", "uitleg": "..."}],
  "strip": [{"spreker_id": "<id of null>", "emotie": "neutraal", "citaat": "...", "tekst": {"normaal": "...", "makkelijk": "..."}}]
}
```
