#!/usr/bin/env bash
# Point d'entrée local Novissi-Droit IA. Aucun Docker requis.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

pause() { printf '\nAppuyez sur Entrée pour continuer…'; read -r _ || true; }
need_bash() { command -v bash >/dev/null 2>&1 || { echo "Bash est requis (Git Bash sous Windows)." >&2; exit 1; }; }
python_cmd() {
  for c in python3 python; do if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys;sys.exit(sys.version_info < (3,10))' >/dev/null 2>&1; then echo "$c"; return 0; fi; done
  if command -v py >/dev/null 2>&1 && py -3 -c 'import sys;sys.exit(sys.version_info < (3,10))' >/dev/null 2>&1; then echo 'py -3'; return 0; fi
  return 1
}
install_all() {
  command -v node >/dev/null 2>&1 || { echo "Node.js est absent. Installez une version LTS depuis https://nodejs.org puis relancez."; return 1; }
  bash setup.sh
}
launch_all() {
  if [ ! -d "$ROOT/.venv" ] || [ ! -d "$ROOT/frontend/node_modules" ]; then
    echo "Installation incomplète : lancement de l'installation…"
    install_all || return 1
  fi
  bash dev.sh
}
run_tests() {
  local py
  py="$(python_cmd)" || { echo "Python 3.10+ est requis."; return 1; }
  if [ -f "$ROOT/.venv/bin/activate" ]; then . "$ROOT/.venv/bin/activate"; elif [ -f "$ROOT/.venv/Scripts/activate" ]; then . "$ROOT/.venv/Scripts/activate"; else echo "Environnement Python absent. Choisissez d'abord l'installation."; return 1; fi
  (cd "$ROOT" && python -m pytest -q) || echo "Certains tests backend ont échoué. Consultez les détails ci-dessus."
  if [ -d "$ROOT/frontend/node_modules" ]; then (cd "$ROOT/frontend" && npm test -- --reporter=default && npm run build); else echo "Frontend non installé : npm test/build non exécutés."; fi
}
audit_language() {
  local py
  py="$(python_cmd)" || { echo "Python 3.10+ est requis."; return 1; }
  if [ -f "$ROOT/.venv/bin/activate" ]; then . "$ROOT/.venv/bin/activate"; elif [ -f "$ROOT/.venv/Scripts/activate" ]; then . "$ROOT/.venv/Scripts/activate"; else echo "Environnement Python absent. Installez d'abord les dépendances."; return 1; fi
  cd "$ROOT"
  python -m backend.language_sources.voix_du_togo
}
diagnose() { bash diagnose.sh; }
status() {
  echo "Projet : $ROOT"
  echo "Python : $(python_cmd 2>/dev/null || echo 'absent — Python 3.10+ requis')"
  echo "Node.js : $(node --version 2>/dev/null || echo absent)"
  echo "npm : $(npm --version 2>/dev/null || echo absent)"
  [ -d "$ROOT/.venv" ] && echo "Environnement Python : présent" || echo "Environnement Python : absent"
  [ -d "$ROOT/frontend/node_modules" ] && echo "Dépendances frontend : présentes" || echo "Dépendances frontend : absentes"
  [ -f "$ROOT/.env" ] && echo "Configuration .env : présente (valeurs masquées)" || echo "Configuration .env : absente"
  [ -f "$ROOT/data/languages/voix_du_togo_audit.json" ] && echo "Audit Voix du Togo : rapport présent" || echo "Audit Voix du Togo : non effectué"
  echo "Ports habituels : frontend 5173, backend 8000"
}
need_bash
while true; do
  printf '\n===========================================\n'
  printf '       NOVISSI-DROIT IA — MENU LOCAL\n'
  printf '===========================================\n'
  printf '1. Installer / vérifier les dépendances\n'
  printf '2. Lancer frontend + backend\n'
  printf '3. Collecter / actualiser les textes juridiques\n'
  printf '4. Lancer les tests et le build\n'
  printf '5. Auditer Voix du Togo (langues locales)\n'
  printf '6. Diagnostiquer les sources juridiques\n'
  printf '7. Vérifier la configuration locale\n'
  printf '0. Quitter\n'
  printf 'Votre choix : '
  read -r choice || exit 0
  case "$choice" in
    1) install_all; pause ;;
    2) launch_all; pause ;;
    3) if [ -f "$ROOT/.venv/bin/activate" ]; then . "$ROOT/.venv/bin/activate"; elif [ -f "$ROOT/.venv/Scripts/activate" ]; then . "$ROOT/.venv/Scripts/activate"; else echo "Installez d'abord les dépendances."; pause; continue; fi; (cd "$ROOT/backend" && python legal_scraper.py --once); pause ;;
    4) run_tests; pause ;;
    5) audit_language; pause ;;
    6) diagnose; pause ;;
    7) status; pause ;;
    0) exit 0 ;;
    *) echo "Choix invalide."; pause ;;
  esac
done
