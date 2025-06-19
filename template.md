# Rapport de veille – Semaine {{ week }} / {{ year }}

## Executive summary
*{{ vulns | length }}* vulnérabilités critiques détectées cette semaine.  
*{{ threats | length }}* rapports de menace validés dans OpenCTI.

| CVE | Vendor / Produit | Score |
|-----|------------------|-------|
{% for v in vulns %}
| {{ v.cve | default(v.title) }} | {{ v.vendor | default("") }} | {{ v.score | default("") }} |
{% endfor %}

---

## Menaces (OpenCTI)

| Nom du rapport | Sévérité | Lien |
|----------------|----------|------|
{% for t in threats %}
| {{ t.name }} | {{ t.severity }} | [OpenCTI]({{ t.url }}) |
{% endfor %}

---

## Actions recommandées (premier tri)
- [ ] Vérifier correctifs disponibles pour les CVE listées
- [ ] Informer les équipes infra et réseau
- [ ] Mettre à jour l’inventaire si nécessaire