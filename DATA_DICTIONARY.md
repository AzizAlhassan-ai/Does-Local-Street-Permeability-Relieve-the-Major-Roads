# Analysis data dictionary

This dictionary describes the stored analysis tables for **Does Local Street Permeability Relieve the Major Roads? Measuring Substitutability, Not Connectivity, in Six US Urban Areas**. It documents the archived implementation without changing the research, source data, or results.

## Primary table and estimation sample

The revised primary table is `data/analysis__aadtfree/analysis_pooled_r800.parquet`: **27,191 rows and 60 columns**, one row per HPMS-derived road segment at an 800 m catchment radius. It contains all stored units, including short segments and incomplete observations. It is not already restricted to the manuscript's estimation sample.

The primary loader, [`load()` in `code/05_model/05x_primary_v2.py`](code/05_model/05x_primary_v2.py), applies the following steps:

1. Retain `length_m >= 400`: **19,022 rows**.
2. Recompute the model's continuous standardized variables within each city using the population standard deviation (`ddof=0`) on the length-filtered data.
3. Remove rows missing the outcome, P1 indicator, cell, route, functional class, standardized log length, or any of the seven continuous controls: population density, job density, employment-sector entropy, centered CBD distance, its square, building vintage, and through lanes.

The resulting primary sample contains **18,684 rows, 5,369 cells, and 5,136 distinct stored route IDs**. Functional class also enters the model as a categorical control. The primary model does not require nonmissing betweenness or POI data. These counts were verified by reading the archived table and calling the existing read-only `load()` function; no model fit was needed to verify these dictionary counts. The primary model was separately re-estimated for the release; see [VERIFICATION.md](VERIFICATION.md).

| City key | Stored rows | Primary complete cases | Cells in primary sample | Distinct route IDs in primary sample |
|---|---:|---:|---:|---:|
| `boston` | 11,088 | 6,783 | 1,795 | 2,240 |
| `charlotte` | 1,805 | 1,339 | 568 | 238 |
| `denver` | 3,456 | 2,429 | 665 | 1,031 |
| `phoenix` | 4,325 | 3,213 | 1,031 | 351 |
| `portland` | 3,521 | 2,515 | 630 | 840 |
| `wasatch_front` | 2,996 | 2,405 | 680 | 436 |
| **Total** | **27,191** | **18,684** | **5,369** | **5,136** |

The segment frame merges contiguous HPMS increments along a route when functional class, through lanes, access control, ownership, and facility type agree. The `aadtfree` branch excludes AADT from these merge keys and applies a nominal 0.5 route-mile block cap. A source increment is never subdivided, and stored geometric segment lengths can exceed that cap. AADT is the route-mile-weighted mean within each merged segment. See [`02a_analysis_frame.py`](code/02_network/02a_analysis_frame.py), especially `dissolve_homogeneous()` and the `aadtfree` branch.

## Files and variants

| Directory | Role | Parquet files present | Stored pooled rows | Stored pooled columns | Radii available |
|---|---|---:|---:|---:|---|
| `data/analysis__aadtfree/` | Revised primary frame | 35 | 27,191 | 60 | 400, 800, 1,200, 1,600 m |
| `data/analysis/` | Earlier frame, retained for comparison; AADT is a merge key | 35 | 39,255 | 62 | 400, 800, 1,200, 1,600 m |
| `data/analysis__oneway/` | Sensitivity branch admitting one-way facilities and doubling their reported AADT under a balanced directional-flow assumption | 14 | 41,390 | 59 | 800 m |

These are counts of the source archive inspected for this release. In each directory, `analysis_table_<city>_r<R>.parquet` is a city-specific table, and `analysis_pooled_r<R>.parquet` combines the six cities. A filename without `_r<R>` is the canonical 800 m copy, not an additional observation set. For the primary directory, every city-specific canonical file was verified equal to its `_r800` counterpart, and `analysis_pooled.parquet` was verified equal to `analysis_pooled_r800.parquet`. Every pooled table contains six cities and has no duplicate `segment_uid` values. Do not concatenate canonical copies with radius-specific copies, or mix alternative segment frames as if they were independent observations.

