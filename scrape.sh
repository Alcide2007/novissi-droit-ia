#!/usr/bin/env bash
# Récupère les lois depuis jo.gouv.tg (page « Lois », 970 textes). Reprend là où il s'est arrêté.
#   bash scrape.sh          -> jusqu'à 400 pages/PDF par passe
#   bash scrape.sh 1000     -> plafond personnalisé
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$ROOT"; ensure_env; activate_venv
cd backend && python legal_scraper.py --once --max-pages "${1:-400}"
echo; c_warn "Relance dev.sh pour que le backend recharge les nouveaux textes."
