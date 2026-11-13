# Opdracht: agendapunt samenvatten in twee taalniveaus en een strip maken

Je krijgt één agendapunt uit een debat van de Tweede Kamer (`data/agendapunten/<id>.json`).
Lees eerst **`prompts/lessen.md`**: fouten die eerder gemaakt zijn en die je niet opnieuw maakt. Controleer je tekst daar aan het eind zelf op.

Schrijf `data/strips/<id>.json`. Draai daarna `python3 scripts/check.py <id>` en los elke fout op tot de check slaagt.

## Twee taalniveaus
Elke tekst schrijf je twee keer, onder `normaal` en `makkelijk`. Beide versies zeggen inhoudelijk hetzelfde.
- **normaal** (standaard op de site): heldere, gewone taal zoals een goede nieuwssite. Zinnen tot ongeveer 20 woorden. Houd getallen, nuances en wie-wat-vindt precies. Geen jargon zonder uitleg.
- **makkelijk**: korte zinnen van hooguit 12 woorden, alledaagse woorden, actieve vorm. Voor laaggeletterden en mensen die Nederlands leren.

## Een deel van een lang debat
Heeft het agendapunt een veld `deel`, dan is het één deel van een lang debat (`deel.nummer` van `deel.van`, fase `deel.fase`, zoals "Inbreng van de Kamer" of "Antwoord van het kabinet").
- Vat alleen samen wat in dít deel gezegd is. Verwijs niet naar wat in andere delen staat.
- Zeg in de samenvatting om welk deel het gaat, met de fase en de sprekers maar **zonder volgnummer** (de nummering kan veranderen als er later delen bijkomen; de site toont het nummer zelf): bijvoorbeeld "In dit deel van het debat over het Belastingplan geven Brekelmans (VVD) en Eerdmans (JA21) hun inbreng." Niet: "In dit tweede deel …".
- De titel gaat over de kern van dit deel, niet over het hele debat.
- "Standpunten per partij" (`sprekers`) bevat de fracties die in dit deel spraken. Een antwoord van het kabinet staat in een ander deel als het hier niet voorkomt; schrijf dan niet dat het ontbreekt.
- Bij een antwoord van het kabinet: noem aan wie de bewindspersoon antwoordt.

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
De strip is het hart van de pagina: hij staat direct onder de samenvatting, en daaronder de standpunten van álle partijen (uit `sprekers`). De strip hoeft dus niet elke partij te tonen, wel de kern van het debat.
- 4 tot 8 vakken, in de volgorde van het debat.
- `tekst`: wat de spreker in dat vak zegt, in de ik-vorm, normaal hooguit 18 woorden, makkelijk hooguit 14.
- `emotie`: neutraal, blij, boos, bezorgd, verbaasd, denkend of vastberaden — wat past bij de toon van het citaat. Het gezicht van het figuur blijft neutraal; de emotie bepaalt de achtergrond van het vak.

### Kies vakken die op zichzelf staan en de moeite waard zijn
Een lezer die alleen de ballonnen leest, moet snappen waar het over gaat en waarom het ertoe doet.
- **Elke ballon is zonder context te begrijpen.** Zeg waaróver het gaat, niet alleen wat de spreker procedureel doet.
  - Fout: "Ik dien een motie in." / "Ik heb nog een vraag aan de minister." / "Daar ben ik het mee eens."
  - Goed: "Ik vraag de regering om de rente-aftrek voor tweede huizen te schrappen." (als het citaat dat zegt)
- **Kies citaten die iets laten zien**: een scherpe vraag, een concreet voorbeeld uit het dagelijks leven, een getal dat blijft hangen, een beeldspraak van de spreker zelf, een verwijzing naar iets wat mensen kennen (een bekend nieuwsonderwerp, sociale media, een merk, een plaats, een persoonlijke ervaring).
- **Laat de botsing zien**: zet een bewering en het tegenargument of antwoord achter elkaar, zodat de lezer beide kanten in hun eigen woorden ziet. Een vraag in vak 3 en het antwoord in vak 4 is sterker dan twee losse vragen.
- **Vermijd** procedure (stemmingsvolgorde, spreektijd, "via de voorzitter"), beleefdheden en vakken waarin twee sprekers hetzelfde zeggen.
- **Aansprekend is geen sensatie.** Het moet waar en eerlijk blijven:
  - De ballon blijft zo dicht mogelijk bij de woorden van de spreker; maak niets scherper, grappiger of bozer dan het citaat (zie L3, L11).
  - Kies niet het opvallendste citaat van de ene kant en het saaiste van de andere: geef elke kant van de hoofdtegenstelling haar sterkste, duidelijkste moment.
  - Een pakkende verwijzing (sociale media, een bekend persoon) gebruik je alleen als de spreker die zelf maakt.
- Het eerste vak (Verteller of eerste spreker) maakt meteen duidelijk wat er op het spel staat; het laatste vak sluit af met een uitkomst, een antwoord of de open vraag.

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