`PIPE_VARIANT` selects derived-data directories through [`code/lib/paths.py`](code/lib/paths.py). The raw acquisitions are shared across variants. The revised primary loader explicitly defaults to `aadtfree`; older scripts and historical comments may use “primary” for the earlier unsuffixed frame. Use the directory and defining script to distinguish them.

The variable definitions below apply to the 60-column revised primary table. Other variants differ in schema; their additional fields are defined by their producing scripts rather than implicitly covered here.

## Spatial and source conventions

All lengths, areas, and Euclidean distances are computed in EPSG:5070. The analysis table itself has no geometry column. Segment and catchment geometries belong to `data/processed/<city>__aadtfree/`. Catchments are full buffers around segment geometry; `catch_area_km2` is not clipped to the urban-area boundary. Nodes are assigned by point inclusion, network edges by midpoint inclusion using their full length, and building footprints by centroid inclusion using their full footprint area.

Traffic comes from HPMS 2018. The configured ACS source is the 2020 five-year release (2016–2020), LODES employment is 2018, and the manuscript records an OSM extraction in July 2026. Geographic releases and exact retrieval details are recorded in `config/cities.yml`, `config/config.yml`, and `notes/data-provenance.md`. These sources are not observations from a single common year.

The code partitions OSM streets into a local set (`residential`, `living_street`, `unclassified`) and a major set. P1 and P3 use undirected local graphs; P1 records topological route availability under the implemented constraints, not observed route choice or travel time. Its endpoint attachments are nearby local nodes, not verified driveway or intersection access links.

## Identifiers and traffic variables

Sources: [frame construction](code/02_network/02a_analysis_frame.py), [HPMS acquisition and code labels](code/01_acquire/01d_hpms_aadt.py), [analysis assembly](code/03_conflate/03b_analysis_table.py), and [city pooling](code/03_conflate/03c_pool_cities.py).

| Variable | Unit or encoding | Definition |
|---|---|---|
| `segment_uid` | String identifier | Derived segment key, prefixed with `<city>` and a pipe separator in pooled files, such as `denver` + pipe + `d1`. The unprefixed key identifies the city-specific processed segment. |
| `route_id` | String identifier | HPMS route identifier retained through merging. Pooling does not add a city prefix to this field. Use `city` with it when joining external city-specific files. |
| `cell_id` | String identifier; nullable | Grid cell containing the segment midpoint. The grid has 1,609.344 m sides (one square mile before urban-area clipping); pooling adds a city prefix. Missing cells are excluded by the primary loader. |
| `aadt` | Vehicles/day | Annual average daily traffic; route-mile-weighted mean of source HPMS increments within the revised segment. |
| `log_aadt` | Natural log of vehicles/day | `ln(aadt)` after merging. |
| `aadt_per_lane` | Vehicles/day/through lane | `aadt / through_lanes`; undefined when through lanes are missing or nonpositive. |
| `f_system` | HPMS category | Retained classes: 3 = other principal arterial, 4 = minor arterial, 5 = major collector. Numeric codes are categorical, not a continuous scale. |
| `facility_type` | HPMS category | All primary-table rows have code 2, two-way roadway. One-way code 1 belongs to the separate sensitivity branch. |
| `through_lanes` | Lane count | HPMS through-lane count; one of the segment merge keys. |
| `access_control_` | HPMS category; nullable | Retained source access-control code, including observed values 0, 1, 2, and 3. The analysis creates a separate indicator equal to 1 for codes 1 or 2; see the model loader for treatment of other codes and missing values. Full source-code meanings are not reinterpreted here. |
| `ownership` | HPMS category | Road ownership code, one of the merge keys. Labels are in `OWNERSHIP_LABEL` in `01d_hpms_aadt.py`; for example 1 = state highway agency, 2 = county, 3 = town/township, 4 = city/municipal. |
| `nhs` | HPMS category; nullable | Original National Highway System source code retained using the first increment in a merged unit. Stored values include 0 through 8; do not treat this as a simple binary flag. Consult the source HPMS codebook for category meanings. |
| `length_m` | Metres | Length of the merged segment geometry in EPSG:5070. This is distinct from route-mile weights used to aggregate AADT. |
| `n_hpms_increments` | Count | Number of source HPMS records combined into the segment. |
| `speed_limit_usable` | Miles/hour; nullable | First retained HPMS speed-limit value in the merged unit when it falls in the configured inclusive 5–90 mph range; otherwise missing. |

