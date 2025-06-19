#!/usr/bin/env python
"""
Collecte KEV + CERT-FR + rapports OpenCTI
Créé data_<YEAR>_<WEEK>.json
"""
from datetime import datetime, timedelta, timezone
import feedparser, requests, json, os, pathlib, sys
from pycti import OpenCTIApiClient

# --------------------------------------------------------------------------- #
TODAY  = datetime.now(timezone.utc)
YEAR, WEEK = TODAY.isocalendar()[:2]
SINCE = (TODAY - timedelta(days=7)).isoformat(timespec="seconds")

def load_kev():
    """Télécharge la KEV, avec fallback GitHub si besoin."""
    urls = [
        # URL officielle (2024+)
        "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        # Miroir non-officiel (toujours JSON brut)
        "https://raw.githubusercontent.com/cisagov/kev-data/main/kev.json",
    ]
    headers = {"User-Agent": "veille-cyber/1.0 (+https://github.com/<ORG>/veille-cyber)"}
    for u in urls:
        try:
            r = requests.get(u, headers=headers, timeout=30)
            r.raise_for_status()
            kev = r.json()["vulnerabilities"]
            print(f"[+] KEV chargée depuis {u} ({len(kev)} entrées)")
            return kev
        except Exception as e:
            print(f"[!] Échec sur {u} → {e}")
    sys.exit("Impossible de récupérer la KEV – abandon")

def parse_certfr():
    d = feedparser.parse("https://www.cert.ssi.gouv.fr/feed/")
    recent = []
    for e in d.entries:
        pub = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
        if pub > TODAY - timedelta(days=7):
            recent.append({"title": e.title, "link": e.link})
    print(f"[+] CERT-FR : {len(recent)} entrées récentes")
    return recent

def get_opencti_reports() -> list[dict]:
    api = OpenCTIApiClient(
        os.getenv("OPENCTI_URL"),
        os.getenv("OPENCTI_TOKEN"),
        ssl_verify=False,                 # mettez le .pem interne quand prêt
    )

    # ----- filtre conforme au schéma GraphQL >= 5.6
    my_filter = {
        "mode": "and",                    # relation entre les filtres
        "filters": [
            {
                "key": "created_at",
                "values": [SINCE],        # ex. "2025-06-12T14:32:00Z"
                "operator": "gt",
                "mode": "or"              # relation entre les *values* (ici 1 seule)
            }
        ],
        "filterGroups": []                # laissé vide
    }

    reports = api.report.list(
        filters=my_filter,
        first=50,
        orderBy="created",
        orderMode="desc",
    )

    return [
        {
            "name": r["name"],
            "severity": r.get("confidence", 0),
            "url": f"{api.api_url}/dashboard/reports/{r['id']}",
        }
        for r in reports
    ]

# --------------------------------------------------------------------------- #
# KEV → on garde uniquement les vulnérabilités < 7 jours
vulns = []
for cve in load_kev():
    if cve["dateAdded"] >= SINCE[:10]:
        vulns.append({
            "cve":    cve["cveID"],
            "vendor": cve.get("vendorProject", ""),
            # Certains enregistrements n’ont plus de score : on essaye cvssBaseScore, sinon ""
            "score":  cve.get("cvssBaseScore", cve.get("cvssScore", "")),
        })
vulns.extend(parse_certfr())            # ajoute les actus CERT-FR
threats = get_opencti_reports()         # rapports internes

# Sauvegarde JSON
out = pathlib.Path(f"data_{YEAR}_{WEEK}.json")
out.write_text(json.dumps({"vulns": vulns, "threats": threats}, indent=2, ensure_ascii=False))
print(f"[OK] {out} écrit ({out.stat().st_size/1024:.1f} kB)")