# Reproducing the deposited research

This document describes the existing research scripts as inspected for the public deposit. The research code, configuration, data, and saved results are preserved without methodological changes. The complete acquisition and modelling pipeline was **not rerun as part of preparing this deposit**. Commands below were checked against script arguments and file dependencies; a successful independent end-to-end rerun is not claimed. The primary estimator was separately rerun in an isolated copy and compared with the archived CSV; see [VERIFICATION.md](VERIFICATION.md).

Run commands from the root of a **fresh clone** of this repository. The scripts write derived data, tables, figures, and local provenance/progress logs into that clone. Keep the deposited results available for comparison before rerunning scripts that write the same filenames.

## 1. Which analysis is primary?

The revised six-city primary analysis is implemented in `code/05_model/05x_primary_v2.py`. It uses:

- `data/analysis__aadtfree/analysis_pooled_r800.parquet`;
- units dissolved on functional class, through lanes, access control, ownership, and facility type, with a 0.5-mile merging cap and length-weighted AADT;
- a **400 m minimum segment length**, followed by the script's complete-case rule;
- job density in addition to the other controls;
- separate city models, a pooled mixed model, and equal-city-weighted pooled inference using exhaustive sign assignments.

The stored result `outputs/tables/primary_v2.csv` records 27,191 units before the length floor, 19,022 after it, and **18,684 complete cases**, with 5,369 cells and 5,136 routes. The city sample sizes are Boston 6,783; Charlotte 1,339; Denver 2,429; Phoenix 3,213; Portland 2,515; and Wasatch Front 2,405.

**Path names retain research history.** `data/analysis/` and `data/processed/<city>/` use the earlier AADT-in-the-dissolve-key frame. Those files are retained for comparisons and older robustness analyses. `data/analysis__oneway/` is a separate one-way-inclusion branch. Running `code/run_city.sh` with no environment override builds the earlier frame, not the revised primary analysis.

The primary scripts named `05x`, `05y`, `05za`, `05zb`, `05zc`, and `05zd` explicitly read the AADT-free table where appropriate. Earlier scripts with words such as “primary” or “canonical” in their comments or filenames predate this revision.

## 2. Install the environment and archived inputs

Python dependencies and their resolved versions are supplied in `pyproject.toml` and `uv.lock`. With `uv` installed:

```bash
uv sync --frozen --python 3.12
mkdir -p outputs/tables outputs/models outputs/figures notes
```

The modelling tables are in the repository itself. Larger processed and raw data are release assets. Download them from this repository's Releases page, placing them in `release-assets/`. Alternatively, from a clone with the GitHub CLI available:

```bash
mkdir -p release-assets
gh release download v1.0.0 --pattern 'processed-data.tar.gz' --dir release-assets
gh release download v1.0.0 --pattern 'raw-*.tar.gz' --dir release-assets
gh release download v1.0.0 --pattern 'hpms_2024_national.zip.part*' --dir release-assets
gh release download v1.0.0 --pattern 'DATA_LICENSES.md' --dir release-assets
gh release download v1.0.0 --pattern 'CDLA-Permissive-2.0.txt' --dir release-assets
gh release download v1.0.0 --pattern 'RELEASE_ASSETS_SHA256.txt' --dir release-assets
(cd release-assets && shasum -a 256 -c RELEASE_ASSETS_SHA256.txt)
```

Extract the processed and city archives from the repository root:

```bash
tar -xzf release-assets/processed-data.tar.gz
for city in denver portland phoenix boston wasatch_front charlotte; do
  tar -xzf "release-assets/raw-${city}.tar.gz"
done
```

The archives restore the `data/processed/` and `data/raw/<city>/` paths expected by the unchanged code. Consult the release's file manifest and checksums to verify the download. Archive names refer to the deposited snapshot; downloading fresh source data instead can produce different results, particularly for OpenStreetMap.

### HPMS 2024 currency and sample-panel checks

The large original national ZIP is supplied in ordered parts. Reassemble it without changing its bytes:

```bash
cat release-assets/hpms_2024_national.zip.part01 \
    release-assets/hpms_2024_national.zip.part02 \
    release-assets/hpms_2024_national.zip.part03 \
    > release-assets/hpms_2024_national.zip
unzip -l release-assets/hpms_2024_national.zip
mkdir -p data/raw/_hpms_currency
unzip release-assets/hpms_2024_national.zip -d data/raw/_hpms_currency
```

