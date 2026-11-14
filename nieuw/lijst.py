"""Bestandslijsten voor het publiceren als artifact: python3 lijst.py <variant> pagina|fig"""
import json, sys
from pathlib import Path
v, soort = sys.argv[1], sys.argv[2]
r = Path(__file__).parent / "uit" / v
fs = sorted(p.relative_to(r).as_posix() for p in r.rglob("*") if p.is_file() and p.name not in ("_artifact.html", "index.html") or p.parent != r)
fs = [f for f in fs if f.startswith("fig/")] if soort == "fig" else [f for f in fs if not f.startswith("fig/")]
print(json.dumps([{"path": f} for f in fs], separators=(",", ":")))
print(len(fs), file=sys.stderr)
