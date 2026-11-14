# Opdracht: agendapunt samenvatten en een strip maken

Je krijgt één agendapunt uit een debat van de Tweede Kamer (`data/agendapunten/<id>.json`).
Lees eerst **`prompts/lessen.md`**: fouten die eerder gemaakt zijn en die je niet opnieuw maakt. Controleer je tekst daar aan het eind zelf op.

Schrijf `data/strips/<id>.json`. Draai daarna `python3 scripts/check.py <id>` en los elke fout op tot de check slaagt.

## Taal
Schrijf in heldere, gewone taal zoals een goede nieuwssite. Zinnen tot ongeveer 20 woorden. Houd getallen, nuances en wie-wat-vindt precies. Geen jargon zonder uitleg.
**Makkelijke taal staat tijdelijk uit** (besluit eigenaar, 14 nov 2026). Schrijf elke tekst één keer, onder `normaal`, en zet onder `makkelijk` precies dezelfde tekst (de site toont alleen `normaal`; `scripts/check.py` verwacht beide velden). Houd daarom de vaktekst in de strip op hooguit 14 woorden.

## Een deel van een lang debat
Heeft het agendapunt een veld `deel`, dan is het één deel van een lang debat (`deel.nummer` van `deel.van`, fase `deel.fase`, zoals "Inbreng van de Kamer" of "Antwoord van het kabinet").
- Vat alleen samen wat in dít deel gezegd is. Verwijs niet naar wat in andere delen staat.
- Zeg in de samenvatting om welk deel het gaat, met de fase en de sprekers maar **zonder volgnummer** (de nummering kan veranderen als er later delen bijkomen; de site toont het nummer zelf): bijvoorbeeld "In dit deel van het debat over het Belastingplan geven Brekelmans (VVD) en Eerdmans (JA21) hun inbreng." Niet: "In dit tweede deel …".
- De titel gaat over de kern van dit deel, niet over het hele debat.
- "Standpunten per partij" (`sprekers`) bevat de fracties die in dit deel spraken. Een antwoord van het kabinet staat in een ander deel als het hier niet voorkomt; schrijf dan niet dat het ontbreekt.
- Bij een antwoord van het kabinet: noem aan wie de bewindspersoon antwoordt.

## Debat met losse onderwerpen of een lijst (vragenuur e.d.)
Bij een vragenuur, mondelinge vragen of een debat waarin achter elkaar losse onderwerpen of een duidelijke lijst met punten langskomen (**altijd** bij een vragenuur; ook bij een tweeminutendebat waarin moties worden ingediend, een debat dat de agendapunten van een Raad of overleg afloopt, stemmingen en een regeling van werkzaamheden):
- **Tweeminutendebat met moties**: één inleidende zin (wie diende hoeveel moties in), dan per motie een regel die begint met "- ": nummer, indiener(s), wat de motie vraagt (uit de verzoekt-zin in `data/moties/`) en het oordeel van het kabinet. Een kernpunt dat alleen een motie herhaalt, hoeft niet. Een `onderwerpen`-indeling is hier niet nodig.
- **Titel** begint met het soort debat en een dubbele punt: "Vragenuur: …". De rest noemt de onderwerpen of het belangrijkste onderwerp.
- **Samenvatting**: één inleidende zin, dan per onderwerp een regel die begint met "- " (de site maakt er een opsomming van). 
- **`onderwerpen`**: per onderwerp, in de volgorde van het debat, `{"titel": {"normaal": "...", "makkelijk": "..."}, "sprekers": [ids van wie over dit onderwerp sprak], "kernpunten": [nummers van de kernpunten over dit onderwerp, vanaf 0]}`. De site zet de standpunten en de kernpunten dan per onderwerp onder een subkop. Zet de kernpunten in `kernpunten` op volgorde van onderwerp; normaal en makkelijk hebben evenveel kernpunten in dezelfde volgorde. Spreekt iemand over twee onderwerpen, zet hem bij het onderwerp waar hij het meest over zei en noem het andere in zijn standpunt.
- **Strip**: kies één onderwerp en belicht het van beide kanten: de vraag, het antwoord van de bewindspersoon en de vervolgvragen of tegenwerpingen van andere partijen. Zet in `strip_onderwerp` het nummer van dat onderwerp (vanaf 0). Kies het onderwerp met de duidelijkste botsing of het meeste belang voor gewone mensen.
- **Spreiding over de reeks**: draai vóór je keuze `python3 scripts/reeks.py --voor <datum van het debat>`. Staat de fractie die de vraag stelde op of boven de grens (een fractie is in de laatste 10 vragenuren hooguit max(2, afgerond 2 × haar zetelaandeel × 10) keer de vraagsteller van het onderwerp in de strip), kies dan een ander onderwerp, tenzij dat geen echte botsing heeft. Schrijf in `keuze_onderwerp` (normaal en makkelijk, één zin) waarom je dit onderwerp koos, zonder oordeel over partijen; de site toont die zin onder de strip. Voorbeeld: "De strip gaat over het loon van uitzendkrachten: hier botsten vraag en antwoord het duidelijkst." De andere onderwerpen staan in de samenvatting, de kernpunten en de standpunten. Het eerste vak (Verteller) zegt dat de strip over dit ene onderwerp gaat; het mag een letterlijk stuk uit de vraag of de inleiding zijn.

