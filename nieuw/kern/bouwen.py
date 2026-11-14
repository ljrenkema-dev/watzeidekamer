"""Hulp voor het wegschrijven van een variant: map leegmaken, bestanden schrijven, figuren, deelbeelden, sitemap, RSS."""
import shutil
from pathlib import Path
from . import model as M, stukken as S, figuren as F

NIEUW = Path(__file__).resolve().parents[1]


class Uitvoer:
    def __init__(self, naam):
        self.dir = NIEUW / "uit" / naam
        self.paden = []
        og = self.dir / "og"
        bewaar = None
        if og.exists():  # deelbeelden bewaren als Chromium straks ontbreekt
            bewaar = NIEUW / "uit" / f".og-{naam}"
            shutil.rmtree(bewaar, ignore_errors=True)
            shutil.copytree(og, bewaar)
        shutil.rmtree(self.dir, ignore_errors=True)
        self.dir.mkdir(parents=True)
        if bewaar:
            shutil.copytree(bewaar, og)
            shutil.rmtree(bewaar, ignore_errors=True)

    def schrijf(self, pad, inhoud, sitemap=True):
        f = self.dir / pad
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(inhoud)
        if sitemap and pad.endswith(".html"):
            self.paden.append(pad)

    def afronden(self, css, rss_items, og_kleur):
        (self.dir / "style.css").write_text((NIEUW / "kern" / "basis.css").read_text() + "\n" + css)
        (self.dir / "favicon.svg").write_text(S.FAVICON)
        (self.dir / "robots.txt").write_text(S.ROBOTS)
        (self.dir / "sitemap.xml").write_text(S.sitemap(self.paden))
        (self.dir / "feed.xml").write_text(S.rss(rss_items))
        F.schrijf(self.dir)
        S.maak_deelbeelden(self.dir, M.debatten(), {"bg": og_kleur})
