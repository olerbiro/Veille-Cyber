# lance depuis le planificateur Windows
$Repo = "C:\src\veille-cyber"
Set-Location $Repo
$env:Path = "$Repo\.venv\Scripts;$env:Path"
git pull
python scripts\collect_feeds.py
python scripts\build_report.py
git add docs\veille
git commit -m "Rapport auto $(Get-Date -Format yyyy-MM-dd)" 2>$null
git push