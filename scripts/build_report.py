#!/usr/bin/env python
"""
Lit le JSON généré par collect_feeds.py
→ produit docs/veille/<YEAR>-W<week>.md
→ met à jour veille/README.md (lien Semaine courante)
"""
import json, datetime, pathlib
from jinja2 import Template

year, week = datetime.date.today().isocalendar()[:2]
data_file = pathlib.Path(f"data_{year}_{week}.json") 
if not data_file.exists():
    raise SystemExit(f"Fichier {data_file} introuvable. Lancez collect_feeds.py d'abord.")

data = json.loads(data_file.read_text())
tmpl = Template(pathlib.Path("template.md").read_text(), autoescape=False)
content = tmpl.render(week=week, year=year, **data)

dest = pathlib.Path(f"docs/veille/{year}-W{week:02}.md")
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(content, encoding="utf-8")

# README de la section veille (pointe vers la semaine courante)
readme = pathlib.Path("docs/veille/README.md")
readme.write_text(f"# Veille semaine {week}\n\n[Accéder au rapport]({year}-W{week:02}.md)\n")

print(f"[+] Rapport écrit : {dest}")