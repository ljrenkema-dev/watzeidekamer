"""Draai check.py en evenwicht.py op een proefversie (data/proeftuin/<versie>/<id>.json) zonder data/strips aan te raken.
Gebruik: python3 scripts/check_proef.py <versie> <id> [--bestand <naam>.json] [--evenwicht]"""
import sys, tempfile, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check, evenwicht  # noqa: E402

versie, pid = sys.argv[1], sys.argv[2]
tmp = Path(tempfile.mkdtemp())
(tmp / "data" / "strips").mkdir(parents=True)
for naam in os.listdir(ROOT / "data"):
    if naam != "strips":
        os.symlink(ROOT / "data" / naam, tmp / "data" / naam)
bestand = sys.argv[sys.argv.index("--bestand") + 1] if "--bestand" in sys.argv else f"{pid}.json"
os.symlink(ROOT / "data" / "proeftuin" / versie / bestand, tmp / "data" / "strips" / f"{pid}.json")
check.ROOT = evenwicht.ROOT = tmp
f, w = check.check(pid)
print(f"{versie}/{bestand}: {'OK' if not f else f'{len(f)} fout(en)'}" + (f", {len(w)} waarschuwing(en)" if w else ""))
for x in f: print("  FOUT  " + x)
for x in w: print("  let op " + x)
if "--evenwicht" in sys.argv:
    try:
        print(evenwicht.evenwicht(pid))
    except Exception as e:
        print("evenwicht:", e)
sys.exit(1 if f else 0)
