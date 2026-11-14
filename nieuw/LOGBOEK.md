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

### Ronde 2: beoordeling (vier nieuwe beoordelaars)
Controleur: weer geen fout in citaten, uitslagen, zetels, datums, nalees-datums, feed of links (31 unieke citaten, 90 moties, 3.990 beurten nagelopen). Wel: label "niet duidelijk oneens" bij een kaart waarvan versie c wél een botsing is (de vlag `geen_botsing` hoort bij versie a), meta description brak midden in een woord, 7 videolinks bij hele korte beurten wezen naar een later moment, nog enkele "nog"-zinnen, en "D66 (26)" zonder "coalitie" in de regel "Aan het woord". Alles hersteld. Videoregel aangescherpt: het moment moet vóór de volgende spreekbeurt beginnen.
Controleur vond ook één aanhaling in een samenvatting die niet letterlijk is ("echt iets doen aan de genocide…", in het verslag "echt iets te doen"). Dat zit in `data/strips/68113dc2…-d4.json`; die mag deze sessie niet wijzigen. `controle.py` waarschuwt nu voor aanhalingen tussen dubbele aanhalingstekens in de paginadata die niet letterlijk in het debat staan. Doorgegeven in het eindverslag.

Overgenomen:
- Belastingplan 10 en 12 november (12 november is de derde termijn): vaste koppeling "Ook met de agendatitel …" tussen debatten met dezelfde agendatitel, in alle varianten. De foute zin "de tweede termijn staat niet in onze gegevens" verschijnt niet meer als het debat moties heeft of een ander debat met dezelfde titel.
- Delenlijst toont per deel van wie de citaten op de kaart van dat deel zijn (fractie en zetels), zodat ook de botsingen uit latere delen (Wilders–Paternotte, Markuszower–Bontenbal, …) zichtbaar zijn.
- Debatten zonder kaart: geen rij figuren van de eerste sprekers meer als enige inhoud, maar "Aan het woord: …" met alle fracties en zetels (de coalitie verdween eerder in "+10").
- Gelijke figuren: heeft één van de twee sprekers op een kaart geen figuur, dan krijgen beide het silhouet (Bertram tegenover Van Oosterhout).
- Uitleg: oppositie stemt mee "met de coalitiefracties" (niet "met het kabinet"); aanhouden doet de indiener; "overbodig" toegevoegd; meerderheid = meer dan de helft van de uitgebrachte stemmen; een niet-uitgevoerde motie moet de regering uitleggen. Partijgedrag.nl als "site van anderen".
- Stemmingen-rij zegt dat welke moties in stemming kwamen niet in de gegevens staat en dat de uitslag bij het debat staat.
- Eerste alinea van de samenvatting in "Waar ging het om"; de rest verderop onder "Meer over dit debat" (kaart eerder in beeld, geen dubbele tekst).
- Figuren lazy geladen (behalve op de kaart van C), echte maat 180×240; tijden in het verslag als 14.01; standpunten in één kolom (regellengte).
A: zijkolom niet meer sticky; geel in donker gedempt (#c9b24a); onzichtbare h1 met eigen klasse.
B: tellingen weer op de voorpagina (politicoloog ronde 2: een uitslagtelling is geen ranglijst; ronde 1 vond het tegendeel, gekozen voor zichtbare besluiten); "Waar ging het om" bij een onderwerp is nu het Kamerstuk met zijn titel uit de data (niet de vraag van één crisisdebat); citaat over de volle breedte met het figuur in de naamregel; eigen tekst heeft geen linkerstreep meer (die is voor citaten); vragen onderstreept als link; vaste adressen (nummeren vanaf het oudste onderwerp, vragenuur met datum).
C: kaart staat in `main`; elk deel heeft zijn eigen h1 (de titel van het deel), de vraag is dan h2; in de kaart een blok "Waar ging het om?" (eerste alinea) naast "Hoe liep het af?"; citaten naast elkaar vanaf 760px; figuur in de naamregel; focusring in het witte citaatkaartje donker; vaste balk alleen onder 700px; vaste `role=status` voor "Link gekopieerd"; verslagpagina met sitenaam bovenaan; "Volgend debat" volgt de volgorde van de voorpagina.

Bewust niet overgenomen:
- Kaartcitaten korter maken (interface-expert): de citaten komen uit de data en de schrijfopdracht; doorgegeven als advies voor `prompts/kaart.md`.
- Lettertype zelf hosten: het artifact staat alleen Google Fonts toe; voor de echte site staan de ttf-bestanden klaar in `nieuw/fonts/` (omzetten naar woff2 en `@font-face` lokaal is een kleine stap).
- Binnen een dag nieuwste eerst in A (lezer): een agenda leest van ochtend naar avond; de regel staat op "Zo werken we".
- Dictum van een motie bovenaan in plaats van de titel (lezer): de omschrijving is de officiële titel; de letterlijke tekst staat uitklapbaar eronder.

### Ronde 3: beoordeling (vier nieuwe beoordelaars)
Controleur: geen feitelijke fout. Middel: coalitielabel ontbrak in de delenlijst; uitleg bij twee stemmingen ("welke, kunnen we niet afleiden") terwijl de voorzitter het onderwerp aankondigt; in C ontbrak de koppeling tussen dagen op deelpagina's; nog een niet-letterlijke aanhaling in `data/strips/68113dc2…-d4.json` ("richtingwijzers zie, maar geen koers"). Klein: video-moment gelijk aan begin volgende beurt (regel nu strikt "vóór"), vijf moties zonder getoonde tekst (zoeken nu op "verzoekt …"/"zegt …"), afgebroken meta descriptions (nu: langer dan 300 tekens → vaste beschrijving). Alles behalve de data-aanhalingen hersteld.

Ernstig volgens lezer, interface-expert en politicoloog, en overgenomen:
- **Uitslag van het Belastingplan onvindbaar.** Nieuwe vaste regel: een stemmingsronde hoort bij een debat als de voorzitter haar aankondigt met de agendatitel ("Aan de orde is de stemming in verband met … het Belastingplan 2027"). Die rondes staan nu bij "Hoe liep het af" (A, C), op de tijdlijn (B), en stemmingen krijgen die titel ("Stemmingen over het Belastingplan 2027"). Zonder uitslag (staat niet in de data), wel met link naar het verslag.
- **Kaart te laat in beeld op debatpagina's (A, B) / "Waar en Hoe" na de citaten (C).** Bovenaan nu één zin "Waar ging het om" (de eerste zin van de samenvatting) en één regel "Hoe liep het af"; daarna direct de kaart; de rest van de samenvatting en een eigen sectie "Hoe liep het af" met uitleg en moties verderop. In C staan beide regels in de kaart direct onder de vraag.
- **Termijnen.** 12 november is de derde termijn; het faselabel uit de data zei "Inbreng van de Kamer". Vaste regel: had een eerder debat met dezelfde agendatitel al een tweede termijn, dan heet de fase "Derde termijn: …". Begrip uitgebreid met de derde termijn.
- **Begin buiten de gegevens.** Begint een debat niet met inbreng van de Kamer (of heet het "Voortzetting"), en staat het begin niet op een eerdere dag in de data, dan staat er dat het begin buiten onze gegevens valt (Belastingplan 10 november, politie-WGO).
- **Mede-indieners.** Alle indieners met fractie en "coalitie" (motie 16 van Mutluer werd ook door VVD, CDA en D66 ondertekend).
- **"Aangehouden"** is geen oordeel van het kabinet: getoond als "Aangehouden door de indiener".
- **Label "oppositie" weg**; alleen "coalitie" staat erbij (de politicoloog: het label "oppositie" bij 14 fracties versterkt het tweekampenbeeld). Zin "oppositie stemt vaak mee" vervangen door "de meerderheid verschilt per stemming".
- **Kop van een deel** is nu de agendatitel met het deelnummer (de samenvattende titel met conflicttaal staat boven de samenvatting, niet als kop en niet in de kaart van C).
- **Fractieregel onder elke kaart**, ook op de voorpagina en in B en C (stond alleen op de debatpagina's van A).
- C: vaste balk lag op de computer over de voettekst (CSS-volgorde) — hersteld; kaart alleen schermhoog als er citaten in staan; knop heet "Eerder debat →" (de volgorde loopt van nieuw naar oud); tikdoelen in het citaatkaartje 32px; figuren in de twee citaatkaartjes op gelijke hoogte.
- A/B: "elk deel heeft een eigen samenvatting" alleen als dat waar is; regellengte overal max. 62 tekens; tikdoelen met extra ruimte; moties-pagina met korte inleiding; vraag onderstreept als link; "Botsingsrij" heet "Rij met kaart"; B spreekt van vergaderdagen en houdt "Voortzetting" in de titel, tellingen als tekst in plaats van tegels.
- Spreidingsregel van het vragenuur staat nu op "Zo werken we".

Bewust niet overgenomen:
- H1 van een debat zonder delen blijft de inhoudelijke titel uit de paginadata (de eigenaar vroeg om inhoudelijke titels; bij delen is de kop nu de agendatitel met deelnummer).
- Kaart met "Waar/Hoe" vóór de citaten maakt in C het eerste scherm iets voller; toch zo gelaten, omdat eis 2 (afloop direct onder de kop) en eis 1 anders botsen.
- B: Kamerstuk XIII als enige dossier bij het digitaliserings-WGO (de moties zitten daar allemaal in); de agendatitel staat erboven als kop.
