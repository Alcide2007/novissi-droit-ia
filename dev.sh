#!/usr/bin/env bash
# Lance backend (port 8000) + frontend (port 5173). Ctrl+C arrête les deux.
#   bash dev.sh            -> les deux
#   bash dev.sh backend    -> backend seul
#   bash dev.sh frontend   -> frontend seul
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$ROOT"
MODE="${1:-all}"
ensure_env
activate_venv

BACK_PID=""
cleanup() { [ -n "$BACK_PID" ] && kill "$BACK_PID" 2>/dev/null; exit 0; }
trap cleanup INT TERM EXIT

if [ "$MODE" != "frontend" ]; then
  c_step "Backend → http://localhost:8000"
  ( cd backend && exec python -m uvicorn main:app --host 127.0.0.1 --port 8000 ) &
  BACK_PID=$!
  for i in $(seq 1 40); do
    python - <<'PY' >/dev/null 2>&1 && break
import urllib.request; urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2)
PY
    sleep 1
    [ "$i" = 40 ] && { c_err "Le backend ne répond pas. Regarde les erreurs ci-dessus."; exit 1; }
  done
  c_ok "Backend en ligne"
  python - <<'PY'
import json,urllib.request
h=json.load(urllib.request.urlopen("http://127.0.0.1:8000/health"))
print("   textes indexés :",h["chunks"]," | fournisseurs IA :",h["ai"] or "AUCUN (renseigne .env)")
PY
fi

if [ "$MODE" = "backend" ]; then wait "$BACK_PID"; exit 0; fi

c_step "Frontend → http://localhost:5173"
cd frontend
VITE_API_TARGET=http://localhost:8000 npm run dev
