"""Bouwt alle drie de varianten en draait de eigen controle. Gebruik: python3 nieuw/bouw.py [a b c]"""
import subprocess, sys
from pathlib import Path
hier = Path(__file__).resolve().parent
varianten = sys.argv[1:] or ["a", "b", "c"]
for v in varianten:
    subprocess.run([sys.executable, str(hier / f"{v}.py")], check=True, cwd=hier)
sys.exit(subprocess.run([sys.executable, str(hier / "controle.py"), *varianten], cwd=hier).returncode)
