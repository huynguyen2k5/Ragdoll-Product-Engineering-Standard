#!/bin/sh
set -eu

RAGDOLL_DATA_HOME=${RAGDOLL_HOME:-"$HOME/.ragdoll"}
BIN_DIR=${RAGDOLL_BIN_DIR:-"$HOME/.local/bin"}
PURGE=false
if [ "${1:-}" = "--purge-data" ]; then
  PURGE=true
fi

if [ -x "$BIN_DIR/ragdoll" ]; then
  "$BIN_DIR/ragdoll" stop >/dev/null 2>&1 || true
fi
rm -f "$BIN_DIR/ragdoll"
rm -rf "$RAGDOLL_DATA_HOME/runtime"

if [ "$PURGE" = true ]; then
  rm -rf "$RAGDOLL_DATA_HOME"
  echo "Ragdoll runtime and user data were permanently removed."
else
  echo "Ragdoll runtime removed. User data preserved at $RAGDOLL_DATA_HOME"
  echo "Use ./uninstall.sh --purge-data only if you intentionally want to delete Project History and local configuration."
fi
