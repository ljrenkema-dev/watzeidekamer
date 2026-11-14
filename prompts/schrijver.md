# Opdracht: debatpagina en kaart voor één agendapunt (één schrijver)

Je maakt voor één agendapunt zowel de debatpagina als de botsingskaart. Eén schrijver doet beide, omdat je het hele debat dan maar één keer leest en de kaart kiest met kennis van het hele debat (besluit eigenaar, 14 nov 2026, na een proef op twee debatten).

1. Lees `prompts/pagina.md`, `prompts/kaart.md` en `prompts/lessen.md` helemaal. Punt 4 "Kort gezegd" in `kaart.md` staat tijdelijk uit: schrijf geen `kort` en geen `vraag_makkelijk`.
2. Bepaal met `python3 scripts/zwaarte.py <id>` of het agendapunt **volledig** of **licht** is. Bij **licht** maak je alleen de pagina, geen kaart.
3. Lees het debat in `data/agendapunten/<id>.json`, en `data/moties/<id>.json` en `data/reeks/` als die er zijn.
4. Schrijf de pagina volgens `pagina.md` naar `data/paginas/<id>.json` en draai `python3 scripts/check_pagina.py <id>` tot OK.
5. Bij **volledig**: draai `python3 scripts/kaart.py voor <id>` en gebruik `data/compact/kaart_<id>.txt` voor de wisselingen en woordtellingen. Voor de bron van de vraag mag je `data/verzoeken/` en `data/procedure/` lezen. Schrijf de kaart volgens `kaart.md` naar `data/proeftuin/botsing/<id>.json` en draai `python3 scripts/kaart.py check <id>` tot OK. Gebruik wat je over het hele debat weet bij de keuze van de wisseling, maar volg de regels van `kaart.md` (langste echte botsing, bijzaak onder 10%, wie het eerst sprak bovenaan, bronvolgorde voor de vraag, inkortregel).
6. Pagina en kaart mogen elkaar niet tegenspreken.

Wijzig geen scripts en commit niets. Eindig met een korte samenvatting: titel, aantal standpunten en kernpunten, en bij een kaart de gekozen wisseling, de vraag en de bron.
