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
- **Uitslag van wetsvoorstel en amendementen** (Besluit/Stemming per Zaak in de open data). Geen AI nodig, alleen een uitbreiding van `scripts/moties.py`. Dan kan "Hoe liep het af" zeggen of het Belastingplan is aangenomen. Nu staat er een vaste zin dat die uitslag niet in onze gegevens staat. Kosten per debat: nul (script).
- **`stemmingen`**: welke moties in welke stemmingsronde, met datum (zie hieronder). Kosten per debat: nul (script).
- **Gewone titel per motie** (bijvoorbeeld "Hypotheekrenteaftrek terugdraaien"), gevraagd door de lezer met leesmoeite. Vraagt per motie één korte AI-zin plus nalezing: ongeveer 5–30 moties per debat, een paar cent per debat. Niet gebouwd; nu staat de omschrijving uit de Kamerdata er.
- **Gewone naam per onderwerp** (variant B), bijvoorbeeld "Belasting op spaargeld en beleggingen" in plaats van "Novelle uitbreiding vermogenswinstbelasting box 3". Eén korte zin per nieuw onderwerp; zelden nodig.
- **Eén zin "waar ging het over"** voor debatten zonder samenvatting (commissiedebatten in de proefperiode). Dat is gewoon de paginatekst die de nachtelijke run in de proefperiode niet maakt.
- **Coalitie per periode en zetels per datum**: `nieuw/eigen/coalitie.json` heeft nu één stand; bij een kabinetswissel moet een periode (van–tot) erbij, zodat oude debatten de coalitie van toen krijgen. `data/fracties.json` heeft al datums; de site gebruikt nu de nieuwste.

## Rondes
### Ronde 1
- A gebouwd; eigen kijkronde op 1280/390 licht/donker: ballonnen te smal (blockquote-marge), staartje scheef, logo onleesbaar in donker, afloopblok met lege rechterkolom, lange uitleglijst op telefoon. Hersteld (uitleg inklapbaar, afloop in de leeskolom).
- **Stemmingen-agendapunten**: de moties die `data/moties/` aan een stemmingen-agendapunt koppelt, zijn op nummer gezocht en daardoor soms fout (10 november: "motie op stuk nr. 40 van de heer Jimmy Dijk" werd motie 40 van Bikker uit het politiedossier). Daarom toont de site bij Stemmingen geen moties, alleen de sprekers, het verslag en de uitleg dat de uitslag bij het debat van de motie staat. Een veld `stemmingen` (welke moties in welke stemmingsronde, met datum) zou dit oplossen; dat staat in de open data (Besluit/Stemming per Zaak) en kost geen AI, alleen een uitbreiding van `scripts/moties.py`.

### Ronde 1: beoordeling (lezer met leesmoeite, interface-expert, politicoloog, controleur)
Controleur: geen ernstige fouten; alle citaten, uitslagen, zetels, videolinks en ankers kloppen. Wel: nalees-datum fout (er bestaat `data/redactie/pagina_<id>.json` voor `data/paginas`), RSS-tijden een uur verkeerd, "van Baarle" zonder hoofdletter, "Keijzer (Keijzer)", "(nog) geen samenvatting", RSS-beschrijving noemde moties die er niet zijn. Alles hersteld.

Overgenomen (alle varianten):
- Minderheidskabinet: de uitleg over coalitie wordt nu berekend (D66, CDA en VVD hebben samen 66 zetels) en zegt dat dit een minderheidskabinet is en dat oppositiefracties vaak meestemmen.
- "Hoe liep het af" zet bij een wetsvoorstel eerst wat er met de wet gebeurt (uitslag niet in onze gegevens, daarna de Eerste Kamer), dan de moties als "verzoeken aan de regering". Lang debat zonder tweede termijn in de data: vaste zin dat die ontbreekt.
- Geen kaart uit een ordedebat (Belastingplan 10 november had alleen een ordedebatkaart; dat debat toont nu titel en sprekers). De regeltekst op "Zo werken we" beschrijft nu wat echt geldt (ook de oudere kaarten bij tweeminutendebatten).
- Onder elke kaart: "Aan het woord in dit debat: SP (3), VVD (22), …" met link naar alle standpunten (tegen het arena-beeld en de eenmansfractie die even zwaar oogt).
- Fracties bij een uitslag in één lijst per kant op zetels, coalitie als label in plaats van twee blokken. "33 zetels voor" in plaats van "33 voor".
- Motieteksten: "óf en hoe" uitvoeren; stemuitleg zegt dat een Kamerlid kan afwijken; geen algemene bewering meer over "de meeste moties", maar het berekende getal. Pdf-afval in motietekst: dan alleen de link. Motie van wantrouwen krijgt een label. Ontbrekend oordeel: "niet in onze gegevens". Herhaalde staart in motietitel (motie 70) weggehaald.
- Amendement "verandert het wetsvoorstel"; begrip novelle toegevoegd; regel voor wetsvoorstel matcht niet meer op "wetgevingsoverleg".
- Vragenuur: de onderwerpen uit de paginadata staan onder de vraag, en de standpunten zijn per onderwerp gegroepeerd.
- Verslag: "voorlopig" in plaats van "ongecorrigeerd", geen losse "#", regels ~62 tekens, contrast van markering in donker.
- Figuren: alt leeg als de naam ernaast staat, niet meer lazy (de lezer zag lege rondjes), verkleind naar 180×240 (was 360×480).
A: afloopblok is geen wit vlak met rand meer (leek op een ballon); focusring op geel donker; geel gedempt in donker thema; moties-pagina per debat ingeklapt; rij met moties nu bij elk debat met moties; intro op telefoon één regel; hoofdpagina van een debat in delen begint met de vraag, delenlijst onder de kaart.
B: videolinks op de voorpagina; geen tellingen meer op de voorpagina; citaat rechtop met het woord "Letterlijk" (cursief was moeilijk leesbaar); tijdlijn dun gestippeld (botste met de citaatstreep); groeperingsregel aangescherpt: geen koppeling via stemmingen, verzameldossiers (`nieuw/eigen/verzameldossiers.json`) verbinden niets, vragenuur nooit samengevoegd.
C: elke deelpagina heeft een eigen kop "Deel 3 van 6: …", ← → in de kaart en in de vaste balk ("← Deel 2 · Deel 4 →"), "Volgend debat" alleen tussen debatten; "Waar ging het om" en "Hoe liep het af" zijn de eerste twee hoofdstukken; agendatitel boven de vraag en in de paginatitel; standpunten zonder kaartvlak (leek op citaat); voorpagina met h1 en datums als koppen, stemmingen klein; focus geel op de donkere kaart.

Bewust niet overgenomen:
- "Nog niet over gestemd" / "Stemming verwacht op dinsdag" (lezer): verboden door de eigenaar (verouderende informatie, datum staat niet in de data).
- Gewone titels per motie en per onderwerp, korte opsommingen per deel: vraagt nieuwe geschreven inhoud per debat (zie velden hierboven).
- Vaste deeltitels "<fase>: <sprekers>" in plaats van de inhoudelijke titels (politicoloog): de eigenaar vroeg om inhoudelijke titels; ze komen uit de nagelezen paginadata.
- Andere regel voor de vraagbron (politicoloog, "coalitiepartij of kabinet"): dat is de schrijfopdracht `prompts/kaart.md`, die deze sessie niet mag wijzigen. Doorgegeven als advies in het eindverslag.
- Zetelbalk bij elke naam: het zetelaantal staat er al als tekst; een balk per naam maakt de kaart drukker.
