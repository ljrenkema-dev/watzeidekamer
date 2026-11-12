# Opdracht: manga-figuren per politicus (pilot)

Doel: per politicus één vaste set manga-figuren, één per emotie, die de strip daarna gebruikt in plaats van de SVG-tekeningen. De figuren worden **één keer** gemaakt, door de eigenaar gekeurd, en daarna nooit 's nachts opnieuw gegenereerd.

## Regels (niet onderhandelbaar)
- **Geen portretfoto naar de beeldgenerator.** De beschrijving komt alleen uit de goedgekeurde kenmerken in `data/uiterlijk.json` (haar, bril, baard, huid, leeftijd, kleding). Het resultaat is een getekend figuur dat dezelfde kenmerken heeft, geen nagemaakte foto.
- **Geen karikatuur.** Niets overdrijven: geen grote neus, geen dik/dun maken, geen tanden, geen huidskleur aanzetten. Vriendelijk en neutraal getekend; emoties ingetogen.
- **Geen tekst in het beeld.** Geen letters, namen, logo's, partijsymbolen of vlaggen. Tekstballonnen voegt de site zelf toe.
- **Zelfde opbouw bij elk figuur**: borstbeeld, recht van voren, iets naar rechts gedraaid, effen witte achtergrond, figuur gecentreerd en vult ongeveer 70% van de hoogte. Zo passen ze in elk stripvak.
- **Partijkleur** alleen als klein accent: de stropdas, sjaal of een speld. De rest is zwart-wit.
- Het eerste beeld (neutraal) is de referentie; elke andere emotie wordt gemaakt met dat beeld als voorbeeld, zodat het hetzelfde figuur blijft.

## Stijl (vast, voor elk beeld gelijk)
Black-and-white manga illustration, clean confident ink lines, classic seinen style, screentone shading, subtle hatching, no colour except a single small accent colour on the tie or scarf. Expressive but restrained eyes. Bust portrait, facing the viewer, turned slightly to the right, plain white background, centred, the figure fills about 70% of the image height. Editorial newspaper-comic feel, respectful, not a caricature. No text, no letters, no logos, no flags, no symbols.

## Beschrijving (uit de kenmerken)
`scripts/manga.py` maakt per persoon een Engelse beschrijving uit `data/uiterlijk.json`, bijvoorbeeld:
"A fictional Dutch politician in their fifties, a man, short platinum-blond hair combed back in a quiff, no glasses, clean-shaven, light skin, wearing a dark suit with a <accent> tie."

## Emoties
neutraal → calm, attentive, closed mouth
blij → warm smile
boos → frowning, firm mouth, not shouting
bezorgd → slightly raised inner eyebrows, concerned look
verbaasd → raised eyebrows, mouth slightly open
denkend → looking slightly up and aside, hand near chin
vastberaden → determined look, set jaw

## Keuring
De beelden komen in `data/manga/<sleutel>/<emotie>.png` en worden gekeurd op een keuringspagina met het officiële portret ernaast (alleen op die privépagina). Pas na goedkeuring gebruikt de strip ze.