## Moties
Staat er een bestand `data/moties/<id>.json` (of een blok MOTIES onderaan de compacte bron), dan weet je per motie de indieners, de volledige tekst, het oordeel van het kabinet en eventueel de uitslag.
- Gebruik dat in de samenvatting, de kernpunten, de standpunten en `woorden`: zeg wat een motie vraagt en van wie ze is ("De Roon (PVV) vraagt in een motie de ontwikkelingshulp aan de Sahel te stoppen; de minister ontraadt die").
- Citaten in de strip komen alleen uit de spreekbeurten, niet uit de motietekst. Wil je een motie in een vak, kies dan het moment in het debat waarop de indiener haar toelicht of de bewindspersoon er een oordeel over geeft, en zeg in de ballon waar de motie over gaat als het citaat dat toelaat.
- Een uitslag noem je alleen als die in het bestand staat. De site toont de moties en uitslagen zelf ook in een eigen blok.

## Juistheid (belangrijkst)
- Gebruik ALLEEN wat in de spreekbeurten staat. Verzin niets. Geen eigen mening. Neutraal naar alle partijen.
- Getallen, data en standpunten precies zoals in de tekst.
- `citaat` is LETTERLIJK overgenomen uit de tekst van de spreekbeurt(en) van die spreker. Je mag inkorten door stukken te verbinden met " … ". Elk stuk moet minstens 5 woorden zijn en letterlijk in de tekst staan (leestekens en hoofdletters precies zo).
- De `tekst` in een stripvak zegt niets wat niet in het citaat van dat vak staat.
- `spreker_id` is de `spreker.id` uit het agendapunt. Gebruik `null` voor de Verteller (inleiding of afsluiting); het citaat van de Verteller mag uit elke spreekbeurt komen.
- Neem in `sprekers` iedere fractie op die in dit agendapunt sprak (voorzitter niet meegerekend). Kies per fractie de hoofdspreker.
- Bewindspersonen (minister, staatssecretaris) tellen als spreker zonder fractie.
- `woorden` legt vaktermen uit. Gebruik zo veel mogelijk de uitleg uit het debat zelf; algemene kennis alleen als die vaststaat en neutraal is.

## Strip
**Waar de strip voor is.** De strip is het uithangbord van de site: hij moet de interesse wekken van een breed publiek, mensen die niet elke dag politiek volgen. Wie de strip leest, moet denken "hé, hier wil ik meer van weten" en dan verder lezen in de samenvatting, de standpunten en het hele debat. Daarom is de strip **accuraat én aansprekend**: elke ballon klopt met het citaat, en samen vertellen de vakken een verhaal met een spanning, een botsing of een verrassing. Twijfel je tussen een correct maar saai vak en een correct en pakkend vak, kies dan het pakkende. Twijfel je tussen pakkend en correct, kies altijd correct.

De strip is het hart van de pagina: hij staat direct onder de samenvatting, en daaronder de standpunten van álle partijen (uit `sprekers`). De strip hoeft dus niet elke partij te tonen, wel de kern van het debat.
- 4 tot 8 vakken, in de volgorde van het debat.
- `tekst`: wat de spreker in dat vak zegt, in de ik-vorm, hooguit 14 woorden (dezelfde tekst onder `normaal` en `makkelijk`).
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
  "samenvatting": {"normaal": "3-5 zinnen (of inleiding + regels met '- ')", "makkelijk": "3-5 korte zinnen"},
  "sprekers": [{"id": "<spreker.id>", "standpunt": {"normaal": "1-2 zinnen", "makkelijk": "1-2 korte zinnen"}}],
  "kernpunten": {"normaal": ["..."], "makkelijk": ["..."]},
  "onderwerpen": [{"titel": {"normaal": "...", "makkelijk": "..."}, "sprekers": ["<id>"], "kernpunten": [0, 1]}],
  "strip_onderwerp": 0,
  "keuze_onderwerp": {"normaal": "...", "makkelijk": "..."},
  "woorden": [{"woord": "...", "uitleg": "..."}],
  "strip": [{"spreker_id": "<id of null>", "emotie": "neutraal", "citaat": "...", "tekst": {"normaal": "...", "makkelijk": "..."}}]
}
```
