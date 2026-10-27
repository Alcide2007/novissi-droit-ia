#!/usr/bin/env bash
# Sauvegarde cohérente : registre, conversations, PDF originaux et textes -> backups/novissi-AAAAMMJJ-HHMM.tgz
# Restauration : arrête l'application, puis   tar xzf backups/<fichier>.tgz -C data/   (ne supprime rien d'autre).
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
cd "$ROOT"; activate_venv
STAMP="$(date +%Y%m%d-%H%M)"; TMP="$(mktemp -d)"; mkdir -p backups
python - "$ROOT/data" "$TMP" <<'PY'
import sqlite3, sys, pathlib
src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
for name in ("registry.db", "conversations.db"):
    if (src / name).exists():                      # API de sauvegarde SQLite : copie cohérente même pendant l'écriture
        a, b = sqlite3.connect(src / name), sqlite3.connect(dst / name)
        a.backup(b); b.close(); a.close()
PY
tar czf "backups/novissi-$STAMP.tgz" -C "$TMP" . -C "$ROOT/data" $( [ -d data/originals ] && echo originals ) $( [ -d data/laws ] && echo laws )
rm -rf "$TMP"
c_ok "Sauvegarde : backups/novissi-$STAMP.tgz"