## Generic local-network measures P3

Source: [`02b_permeability.py`](code/02_network/02b_permeability.py). An undirected simple local graph deduplicates reverse edges by unordered node pair. Node degree is computed on the whole city's local graph before catchment assignment.

| Variable | Unit | Definition |
|---|---|---|
| `local_int_density` | Intersections/km² | Number of local nodes of degree at least 3 inside the catchment divided by `catch_area_km2`. |
| `local_link_node_ratio` | Ratio; nullable | Degree-2 chains are contracted: qualifying nodes have degree 1 or at least 3; links are half the degree sum over those nodes. The stored ratio is links divided by qualifying-node count, missing if that count is zero. |
| `local_street_density` | Street km/km² | Sum of the full lengths of undirected local edges whose midpoints lie inside the catchment, divided by catchment area. |
| `local_deadend_share` | Fraction; nullable | Degree-1 local nodes divided by all local nodes inside the catchment, including degree-2 nodes in the denominator. Missing with no local nodes. |
| `local_circuity` | Ratio; nullable | Sum of assigned local-edge lengths divided by sum of their endpoint straight-line distances. Missing when the chord-distance denominator is zero. This is not the mean of per-edge ratios. |
| `local_nodes` | Count stored as float | All local-graph nodes inside the catchment, including degree-2 nodes. |
| `local_edges` | Count stored as float | Undirected local edges assigned by midpoint inclusion. |
| `no_local_network` | Boolean | True when `local_nodes` is zero; assembly treats missing node counts as zero for this flag. |

## Catchments and controls

Sources: [`03a_controls.py`](code/03_conflate/03a_controls.py), [`01c_acs_density.py`](code/01_acquire/01c_acs_density.py), [`03b_analysis_table.py`](code/03_conflate/03b_analysis_table.py), and [source settings](config/cities.yml).

The five ACS variables are area-weighted means of tract values over each buffer's intersections with available tracts. They are not values of only the midpoint tract. For each variable the weighting denominator includes only overlap pieces carrying a nonmissing value. The stored vintage is consequently an average of tract medians, not a newly computed median for all buildings in the catchment.