Both `05j_hpms_currency.py` and `05q_panel_aadt.py` require the actual directory at **`data/raw/_hpms_currency/HPMS2024.gdb`**. If the ZIP has an enclosing directory, place the extracted `HPMS2024.gdb` directory at that exact path. The expected layers include `HPMS_FULL_CO_2024`, `HPMS_FULL_OR_2024`, `HPMS_FULL_WA_2024`, `HPMS_FULL_AZ_2024`, `HPMS_FULL_MA_2024`, `HPMS_FULL_NH_2024`, `HPMS_FULL_UT_2024`, `HPMS_FULL_NC_2024`, and `HPMS_FULL_SC_2024`.

The national geodatabase is unnecessary for the primary 2018 analysis. If the release asset cannot be obtained, it must be downloaded and installed manually from the HPMS 2024 National Transportation Atlas Database source; there is no automated national-2024 acquisition script in `code/01_acquire/`.

## 3. Re-estimate from the archived modelling tables

No API key or fresh network acquisition is needed for this route. Start with the primary result:

```bash
unset PIPE_VARIANT MIN_SEG_LEN_M
uv run python code/05_model/05x_primary_v2.py
```

Compare the generated `outputs/tables/primary_v2.csv` with the deposited version. The script reports its actual sample, coefficients, confidence intervals, and inferential quantities. Small numerical differences can arise from platform-dependent numerical libraries; changed sample sizes indicate a data/path/environment issue that needs investigation.

With the processed archive installed, run the principal revised companion analyses:

```bash
uv run python code/05_model/05y_comparators_v2.py
uv run python code/05_model/05za_adversarial.py
uv run python code/05_model/05zc_rq2_rq3_v2.py
uv run python code/05_model/05zd_ablation_v2.py
uv run python code/05_model/05zb_measure_diagnostics.py
```

| Script | Main output | Additional input beyond the primary pooled table |
|---|---|---|
| `05x_primary_v2.py` | `primary_v2.csv` | None for the main estimate; moderation uses the betweenness column already stored in the table. |
| `05y_comparators_v2.py` | `comparators_v2.csv` | Baseline `data/processed/<city>/cell_metrics.parquet` for all six cities. Leave `PIPE_VARIANT` unset for this documented invocation. |
| `05za_adversarial.py` | `adversarial_v2.csv` | Baseline pooled table for comparisons between unit definitions. |
| `05zc_rq2_rq3_v2.py` | `rq2_rq3_v2.csv` | Baseline and AADT-free pooled tables, including betweenness. |
| `05zd_ablation_v2.py` | `ablation_v2.csv` | `through_routes_r800.parquet` in each city's `__af_ablall`, `__af_ablnocap`, and `__af_ablnospan` processed directories. |
| `05zb_measure_diagnostics.py` | `measure_diagnostics.csv` | Raw major-network OSM GeoPackages for tag diagnostics; stored `outputs/tables/aadt_sample_panel.csv` for its panel-summary section. Missing optional inputs are reported/skipped. |

All CSV outputs above are written under `outputs/tables/`. The ablation estimator can skip absent branches, and other scripts can skip failed or inestimable models: a zero exit code alone is not evidence that every requested result was reproduced. Read the console output and check that all expected cities/branches are present.

### Matched-pair transfer and standard comparators

These scripts require explicit switches to use the AADT-free frame and 400 m floor:

```bash
PIPE_VARIANT=aadtfree MIN_SEG_LEN_M=400 \
  uv run python code/05_model/05f_psm_replication.py
PIPE_VARIANT=aadtfree MIN_SEG_LEN_M=400 \
  uv run python code/05_model/05s_standard_comparators.py
```

The first writes `psm_choi_ewing_replication.csv` despite the inherited filename; it transfers the matching procedure using an AADT outcome. It needs each city's AADT-free `cell_metrics.parquet` and analysis table. Its aggregation and complete-case rules are its own; setting the floor does not make every earlier script use `05x`'s complete-case definition.

