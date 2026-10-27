#!/usr/bin/env bash
# Fonctions communes aux scripts (ne pas lancer directement).
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv"

c_ok()   { printf '\033[32m✔ %s\033[0m\n' "$*"; }
c_warn() { printf '\033[33m⚠ %s\033[0m\n' "$*"; }
c_err()  { printf '\033[31m✘ %s\033[0m\n' "$*" >&2; }
c_step() { printf '\n\033[1m== %s ==\033[0m\n' "$*"; }

# Trouve un Python >= 3.10 (python3, python, puis « py -3 » sous Windows)
find_python() {
  local c
  for c in python3 python "py -3"; do
    if $c -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' >/dev/null 2>&1; then
      PY="$c"; return 0
    fi
  done
  return 1
}

# Active le venv (Linux/macOS : bin/, Windows : Scripts/)
activate_venv() {
  if   [ -f "$VENV/bin/activate" ];     then . "$VENV/bin/activate"
  elif [ -f "$VENV/Scripts/activate" ]; then . "$VENV/Scripts/activate"
  else c_err "Environnement Python absent. Lance d'abord :  bash setup.sh"; exit 1; fi
}

ensure_env() {
  if [ ! -f "$ROOT/.env" ]; then
    cp "$ROOT/.env.example" "$ROOT/.env"
    c_warn ".env créé depuis .env.example : ouvre-le et colle tes clés (GEMINI_API_KEY, GROQ_API_KEY)."
  fi
}
