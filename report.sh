#!/usr/bin/env bash
# Rapport d'exhaustivité de la collecte : pages inspectées, ressources par statut, extractions, changements, erreurs.
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$ROOT"; ensure_env; activate_venv
cd backend && python legal_scraper.py --report