The second writes `standard_comparators.csv`; its angular-choice calculation also needs raw OSM graphs, variant segments, and catchments. `--skip-nach` skips that calculation and therefore does **not** reproduce the complete functional-comparator result.

### Figures

```bash
uv run python code/06_figures/06d_schematic_p1p2p3.py
uv run python code/06_figures/06e_forest_and_scale.py
PIPE_VARIANT=aadtfree MIN_SEG_LEN_M=400 \
  uv run python code/06_figures/06b_paper_figures.py
PIPE_VARIANT=aadtfree \
  uv run python code/06_figures/06c_matched_pair_closeups.py
```

Run matching before the map and close-up scripts. The forest plot reads `primary_v2.csv`. The older multi-figure script also contains a legacy moderation illustration using fixed numbers; running it is not a recalculation of all statistical evidence from the revised model. The close-up script does not implement `MIN_SEG_LEN_M`; preserve the deposited images when comparing the exact submitted presentation.

## 4. Rebuild the derived analysis from archived raw data

Use this longer route when auditing how the archived source data became analysis tables. It is more computationally expensive than Section 3. The raw archive supplies the urban-area/geography, HPMS, OSM, and building inputs. The processed archive also supplies `tract_density.gpkg` and `lodes_blocks.gpkg` from ACS and LODES acquisition.

### 4.1 Earlier frame and shared controls

The earlier frame remains a dependency of the deposited betweenness transfer and the frame-comparison models. With archived raw data installed and shared controls available:

```bash
unset PIPE_VARIANT MIN_SEG_LEN_M
for city in denver portland phoenix boston wasatch_front charlotte; do
  uv run python code/02_network/02a_analysis_frame.py --city "$city"
  uv run python code/02_network/02b_permeability.py --city "$city"
  uv run python code/02_network/02d_through_routes.py --city "$city"
  uv run python code/02_network/02c_betweenness.py --city "$city"
  uv run python code/02_network/02e_cell_metrics.py --city "$city"
  uv run python code/03_conflate/03a_controls.py --city "$city"
  uv run python code/03_conflate/03b_analysis_table.py --city "$city"
done
uv run python code/03_conflate/03c_pool_cities.py
```

`02c_betweenness.py` computes distance-weighted edge betweenness on the **major-road graph**, with the configured 8,000 pivots and seed. Its cost can be substantial. Do not replace it with a smaller `--k` if comparing the deposited results. The current code's graph definition is authoritative for reproduction even where manuscript wording refers more broadly to the drive graph.

### 4.2 Revised AADT-free frame

`PIPE_VARIANT=aadtfree` changes derived path namespaces and activates the AADT-free dissolve in `02a`. Raw acquisition paths remain shared. The shared ACS and LODES layers are independent of segment boundaries, so explicitly copy them into the variant directories before assembling catchment controls:

```bash
for city in denver portland phoenix boston wasatch_front charlotte; do
  mkdir -p "data/processed/${city}__aadtfree"
  cp "data/processed/${city}/tract_density.gpkg" \
     "data/processed/${city}__aadtfree/tract_density.gpkg"
  cp "data/processed/${city}/lodes_blocks.gpkg" \
     "data/processed/${city}__aadtfree/lodes_blocks.gpkg"
  PIPE_VARIANT=aadtfree uv run python code/02_network/02a_analysis_frame.py --city "$city"
  PIPE_VARIANT=aadtfree uv run python code/02_network/02b_permeability.py --city "$city"
  PIPE_VARIANT=aadtfree uv run python code/02_network/02d_through_routes.py --city "$city"
  PIPE_VARIANT=aadtfree uv run python code/02_network/02e_cell_metrics.py --city "$city"
  PIPE_VARIANT=aadtfree uv run python code/03_conflate/03a_controls.py --city "$city"
done
uv run python code/02_network/02c2_transfer_betweenness.py --variant aadtfree
for city in denver portland phoenix boston wasatch_front charlotte; do
  PIPE_VARIANT=aadtfree uv run python code/03_conflate/03b_analysis_table.py --city "$city"
done
PIPE_VARIANT=aadtfree uv run python code/03_conflate/03c_pool_cities.py
```

