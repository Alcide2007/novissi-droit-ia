#!/usr/bin/env bash
# Explique pourquoi un site donne (ou non) des textes.   Usage : bash diagnose.sh https://jo.gouv.tg
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
[ -z "$1" ] && { echo "Usage : bash diagnose.sh <URL>"; exit 1; }
cd "$ROOT"; ensure_env; activate_venv
cd backend && python legal_scraper.py --diagnose "$1"