| Variable | Unit | Definition |
|---|---|---|
| `catch_area_km2` | km² | Full segment-buffer area, including portions outside the study urban area. |
| `pop_density_km2` | Persons/km² | Area-weighted tract population density. Tract density is ACS population (`B01003_001E`) divided by TIGER land area `ALAND`. |
| `housing_density_km2` | Housing units/km² | Area-weighted tract housing density; ACS housing units (`B25001_001E`) divided by tract land area. |
| `median_year_structure_built` | Calendar year, possibly fractional | Area-weighted mean of tract median year built (`B25035_001E`). Acquisition marks invalid years below 1900 as missing. |
| `pct_no_vehicle` | Percent, 0–100 | Area-weighted tract percentage of households without vehicles: 100 × `B08201_002E / B08201_001E`. |
| `avg_household_size` | Persons/household | Area-weighted tract average household size (`B25010_001E`). |
| `tract_overlap_km2` | km² | Total geometric catchment–tract overlap area summed during aggregation. It is not a separate completeness measure for each ACS variable. |
| `lu_entropy` | Normalized index, 0–1; nullable | Employment-sector mix proxy. Raw LODES sector counts are pooled for block representative points within the buffer, then normalized Shannon entropy is computed as `−sum(p × ln(p)) / ln(k)`, where `k` is the number of positive sectors among `CNS01`–`CNS20`. Missing for no jobs or fewer than two positive sectors. It does not measure mapped land-use area shares. |
| `jobs_total` | Jobs | Sum of LODES `C000` in blocks whose representative points fall within the catchment; unmatched catchments receive zero. |
| `n_sectors_present` | Count stored as float; nullable | Number of positive pooled sector counts. Missing when no block group is joined into the aggregation. |
| `job_density_km2` | Jobs/km² | `jobs_total / catch_area_km2`. |
| `poi_count` | Count stored as float; nullable | OSM amenity/shop/office features within the catchment, after the configured parking and street-furniture exclusions. Missing if the optional POI layer was unavailable for that city; zero means the available layer yielded no assigned features. |
| `poi_density_km2` | Features/km²; nullable | `poi_count / catch_area_km2`. |
| `n_buildings` | Count stored as float | Microsoft building footprints whose centroids fall within the catchment; zero if none are assigned. |
| `built_area_m2` | m² | Full areas of the assigned building footprints, summed without clipping footprints to the catchment boundary. |
| `built_density` | Area ratio | `built_area_m2 / (catch_area_km2 × 1,000,000)`. |
| `dist_cbd_km` | km | Euclidean distance from segment midpoint to the city-specific CBD anchor in `config/cities.yml`, measured in EPSG:5070. |
| `dist_cbd_mean_km` | km | City-table mean of `dist_cbd_km` at assembly time, repeated on each row. This mean precedes the model's length and complete-case exclusions. |
| `dist_cbd_km_c` | km | `dist_cbd_km − dist_cbd_mean_km`. |
| `dist_cbd_km_c_sq` | km² | Square of the centered CBD distance. |
| `radius_m` | Metres | Catchment buffer radius; 800 in the primary stored table. |
| `city` | String category | One of the six city keys in the inventory above. |

## Route availability P1 and access connections P2

Source: [`02d_through_routes.py`](code/02_network/02d_through_routes.py), especially `disjoint_paths()` and the record-construction block; parameters are in `through_routes` in [`config/config.yml`](config/config.yml).

The P1 search uses the undirected local subgraph induced by nodes inside the catchment. Candidate source and target nodes lie within 200 m of the segment's two endpoints. Nodes present in both attachment sets are removed from both. Greedy shortest-path enumeration retains up to five edge-disjoint qualifying routes. For an accepted route, project its local endpoints onto the segment: the gap between these projections is the **arterial-equivalent span**. The distance detour ratio is local route length divided by that span, not simply by the full segment length. Acceptance requires a ratio at most 1.5 and a span at least 0.5 of the full segment length. The implementation also uses 1.5 times full segment length as an early stopping bound.

These are stored implementation definitions. Three names deserve particular care: `p1_min_span` stores a maximum, `p2_pairs` stores independent connections, and `p1_short_segment` uses a 500 m flag threshold that differs from the revised primary model's 400 m exclusion floor.