The transfer script matches each revised unit's midpoint to the nearest earlier-frame unit midpoint with a nonmissing betweenness value, within 300 m. That is an approximation to direct reassignment from the OSM edges, and it is the method used by the deposited revised moderation analysis. Running `02c_betweenness.py` directly under `PIPE_VARIANT=aadtfree` is a different assignment procedure and may change moderation results. Betweenness is not a control in the principal substitutability estimate.

Stages 2 and 3 build all configured catchment radii (400, 800, 1,200, and 1,600 m). The 400 m **length floor** is subsequently applied by the revised modelling scripts; it is distinct from the catchment radius. `03c` reports absent cities but can still create a partial pooled file. Confirm that every radius required for an analysis contains all six cities.

### 4.3 Rebuild revised ablation routes

Each ablation must reuse the **AADT-free segment and catchment geometry**. Only the literal variant name `aadtfree` activates the exogenous dissolve in `02a`; running `02a` under a name such as `af_ablall` would build the earlier frame. Therefore copy the AADT-free geometry explicitly and rerun only the route search:

```bash
for city in denver portland phoenix boston wasatch_front charlotte; do
  for variant in af_ablall af_ablnocap af_ablnospan; do
    mkdir -p "data/processed/${city}__${variant}"
    cp "data/processed/${city}__aadtfree/segments.parquet" \
       "data/processed/${city}__${variant}/segments.parquet"
    cp "data/processed/${city}__aadtfree/catchments_r800.parquet" \
       "data/processed/${city}__${variant}/catchments_r800.parquet"
  done
  PIPE_VARIANT=af_ablall uv run python code/02_network/02d_through_routes.py \
    --city "$city" --radii 800 --graph all
  PIPE_VARIANT=af_ablnocap uv run python code/02_network/02d_through_routes.py \
    --city "$city" --radii 800 --detour 99
  PIPE_VARIANT=af_ablnospan uv run python code/02_network/02d_through_routes.py \
    --city "$city" --radii 800 --no-span
done
uv run python code/05_model/05zd_ablation_v2.py
```

The “no cap” branch uses the implemented detour setting of 99. The “all graph” branch permits major roads while excluding edges near the focal segment as implemented in `02d`.

## 5. Acquire inputs again from original providers

This route queries current provider endpoints and is a **new acquisition**, not guaranteed reconstruction of the deposited network snapshot. URLs, city/state identifiers, source years, and coverage choices are supplied in `config/config.yml` and `config/cities.yml`.

| Input | Source and script |
|---|---|
| Urban-area boundaries and tract geometry | Census TIGER/Line 2023 files with 2020 urban areas/tract geography; `01b_census_geography.py`. |
| Population, housing, structure vintage, vehicle availability | ACS 2020 five-year estimates; `01c_acs_density.py`. |
| Arterial/collector outcomes | FHWA HPMS 2018 per-state feature services configured in `cities.yml` / source templates; `01d_hpms_aadt.py`. |
| Local, major, and all-road graph extracts | OpenStreetMap through OSMnx/Overpass; `01a_osm_network.py --extent urban_area`. |
| Employment sectors and optional points of interest | LEHD LODES v8, 2018 workplace data with Census block geography, and OSM POIs; `01e_landuse_mix.py`. |
| Building footprints | Microsoft Global Building Footprints manifest/tiles; `01f_building_footprints.py`. |
| HPMS 2024 | National geodatabase, provided as release parts or installed manually; no `01_acquire` script downloads it. |

The ACS acquisition code requires a Census API key. Set `CENSUS_API_KEY` privately in the process environment before running `01c`; obtain your own key from the Census API service. No credential is included in this repository. The archived-table route in Section 3 does not need a key.

In a separate fresh clone/directory where you intend to acquire new inputs:

```bash
unset PIPE_VARIANT MIN_SEG_LEN_M
for city in denver portland phoenix boston wasatch_front charlotte; do
  uv run python code/01_acquire/01b_census_geography.py --city "$city"
  uv run python code/01_acquire/01c_acs_density.py --city "$city"
  uv run python code/01_acquire/01d_hpms_aadt.py --city "$city"
  uv run python code/01_acquire/01a_osm_network.py --city "$city" --extent urban_area
  uv run python code/01_acquire/01e_landuse_mix.py --city "$city"
  uv run python code/01_acquire/01f_building_footprints.py --city "$city"
done
```

