Je werkt aan **Wat zei de Kamer?** (repository `ljrenkema-dev/watzeidekamer`, branch `claude/fase-1-proef`). De site vat Tweede Kamer-debatten samen en toont ze als anime-strip. Elke spreker heeft een vast figuur, getekend naar zijn of haar officiële portret. Jouw taak in deze chat: **de figuren (avatars) verbeteren**. Aan de debatteksten, citaten en strips zelf verander je niets.

## Wat er al is
- `site/strip.js` — alle tekencode. `portraitCharacter(u, outfit, emo)` tekent een figuur uit kenmerken; `hairBack`, `hairFront`, `beard`, `glasses` en `eyes`/`mouth`/`extras` (emoties) zijn losse functies. SVG in een vak van 100×120.
- `data/uiterlijk.json` — per persoon de kenmerken: `gezicht` (m/v), `haarkleur`, `kapsel`, `bril`, `baard`, `huid`, `leeftijd`, `spiegel` (scheiding links/rechts), `goedgekeurd`. Sleutel = Persoon-id van de Tweede Kamer (of `wiki:<naam>` voor wie daar geen portret heeft, met `foto_url`).
- `data/sprekers.json` — koppelt spreker-id's uit de verslagen aan een sleutel in `uiterlijk.json`. `scripts/koppel.py` vult dit bij en meldt sprekers zonder figuur.
- `scripts/keuring.py UITVOER.html [--alleen "Naam1,Naam2"]` — bouwt een keuringspagina: officieel portret naast het figuur (neutraal, blij, boos), per vijf, met knoppen Goed / Niet goed en een opmerkingenveld. Portretten worden opgehaald naar `data/portret/` (niet in git).
- Bestaande keuringspagina: https://claude.ai/artifact/7DQNkPbYi9GAKFfPb5uoEe (Artifact met capability `db`; oordelen in collectie `keuring`, doc-id = sleutel met `:` → `-`; velden `oordeel` (goed/fout), `opmerking`, `vorige_opmerking`). Publiceer een nieuwe versie naar dezelfde URL en lees oordelen terug met de ArtifactData-tool.
- Huidige stand: **alle 154 figuren zijn goedgekeurd** (149 Kamerleden + 5 bewindspersonen).

## Wat ik wil
1. **Ontbrekende figuren maken** voor: premier Rob Jetten, minister David van Weel, minister Rianne Letschert, staatssecretaris Eelco Eerenberg, staatssecretaris Willemijn Aerdts en Kamerlid Iem Al Biyati (FVD, heeft geen portret bij de Kamer). Zoek een portret op Wikipedia/Wikimedia Commons (`nl.wikipedia.org` en `upload.wikimedia.org` zijn toegestaan; Wikimedia weigert soms verzoeken zonder geschikte user-agent — gebruik dan de thumbnail-URL van de pagina en geef het bestand handmatig door). Zet de bron in `bron` en `foto_url`.
2. **Meer variatie en herkenbaarheid**, zonder karikatuur. Ideeën om uit te werken en mij voor te leggen:
   - gezichtsvorm (smal, rond, hoekig), wenkbrauwdikte, oogkleur waar zichtbaar;
   - meer haartinten (bijv. donkerblond, rossig, peper-en-zout);
   - kleding: colbert, das, blouse, trui — en of we echte partijkleuren gebruiken (nu een automatisch gekozen kleur per partij);
   - fijnere brillen (montuurkleur, randloos), oorbellen als duidelijk kenmerk;
   - leeftijd subtieler tonen.
   Voeg nieuwe opties toe als extra waarden of velden in `uiterlijk.json`, met een veilige standaard, zodat goedgekeurde figuren niet veranderen tenzij dat de bedoeling is.
3. **Laat mij alles keuren** op de keuringspagina: per vijf, met het originele portret ernaast. Zet bij elke figuur die verandert `goedgekeurd` op false tot ik Goed heb gegeven, en zet mijn eerdere opmerking in `vorige_opmerking`. Lees mijn oordelen uit als ik zeg dat ik klaar ben, verwerk "Niet goed" en leg alleen die opnieuw voor.

## Regels
- **Geen karikaturen.** Niets overdrijven (neus, gewicht, tanden, huidskleur). Herkenbaar, vriendelijk anime-poppetje.
- **Portretfoto's komen nooit op de site of in git**, alleen in de privé-keuringspagina. `data/portret/` staat in `.gitignore`.
- Huidskleur beperkt houden tot de bestaande neutrale tinten (`licht`, `middel`, `donker`), alleen aanpassen als ik daarom vraag.
- Test elke wijziging: `python3 scripts/build.py`, en bekijk een strip en de keuringspagina met een schermafbeelding (Playwright staat klaar) voordat je mij iets voorlegt.
- Commit en push alleen naar `claude/fase-1-proef`, nooit naar `main`. Geen pull request tenzij ik erom vraag.
- Schrijf in het Nederlands, kort en concreet.

Begin met het lezen van `site/strip.js` en `data/uiterlijk.json`, maak dan de zes ontbrekende figuren en leg ze aan mij voor. Doe daarna een voorstel voor punt 2 met een paar voorbeelden voordat je alles aanpast.
