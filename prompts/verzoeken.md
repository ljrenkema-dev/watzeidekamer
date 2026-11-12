# Opdracht: verzoeken uit de regeling van werkzaamheden vastleggen

Je krijgt één regeling van werkzaamheden (`data/procedure/<id>.json`, `soort` = "Regeling van werkzaamheden"). Daarin vragen Kamerleden om een debat, een brief of een andere agendawijziging, en reageren andere Kamerleden met steun of geen steun. De voorzitter stelt daarna vast of er een meerderheid is.

Schrijf `data/verzoeken/<id>.json` en draai `python3 scripts/verzoeken_check.py <id>` tot er 0 fouten zijn.

## Regels
- Leg **alleen vast wat in het verslag staat**. Verzin geen steun en geen uitkomst.
- Een verzoek begint bij de spreekbeurt van de verzoeker en loopt tot het volgende verzoek. Neem **elke** Kamerlid-reactie in dat stuk op.
- `oordeel` per reactie:
  - `steun`: steunt het verzoek (ook "van harte steun", "steun voor het debat").
  - `geen_steun`: steunt het niet (ook "geen steun, maar wel een brief": dan `geen_steun` en `brief: true`).
  - `steun_brief`: steunt alleen een brief, niet het debat.
  - `onduidelijk`: zegt het niet duidelijk ("wat mevrouw X zegt", inhoudelijke opmerking zonder oordeel). **Raad niet.**
- `uitkomst` volgens de voorzitter: `meerderheid`, `geen_meerderheid`, `dertigledendebat` (op de lijst van dertigledendebatten gezet), `ingetrokken`, `anders` of `onbekend` (als de voorzitter het niet zegt).
- `citaat` en `uitkomst_citaat` zijn **letterlijk** uit de spreekbeurt van die spreker (minstens 3 woorden; inkorten met " … " mag).
- `onderwerp`: één neutrale zin in normale taal, hooguit 15 woorden, zonder de framing van de verzoeker over te nemen ("Debat over de demonstratie tegen het Israëlbeleid", niet "Debat over het falende kabinet").
- `soort`: `debat`, `dertigledendebat`, `brief`, `stemmingen`, `agenda` (iets toevoegen of verplaatsen), `anders`.
- Een spreekbeurt van de voorzitter zelf die iets aan de agenda toevoegt zonder verzoek van een Kamerlid, hoort niet in de lijst.

## Vorm
```json
{
  "procedure": "<id>",
  "datum": "JJJJ-MM-DD",
  "verzoeken": [
    {
      "verzoeker_id": "<spreker.id>",
      "soort": "debat",
      "onderwerp": "…",
      "bewindspersoon": "minister van … (alleen als genoemd, anders null)",
      "citaat": "…",
      "brief_gevraagd": true,
      "reacties": [{"spreker_id": "<spreker.id>", "oordeel": "steun", "citaat": "Steun."}],
      "uitkomst": "geen_meerderheid",
      "uitkomst_citaat": "U heeft geen meerderheid."
    }
  ]
}
```
