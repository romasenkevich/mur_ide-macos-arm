#!/usr/bin/env bash
set -euo pipefail

LIB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$LIB_ROOT/../.." && pwd)"
BIN="$REPO/Urho3D/bin"
BUILD_BIN="$REPO/Urho3D/build/bin"
EDITOR_SH="$BIN/Editor.sh"
PLAYER="$BIN/Urho3DPlayer"

if [[ ! -x "$PLAYER" && -x "$BUILD_BIN/Urho3DPlayer" ]]; then
  ln -sf ../build/bin/Urho3DPlayer "$PLAYER" 2>/dev/null || true
fi

if [[ ! -e "$BIN/Scripts/Editor.as" && -f "$BIN/Data/Scripts/Editor.as" ]]; then
  ln -sf Data/Scripts "$BIN/Scripts" 2>/dev/null || true
fi

if [[ ! -x "$PLAYER" ]]; then
  echo "Не найден Urho3DPlayer. Соберите Urho3D (RUNBOOK.md):" >&2
  echo "  cd \"$REPO/Urho3D\" && cmake -S . -B build -G Ninja && cmake --build build -j" >&2
  exit 1
fi

if [[ ! -f "$EDITOR_SH" ]]; then
  echo "Не найден Editor.sh: $EDITOR_SH" >&2
  exit 1
fi

cd "$BIN"
echo "Запуск редактора сцен Urho3D (Create → Builtin object: Box, Sphere, Cylinder, Cone...)"
exec ./Editor.sh "$@"
