#!/usr/bin/env bash
# Installation unique : environnement Python + dépendances backend + dépendances frontend.
set -e
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$ROOT"

c_step "1/4 Python"
find_python || { c_err "Python 3.10+ introuvable. Installe-le depuis python.org (coche « Add Python to PATH »)."; exit 1; }
c_ok "Python : $($PY --version)"
PLAT="$($PY -c 'import sysconfig;print(sysconfig.get_platform())')"
case "$PLAT" in *mingw*) c_warn "Python MSYS2/MinGW détecté ($PLAT) : opencv et scikit-learn s'y installent mal. Utilise le Python de python.org dans Git Bash ou PowerShell.";; esac

c_step "2/4 Environnement virtuel + dépendances backend"
[ -d "$VENV" ] || $PY -m venv "$VENV"
activate_venv
python -m pip install --upgrade pip -q
pip install -r backend/requirements.txt
c_ok "Backend prêt"

c_step "3/4 Frontend (Node)"
command -v node >/dev/null || { c_err "Node.js 18+ introuvable. Installe-le depuis nodejs.org."; exit 1; }
c_ok "Node : $(node --version)"
(cd frontend && npm install)
c_ok "Frontend prêt"

c_step "4/4 Configuration"
ensure_env
command -v tesseract >/dev/null && c_ok "Tesseract (OCR) présent" \
  || c_warn "Tesseract absent : tout marche sauf la lecture OCR des actes scannés (facultatif)."

echo
c_ok "Installation terminée. Étapes suivantes :"
echo "   1) édite .env (clés IA)     2) bash dev.sh     3) ouvre http://localhost:5173"