| Variable | Unit or encoding | Definition |
|---|---|---|
| `p1_routes` | Count, 0–5 | Number of accepted routes found by greedy edge-disjoint enumeration. This is not guaranteed to be the graph's maximum possible number of such routes. |
| `p1_any` | Integer 0/1 | One when at least one accepted route was found. Stored zero values below 400 m must not be interpreted as valid untreated observations in the revised primary model; those segments are excluded. |
| `p1_min_detour` | Ratio; nullable | Minimum local-length/arterial-equivalent-span ratio among accepted routes. Missing when no route is accepted. |
| `p1_min_span` | Fraction; nullable | **Maximum**, despite the field name, accepted arterial-equivalent span divided by full segment length. Missing with no accepted route. |
| `p2_pairs` | Count | Sum over local connected components of `max(0, n − 1)`, where `n` is the number of local nodes also incident to a major edge within that component and catchment. It counts independent access connections, not all pair combinations. |
| `p2_pairs_per_km2` | Connections/km² | `p2_pairs / catch_area_km2`. |
| `p1_short_segment` | Integer 0/1 | One when segment geometry length is below the configured **500 m** diagnostic threshold. This field is not the primary sample filter. |
| `n_src_nodes` | Count | Candidate source-end local nodes after catchment restriction and removal of nodes shared by both attachment sets. |
| `n_tgt_nodes` | Count | Candidate target-end local nodes after the same restrictions. |
| `p1_best_circuity` | Ratio; nullable | Shortest accepted route length divided by straight-line distance between that route's local endpoints; missing if no accepted route or endpoint chord is at most 1 m. |
| `p1_best_n_intersections` | Count stored as float; nullable | Interior nodes traversed by the shortest accepted route, implemented as `max(0, number of route nodes − 2)`. The code does not apply a degree-at-least-3 intersection test here. |
| `p1_best_int_per_km` | Interior nodes/km; nullable | `p1_best_n_intersections` divided by shortest accepted route length in kilometres. |
| `p1_best_time_ratio` | Estimated time ratio; nullable | Estimated time along the shortest accepted distance route divided by estimated arterial travel time over its projected span. Local defaults are 40 km/h residential, 20 living street, and 48 unclassified, with a 6-second delay per interior node. Arterial defaults for classes 3/4/5 are 64/56/48 km/h. These are assumed speeds and delays, not measurements. |
| `p1q_any` | Integer 0/1 | One if the shortest accepted distance route has estimated time ratio at most 1.5. Zero otherwise, including when no route was accepted. Despite “any” in the name, the quality calculation evaluates the shortest accepted distance route rather than searching all possible paths for the fastest route. |

## Betweenness

| Variable | Unit | Definition |
|---|---|---|
| `arterial_betweenness` | Normalized centrality; nullable | Distance-weighted edge betweenness on the undirected citywide **major-road** graph, using NetworkX pivot sampling. The original frame attaches values through nearest edge-midpoint matching. The revised `aadtfree` frame receives these stored values from the nearest original-frame segment midpoint within 300 m through the transfer script. Unmatched values remain missing. This is a moderator in secondary models, not a required primary-model control. |

Defining sources are [`02c_betweenness.py`](code/02_network/02c_betweenness.py) and [`02c2_transfer_betweenness.py`](code/02_network/02c2_transfer_betweenness.py). See these files and `config/config.yml` for pivot count, random seed, original match-distance threshold, and transfer behavior. Do not infer that this field was computed on the complete local-plus-major graph from a general description of network centrality.

## Missing values and variables created by the model

Parquet nulls represent unavailable or undefined values; they are not universally zeros. Structural examples include route-quality fields without an accepted P1 route, entropy with insufficient sector representation, ratios with no denominator, and optional POI data absent for a city. Retained source codes such as `access_control_ = 0` are not automatically converted to missing.

The primary table stores raw-scale fields. The primary loader creates `p1 = float(p1_any)` and `y = log_aadt`, standardized controls ending in `_z`, `p1n_z` for route count, `p2_z` for P2, and `loglen_z` for natural-log segment length. It creates `betweenness_log = log10(arterial_betweenness + 0.00001)` and `betw_z` for secondary models. Those derived columns are not additional stored fields in the 60-column table.

The loader also creates `access_controlled = access_control_.isin([1, 2]).astype(float)`. Consequently its current implementation maps a missing source code, as well as codes outside 1 and 2, to zero. This dictionary records that behavior; it does not impute or recode the archived data.

