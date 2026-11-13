# Opdracht: botsingskaart (lokbeeld) voor één debat

De kaart is het lokbeeld voor sociale media: een neutrale vraag en twee letterlijke citaten tegenover elkaar, die laten zien waar het in het debat om draaide. Wie nieuwsgierig wordt, leest verder op de site (alle standpunten, het hele debat). Accuraat en aansprekend; juistheid gaat altijd voor.

Je krijgt `data/compact/kaart_<id>.txt`: het debat, de partijen, de afloop uit de motiedata en de drie langste wisselingen (twee sprekers die over en weer op elkaar reageren) met volledige tekst. Lees alleen dat bestand en `prompts/lessen.md` (L1–L6 gelden ook hier).

## Wat je kiest
1. **De wisseling.** Neem de langste, tenzij die geen echte tegenstelling heeft (twee sprekers die het eens zijn, of alleen procedure); kies dan de volgende. Is geen enkele wisseling een echte botsing, forceer er dan geen: geef één versie met één citaat en zet `"geen_botsing": true`.
   **Bijzaak = een onderwerp met minder dan 10% van de spreektijd van het debat** (woorden zonder de voorzitter; de bron geeft per beurt het aantal woorden en de grens). Meet het met `python3 scripts/kaart.py aandeel <id> "<trefwoorden als regex>"` (telt de zinnen die het onderwerp noemen, in het hele debat) en zet de uitkomst met de gebruikte trefwoorden in `aandeel_onderwerp`, bijvoorbeeld `"19% (Israël|Gaza|Palestijn|genocide)"`. Kies trefwoorden die het onderwerp dekken, niet te ruim ("gas" telt ook gasprijzen) en niet te smal. Is het onderwerp een bijzaak (bijvoorbeeld één vraag over lng in een debat dat vooral over Israël en Oekraïne ging), kijk dan welk onderwerp de meeste spreektijd en de duidelijkste tegenstelling had, en zet twee sprekers van verschillende kanten over dát onderwerp tegenover elkaar, ook als ze niet direct op elkaar reageerden. Zeg dat in `regel`.
   Bij een vragenuur geldt de bijzaakregel niet (elke vraag is een eigen onderwerp): het onderwerp van de eerste vraag, tenzij `python3 scripts/reeks.py --voor <datum>` die fractie op de grens zet.
2. **De vraag**: één neutrale zin, als echte vraag ("Moet …?", "Is …?", "Stemmen …?"), nooit sturend ("Waarom faalt …?"). Hij steunt op het onderwerp dat de voorzitter, het Kamerstuk of de vraagsteller zelf noemt. Schrijf in `vraag_bron` op welke zin uit de bron hij steunt.
3. **Twee citaten**, één per spreker, uit die wisseling. **Wie het eerst sprak, staat bovenaan** (vaste regel, ook als dat telkens de vraagsteller is; zo kiest niemand wie het laatste woord krijgt). Het script controleert dit. Per citaat hooguit **twee zinnen en ongeveer 35 woorden** (anders past de kaart niet), de zinnen die de vraag en het antwoord dragen (geen aanhef, geen beleefdheden). Letterlijk; stukken van minstens 5 woorden mag je verbinden met " … ", zolang de betekenis niet verandert. Samen moeten ze zonder voorkennis te begrijpen zijn.
4. **Versie c** (optioneel, alleen als het iets toevoegt): een tweede paar citaten uit een andere ronde of wisseling, zodat de eigenaar ziet wat een andere keuze doet.

## Uitvoer
Schrijf `data/proeftuin/botsing/<id>.json`:
```json
{"debat": "<id>", "kop": "<soort debat> · <d mmm jjjj>[ · <deel of vraag x van y>]",
 "vraag": "...?", "vraag_bron": "...",
 "versies": {"a": {"regel": "welke wisseling en waarom", "wisseling": "A (partij) ↔ B (partij), beurt x–y, n beurten",
                   "afgevallen": ["..."], "aandeel_onderwerp": "ca. 35% (beurten 4, 7, 11–14)", "citaten": [{"beurt": 12, "citaat": "..."}, {"beurt": 13, "citaat": "..."}]},
             "c": {...}}}
```
Naam, partij, video, figuur en de afloop vult het script aan; de afloop wordt bij elke run opnieuw uit de stemdata berekend, dus schrijf er zelf niets over. Draai `python3 scripts/kaart.py check <id>` en herstel tot OK. Eindig met twee zinnen: welke wisseling en vraag je koos en waarom.
