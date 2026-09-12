#!/usr/bin/env bash
# Run the full pipeline for one city, Stage 1 -> Stage 3.
# Usage:  bash code/run_city.sh <city>
# Each step is logged and a failure stops the chain for that city only.
set -o pipefail
CITY="$1"
[ -z "$CITY" ] && { echo "usage: run_city.sh <city>"; exit 2; }

cd "$(dirname "$0")/.." || exit 1
export PATH="/opt/homebrew/bin:$PATH"
LOG="outputs/${CITY}_pipeline.log"
: > "$LOG"

step () {
  local name="$1"; shift
  echo "=== [$CITY] $name  $(date -u +%H:%M:%S) ===" | tee -a "$LOG"
  if ! uv run python "$@" --city "$CITY" >>"$LOG" 2>&1; then
    echo "!!! [$CITY] FAILED at $name — see $LOG" | tee -a "$LOG"
    return 1
  fi
  echo "    [$CITY] ok: $name" | tee -a "$LOG"
}

step "01b census geography" code/01_acquire/01b_census_geography.py || exit 1
step "01c ACS density"      code/01_acquire/01c_acs_density.py      || exit 1
step "01d HPMS AADT"        code/01_acquire/01d_hpms_aadt.py        || exit 1

echo "=== [$CITY] 01a OSM network (urban area) $(date -u +%H:%M:%S) ===" | tee -a "$LOG"
if ! uv run python code/01_acquire/01a_osm_network.py --city "$CITY" \
      --extent urban_area >>"$LOG" 2>&1; then
  echo "!!! [$CITY] FAILED at 01a OSM" | tee -a "$LOG"; exit 1
fi
echo "    [$CITY] ok: 01a OSM network" | tee -a "$LOG"

step "01e land-use mix"     code/01_acquire/01e_landuse_mix.py      || exit 1
step "01f footprints"       code/01_acquire/01f_building_footprints.py || exit 1
step "02a analysis frame"   code/02_network/02a_analysis_frame.py   || exit 1
step "02b permeability P3"  code/02_network/02b_permeability.py     || exit 1
step "02d through routes P1" code/02_network/02d_through_routes.py  || exit 1
step "02c betweenness"      code/02_network/02c_betweenness.py      || exit 1
step "03a controls"         code/03_conflate/03a_controls.py        || exit 1
step "03b analysis table"   code/03_conflate/03b_analysis_table.py  || exit 1

echo "=== [$CITY] PIPELINE COMPLETE $(date -u +%H:%M:%S) ===" | tee -a "$LOG"
