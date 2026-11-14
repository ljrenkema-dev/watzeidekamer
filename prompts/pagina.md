# Opdracht: debatpagina schrijven voor één agendapunt

Je krijgt één agendapunt uit een debat van de Tweede Kamer (`data/agendapunten/<id>.json`). Je schrijft de tekst van de debatpagina: titel, samenvatting, standpunten van alle partijen, kernpunten en moeilijke woorden. Bovenaan de pagina staat een botsingskaart; die wordt apart gemaakt (`prompts/kaart.md`) en hoort niet bij deze opdracht.
Lees eerst **`prompts/lessen.md`**: fouten die eerder gemaakt zijn en die je niet opnieuw maakt. Controleer je tekst daar aan het eind zelf op.

Schrijf `data/paginas/<id>.json`. Draai daarna `python3 scripts/check_pagina.py <id>` en los elke fout op tot de check slaagt.

## Taal
Heldere, gewone taal zoals een goede nieuwssite. Zinnen tot ongeveer 20 woorden. Houd getallen, nuances en wie-wat-vindt precies. Geen jargon zonder uitleg. Elke tekst schrijf je één keer (makkelijke taal staat uit).

## Juistheid (belangrijkst)
- Gebruik ALLEEN wat in de spreekbeurten staat (en, voor moties, in `data/moties/<id>.json`). Verzin niets. Geen eigen mening. Neutraal naar alle partijen.
- Getallen, data en standpunten precies zoals in de tekst.
- Wat één spreker beweert, schrijf je als bewering van die spreker ("volgens X", "X zegt"), niet als feit.
- Een voorbehoud, ontkenning of voorwaarde van een spreker valt nooit weg.
- Neem in `sprekers` **iedere fractie op die in dit agendapunt sprak** (voorzitter niet meegerekend), met per fractie de hoofdspreker en een standpunt van 1 à 2 zinnen. Bewindspersonen (minister, staatssecretaris) tellen als spreker zonder fractie. Het script controleert dat geen fractie ontbreekt.
- `woorden` legt vaktermen uit die in de tekst staan. Gebruik zo veel mogelijk de uitleg uit het debat zelf; algemene kennis alleen als die vaststaat en neutraal is.

## Een deel van een lang debat
Heeft het agendapunt een veld `deel`, dan is het één deel van een lang debat (`deel.nummer` van `deel.van`, fase `deel.fase`).
- Vat alleen samen wat in dít deel gezegd is. Verwijs niet naar wat in andere delen staat.
- Zeg in de samenvatting om welk deel het gaat, met de fase en de sprekers maar **zonder volgnummer**: "In dit deel van het debat over het Belastingplan geven Brekelmans (VVD) en Eerdmans (JA21) hun inbreng."
- De titel gaat over de kern van dit deel, niet over het hele debat.
- `sprekers` bevat de fracties die in dít deel spraken. Een antwoord van het kabinet dat in een ander deel staat, noem je niet als ontbrekend.
- Bij een antwoord van het kabinet: noem aan wie de bewindspersoon antwoordt.

## Debat met losse onderwerpen of een lijst
**Altijd** bij een vragenuur; ook bij mondelinge vragen, een debat dat de agendapunten van een Raad of overleg afloopt, een tweeminutendebat met moties, stemmingen en een regeling van werkzaamheden:
- **Titel** begint met het soort debat en een dubbele punt: "Vragenuur: …".
- **Samenvatting**: één inleidende zin, dan per onderwerp een regel die begint met "- " (de site maakt er een opsomming van).
- **Tweeminutendebat met moties**: één inleidende zin (wie diende hoeveel moties in), dan per motie een regel "- ": nummer, indiener(s), wat de motie vraagt (uit de verzoekt-zin) en het oordeel van het kabinet. Geen `onderwerpen` nodig.
- **`onderwerpen`** (vragenuur en andere losse onderwerpen): per onderwerp, in de volgorde van het debat, `{"titel": "...", "sprekers": [ids], "kernpunten": [nummers vanaf 0]}`. De site zet standpunten en kernpunten per onderwerp onder een subkop. Zet de kernpunten op volgorde van onderwerp. Spreekt iemand over twee onderwerpen, zet hem bij het onderwerp waar hij het meest over zei.

## Moties
Staat er `data/moties/<id>.json`, gebruik dan de indieners, de tekst en het oordeel van het kabinet in samenvatting, kernpunten en standpunten ("De Roon (PVV) vraagt in een motie de ontwikkelingshulp aan de Sahel te stoppen; de minister ontraadt die"). Een uitslag noem je alleen als die in het bestand staat; de site toont moties en uitslagen ook zelf.

## Wat de pagina moet doen
De kaart bovenaan wekt de interesse; deze tekst laat daarna het hele debat zien. Een lezer moet na de samenvatting weten waar het over ging, wie wat wilde en wat er nu gebeurt. Kies in de kernpunten wat iemand die het debat niet zag moet weten, niet wat procedureel gebeurde.

## Vorm
```json
{
  "agendapunt": "<id>",
  "verslag_id": "<vergadering.verslag_id uit het agendapunt>",
  "titel": "hooguit 12 woorden",
  "samenvatting": "3-5 zinnen (of inleiding + regels met '- ')",
  "sprekers": [{"id": "<spreker.id>", "standpunt": "1-2 zinnen"}],
  "kernpunten": ["..."],
  "onderwerpen": [{"titel": "...", "sprekers": ["<id>"], "kernpunten": [0, 1]}],
  "woorden": [{"woord": "...", "uitleg": "..."}]
}
```
`onderwerpen` laat je weg als het debat niet uit losse onderwerpen bestaat.
