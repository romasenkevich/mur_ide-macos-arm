#!/usr/bin/env bash
if [[ $# -eq 0 ]]; then OPT1="-w -s"; fi
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/Urho3DPlayer" "$DIR/Scripts/Editor.as" $OPT1 "$@"
