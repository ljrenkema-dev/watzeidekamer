# Logboek nieuwe site (branch `claude/nieuwe-site`)

## Opzet
- Alles staat in `nieuw/`. `kern/` is gedeeld (datamodel, HTML-stukken, figuren, deelbeelden, controle-hulp); `a.py`, `b.py`, `c.py` bouwen elk een variant naar `uit/a`, `uit/b`, `uit/c`. `bouw.py` bouwt alle drie, `controle.py` controleert ze, `kijk.js` maakt schermafdrukken (1280/390, licht/donker).
- Bouwen kost geen AI: de scripts lezen `data/` (alleen lezen) en `nieuw/eigen/`. Een nieuw debat in de data komt vanzelf mee.
- Afhankelijkheden: Python 3, Node (voor de getekende figuren uit `site/strip.js`) en Playwright/Chromium (alleen voor de deelbeelden; ontbreekt die, dan blijven de oude deelbeelden staan en valt een nieuw debat terug op `og/site.png`).

## Besluiten (met reden)
- **Moties per debat**: `data/moties/<id>.json` noemt ook moties die alleen *genoemd* werden (een minister die een nummer noemt; stemverklaringen). Daardoor stonden politiemoties bij het Belastingplan en bij digitalisering. Vaste regel: een motie hoort bij het debat waarin haar eerste indiener sprak. Dat haalt precies de verkeerd gekoppelde moties weg (gecontroleerd op alle 110 moties). Bij Stemmingen tonen we de genoemde moties met een link naar hun debat.
- **Kaart bij een debat in delen**: het eerste deel met een kaart met twee citaten zonder `geen_botsing`; anders het eerste deel met een kaart.
- **Kernpunten** uit de paginadata worden niet getoond: ze herhalen de samenvatting en de standpunten (regel: geen dubbele informatie).
- **Verzoeken** (`data/verzoeken/`) staan niet op de site: CLAUDE.md zegt "niet op de site; voor analyses".
- **Figuren zonder manga-beeld** (4 personen) worden met `makeLook/character` uit `site/strip.js` als vaste SVG getekend, maar met één neutrale kledingkleur voor iedereen in plaats van de partijkleur (geen partijkleur als vlak). De 3 sprekers zonder goedgekeurd figuur krijgen een neutraal silhouet. Manga-beelden worden ongewijzigd gekopieerd.
- **Tekst over de figuren** wordt uit `data/uiterlijk.json` geteld: 84 naar een Kamerportret, 7 naar een andere foto, 3 zonder figuur.
- **Tekst van een motie** (het letterlijke verzoek) staat in een documentvorm (grijs vlak, vaste letterbreedte) met het label "Letterlijke tekst van het verzoek", niet in de citaatvorm: de citaatvorm is voor gesproken woorden van een spreker met figuur. Ook de verslagpagina (alles letterlijk, zo aangekondigd) gebruikt de citaatvorm niet; daar zijn de geciteerde stukken gemarkeerd.
- **Datum van een stemming** staat niet in de data; daarom staat nergens wanneer gestemd is. Moties zonder uitslag krijgen geen "nog niet gestemd" maar "geen uitslag in onze gegevens".
- **Wetsvoorstel**: vaste regel op de agendatitel (begroting, belastingplan, novelle, wet) voor de zin dat er apart over wet en amendementen gestemd wordt en dat de Eerste Kamer daarna stemt.
- **Afzender**: geen naam of adres verzonnen. `nieuw/eigen/afzender.json` is de invulplek; zolang die leeg is, toont de site een rood gestreepte plek "[naam van de maker: nog invullen]" en "[e-mailadres of formulier om een fout te melden: nog invullen]".
- **Fractie "Keijzer"** in de stemuitslagen = "Lid Keijzer" in `data/fracties.json` (`nieuw/eigen/aliassen.json`).
- **Coalitie** D66, CDA, VVD: `nieuw/eigen/coalitie.json` (handmatig, stand 14 november 2026).
- **Makkelijke taal**: `MAKKELIJK = False` in `kern/model.py`; teksten worden nu alleen in normale taal getoond.

## Velden die een variant beter zouden maken (niet gebouwd; site werkt zonder)
- (wordt aangevuld)

## Rondes
### Ronde 1
- A gebouwd; eigen kijkronde op 1280/390 licht/donker: ballonnen te smal (blockquote-marge), staartje scheef, logo onleesbaar in donker, afloopblok met lege rechterkolom, lange uitleglijst op telefoon. Hersteld (uitleg inklapbaar, afloop in de leeskolom).
- **Stemmingen-agendapunten**: de moties die `data/moties/` aan een stemmingen-agendapunt koppelt, zijn op nummer gezocht en daardoor soms fout (10 november: "motie op stuk nr. 40 van de heer Jimmy Dijk" werd motie 40 van Bikker uit het politiedossier). Daarom toont de site bij Stemmingen geen moties, alleen de sprekers, het verslag en de uitleg dat de uitslag bij het debat van de motie staat. Een veld `stemmingen` (welke moties in welke stemmingsronde, met datum) zou dit oplossen; dat staat in de open data (Besluit/Stemming per Zaak) en kost geen AI, alleen een uitbreiding van `scripts/moties.py`.