Then follow Section 4. `--test` on the OSM script downloads only a small test area and cannot supply the full six-city study. Acquisition scripts cache or reuse existing files, so follow their printed messages to distinguish reuse from a download. Overpass requests and large national/state downloads may be slow or fail when services are unavailable.

`03a_controls.py` treats OSM POIs as optional, reporting missing POI density, but treats `footprints_ua.parquet`, `tract_density.gpkg`, and `lodes_blocks.gpkg` as mandatory inputs even though some of their derived variables are secondary controls. An existing footprint `.gpkg` alone does not satisfy that script's `.parquet` path. The archived input set avoids this format mismatch.

## 6. Earlier models and robustness outputs

The full code and saved output tables include analyses made before the revised primary model. They remain inspectable and can be rerun on their original frame. They should not automatically be interpreted as estimates on the revised 18,684-case sample.

With baseline raw/processed data installed and `PIPE_VARIANT` unset, principal earlier commands are:

```bash
uv run python code/05_model/05c_multicity.py --radius 800
uv run python code/05_model/05d_independent_subsample.py --radius 800
uv run python code/05_model/05e_sensitivity.py --radius 800
uv run python code/05_model/05g_ce_eligible.py --radius 800
uv run python code/05_model/05i_p1_constants.py
uv run python code/05_model/05j_hpms_currency.py --radius 800
uv run python code/05_model/05k_oneway_selection.py
uv run python code/05_model/05n_round3_models.py --radius 800
uv run python code/05_model/05q_panel_aadt.py
uv run python code/05_model/05r_aadtfree_units.py --radius 800
uv run python code/05_model/05v_boston_variance_vintage.py
uv run python code/05_model/05w_canonical_tables.py
```

`05r` compares both frames. `05j` and `05q` require HPMS 2024. `05e` and `05i` recompute route measures in memory and need the raw OSM graphs. `05n` and `05v` spatial analyses need processed segment geometries. Scripts write their corresponding CSVs into the shared output directory; save comparisons before running alternatives.

Two old pilot scripts, `05a_multilevel.py` and `05b_spatial_robustness.py`, read legacy aliases such as `data/analysis/analysis_table_r800.parquet`, rather than the current city-named paths generated by `03b`. For an explicitly Denver-only legacy rerun, those aliases can be made in the reproduction clone:

```bash
for radius in 400 800 1200 1600; do
  cp "data/analysis/analysis_table_denver_r${radius}.parquet" \
     "data/analysis/analysis_table_r${radius}.parquet"
done
uv run python code/05_model/05a_multilevel.py --city denver --radius 800 --predictor p1_any
uv run python code/05_model/05b_spatial_robustness.py --city denver
```

The `--city` option does not itself switch that legacy input alias to a different city's table. These commands document old pilot analyses; use `05x_primary_v2.py` for the revised six-city headline result.

## 7. Limits of the reproduction claim

- This is a preservation deposit of the existing research, not a code refactor or a completed independent replication. The deposited tables and source snapshots are the comparison reference.
- Several earlier robustness scripts (`05g`, `05j`, `05q`, `05v`, among others) have their own control and missing-data rules, omit the revised job-density control, or do not implement the revised length floor. Setting `PIPE_VARIANT=aadtfree` changes their input path but does not update their statistical specification. No undocumented wrapper or code modification is supplied here to imply equivalence.
- Some supplementary manuscript values are not demonstrably generated by a dedicated revised-sample script in this deposit. Retaining the saved outputs makes those values auditable, but does not establish a verified command for every number in the manuscript. The entry points and primary sample above are the clearly identifiable revised pathway.
- The main network acquisition does not pin a historical Overpass date. Reacquisition can change topology, tags, node order, and derived measures. Use the archived OSM GeoPackages for comparison with the saved analysis.
- Primary estimates are associational. Reproducing their computation does not establish causal arterial relief or observed redistribution of trips onto local roads.

Report the repository release/tag, table/frame, script, command-line arguments, environment, and any input replacements with an independent rerun. That information is necessary to distinguish an exact archived-data re-estimation from a new acquisition or methodological extension.
