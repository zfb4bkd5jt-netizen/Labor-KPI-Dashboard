#!/usr/bin/env bash
# Erzeugt das Offline-Paket für Windows mit mitgeliefertem Python (keine Python-Installation nötig).
#
#   ./build_portable.sh              aus dem aktuellen Commit
#   ./build_portable.sh v1.2         aus einem Git-Tag
#                                    -> dist/Labor-KPI-Dashboard_<version>_portable_Windows.zip
#
# Gebaut wird per "git archive": nur eingecheckte Dateien kommen ins Paket. Excel-Exporte,
# daten.js und stand.js sind nicht in Git und landen deshalb nie im Paket.
set -euo pipefail
REF="${1:-HEAD}"
HIER="$(cd "$(dirname "$0")" && pwd)"
cd "$HIER"
git rev-parse -q --verify "$REF^{commit}" >/dev/null || { echo "$REF gibt es in Git nicht."; exit 1; }

VER="$(git show "$REF:quellcode/bauen.py" | sed -n 's/.*<span id="version">Version \([^<]*\)<.*/\1/p' | head -1)"
[ -n "$VER" ] || { echo "Version in quellcode/bauen.py nicht gefunden."; exit 1; }
[ "$REF" = "HEAD" ] && VER="$VER-$(git rev-parse --short HEAD)"
PYVER="$(git show "$REF:portable/PYTHON_VERSION" | tr -d '[:space:]')"

ARBEIT="$(mktemp -d)"; trap 'rm -rf "$ARBEIT"' EXIT
mkdir -p "$ARBEIT/src"; git archive "$REF" | tar -x -C "$ARBEIT/src"
S="$ARBEIT/src"
OUT="$ARBEIT/Labor-KPI-Dashboard"; mkdir -p "$OUT"

# 1) Offizielles portables Python für Windows (NuGet-Paket "python" der Python Software Foundation)
curl -sSL --retry 3 -o "$ARBEIT/python.nupkg" "https://api.nuget.org/v3-flatcontainer/python/$PYVER/python.$PYVER.nupkg"
unzip -q "$ARBEIT/python.nupkg" -d "$ARBEIT/nupkg"
cp -r "$ARBEIT/nupkg/tools" "$OUT/python"
rm -rf "$OUT/python/include" "$OUT/python/libs"

# 2) pandas und openpyxl als fertige Windows-Pakete (tzdata, weil Windows keine Zeitzonendaten mitbringt)
pip install -q --target "$OUT/python/Lib/site-packages" --platform win_amd64 \
  --python-version "${PYVER%.*}" --implementation cp --only-binary=:all: --no-compile \
  -r "$S/requirements.txt" tzdata
# Mitgelieferte Selbsttests von pandas und numpy werden nicht gebraucht (spart rund 40 MB)
rm -rf "$OUT/python/Lib/site-packages/pandas/tests"
find "$OUT/python/Lib/site-packages/numpy" -type d -name tests -prune -exec rm -rf {} +

# 3) Dashboard und Startdateien (nur was im Ordner dashboard/ eingecheckt ist)
cp -r "$S/dashboard/." "$OUT/"
find "$OUT" -name __pycache__ -prune -exec rm -rf {} +

mkdir -p "$HIER/dist"
ZIEL="$HIER/dist/Labor-KPI-Dashboard_${VER}_portable_Windows.zip"
rm -f "$ZIEL"; (cd "$ARBEIT" && zip -qr "$ZIEL" Labor-KPI-Dashboard)
echo "Fertig: $ZIEL ($(du -h "$ZIEL" | cut -f1))"
