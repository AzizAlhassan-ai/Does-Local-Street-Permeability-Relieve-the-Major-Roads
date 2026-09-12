# Data provenance

Machine-appended by `code/lib/provenance.py`. One row per acquisition.
Do not edit by hand — re-run the acquisition script instead.

| retrieved (UTC) | city | layer | source URL | rows | bytes | sha256 (first 16) | file |
|---|---|---|---|---|---|---|---|
| 2026-07-30 10:41 | denver | osm_network_test_all | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 935 | 442368 | 3be3b5c8bb83c678 | `data/raw/denver/osm/network_test_all.gpkg` |
| 2026-07-30 10:41 | denver | osm_network_test_major | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 383 | 217088 | e01a3e03aced5c14 | `data/raw/denver/osm/network_test_major.gpkg` |
| 2026-07-30 10:41 | denver | osm_network_test_local | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 552 | 266240 | e0c39ddb6a6c651e | `data/raw/denver/osm/network_test_local.gpkg` |
| 2026-07-30 10:42 | denver | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 315392 | f64d07bc7ee3ed98 | `data/raw/denver/census/urban_area.gpkg` |
| 2026-07-30 10:42 | denver | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_08_tract.zip | 661 | 2686976 | 25ad507367316a81 | `data/raw/denver/census/tracts.gpkg` |
| 2026-07-30 11:20 | denver | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 661 | 2748416 | 43fc3a2518ba188c | `data/processed/denver/tract_density.gpkg` |
| 2026-07-30 11:21 | denver | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 661 | 2752512 | 6d6d3d073f3c2d62 | `data/processed/denver/tract_density.gpkg` |
| 2026-07-30 11:32 | denver | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/co/wac/co_wac_S000_JT00_2018.csv.gz | 18418 | 2686976 | b387fd852193f799 | `data/processed/denver/lodes_blocks.gpkg` |
| 2026-07-30 11:33 | denver | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Colorado_2018_PR/FeatureServer/0 | 13839 | 5435392 | bf06479606e8f12f | `data/raw/denver/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 11:33 | denver | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Colorado_2018_PR/FeatureServer/0 | 10267 | 3780608 | e25a1151dd3bc2d7 | `data/raw/denver/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 11:34 | denver | building_footprints | https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv | 780469 | 231124992 | cfcb77cf48debffd | `data/raw/denver/building_footprints/footprints_ua.gpkg` |
| 2026-07-30 11:35 | denver | osm_poi | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 99877 | 12505088 | 793179873b7d4fc8 | `data/raw/denver/osm_poi/pois.gpkg` |
| 2026-07-30 11:35 | denver | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/co/wac/co_wac_S000_JT00_2018.csv.gz | 18418 | 2686976 | 60a395d8f1e080d2 | `data/processed/denver/lodes_blocks.gpkg` |
| 2026-07-30 11:35 | denver | osm_poi | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 99877 | 12505088 | 793179873b7d4fc8 | `data/raw/denver/osm_poi/pois.gpkg` |
| 2026-07-30 11:35 | denver | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Colorado_2018_PR/FeatureServer/0 | 13839 | 5435392 | 969ba009699a173a | `data/raw/denver/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 11:35 | denver | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Colorado_2018_PR/FeatureServer/0 | 10267 | 3780608 | 0ee1d37b6b623ad2 | `data/raw/denver/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 11:36 | denver | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/co/wac/co_wac_S000_JT00_2018.csv.gz | 18418 | 2686976 | 26316c64a9769cc5 | `data/processed/denver/lodes_blocks.gpkg` |
| 2026-07-30 11:36 | denver | osm_poi | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 99877 | 12505088 | 793179873b7d4fc8 | `data/raw/denver/osm_poi/pois.gpkg` |
| 2026-07-30 11:36 | denver | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Colorado_2018_PR/FeatureServer/0 | 13839 | 5435392 | 8ec7f5de1c78fc81 | `data/raw/denver/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 11:36 | denver | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Colorado_2018_PR/FeatureServer/0 | 10267 | 3780608 | f51b87edd4c4eeb9 | `data/raw/denver/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 11:36 | denver | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Colorado_2018_PR/FeatureServer/0 | 13839 | 5435392 | 30d005cad2c28a14 | `data/raw/denver/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 11:36 | denver | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Colorado_2018_PR/FeatureServer/0 | 10267 | 3780608 | 16e46b3e1613685a | `data/raw/denver/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 11:36 | denver | building_footprints | https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv | 780469 | 231124992 | fc71be35bee8fac7 | `data/raw/denver/building_footprints/footprints_ua.gpkg` |
| 2026-07-30 11:52 | denver | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Colorado_2018_PR/FeatureServer/0 | 13839 | 5472256 | 07e0cbff3a1a365a | `data/raw/denver/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 11:52 | denver | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Colorado_2018_PR/FeatureServer/0 | 10267 | 3801088 | 72038ce3ee6fb8d3 | `data/raw/denver/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 11:54 | denver | osm_network_urban_area_all | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 218479 | 80420864 | 8ae6ccd77b6a9456 | `data/raw/denver/osm/network_urban_area_all.gpkg` |
| 2026-07-30 11:54 | denver | osm_network_urban_area_major | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 53187 | 17784832 | 9a73d9015746a302 | `data/raw/denver/osm/network_urban_area_major.gpkg` |
| 2026-07-30 11:54 | denver | osm_network_urban_area_local | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 165221 | 51818496 | 2343e5571d80028c | `data/raw/denver/osm/network_urban_area_local.gpkg` |
| 2026-07-30 11:54 | denver | catchments_r400 | derived: 01d + 01b | 9490 | 12446961 | 45016e7452673082 | `data/processed/denver/catchments_r400.parquet` |
| 2026-07-30 11:54 | denver | catchments_r800 | derived: 01d + 01b | 9490 | 12287246 | 302264db438e7e28 | `data/processed/denver/catchments_r800.parquet` |
| 2026-07-30 11:54 | denver | catchments_r1200 | derived: 01d + 01b | 9490 | 12196246 | 64c71d2be3270927 | `data/processed/denver/catchments_r1200.parquet` |
| 2026-07-30 11:54 | denver | catchments_r1600 | derived: 01d + 01b | 9490 | 12127938 | a9afc707d761a49c | `data/processed/denver/catchments_r1600.parquet` |
| 2026-07-30 11:54 | denver | analysis_segments | derived: 01d | 9490 | 1558114 | 8188ea2ce84c8002 | `data/processed/denver/segments.parquet` |
| 2026-07-30 11:54 | denver | grid_1mi2 | derived: 01b | 844 | 46040 | 73a91f7e223b7ea8 | `data/processed/denver/grid.parquet` |
| 2026-07-30 11:55 | denver | permeability_r400 | derived: 01a local subgraph + 02a catchments | 9490 | 793239 | 27e1ee78d338ff66 | `data/processed/denver/permeability_r400.parquet` |
| 2026-07-30 11:55 | denver | permeability_r800 | derived: 01a local subgraph + 02a catchments | 9490 | 852787 | aecdb02fe9519cf6 | `data/processed/denver/permeability_r800.parquet` |
| 2026-07-30 11:55 | denver | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 9490 | 909523 | b0303583c5a5e66c | `data/processed/denver/permeability_r1200.parquet` |
| 2026-07-30 11:55 | denver | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 9490 | 939475 | 918fc295393bcb5e | `data/processed/denver/permeability_r1600.parquet` |
| 2026-07-30 11:59 | denver | segment_betweenness | derived: 01a major subgraph | 9490 | 221043 | 05b4f811a9d35734 | `data/processed/denver/segment_betweenness.parquet` |
| 2026-07-30 12:16 | denver | segment_betweenness | derived: 01a major subgraph | 9490 | 223718 | 5b23605987ae00b1 | `data/processed/denver/segment_betweenness.parquet` |
| 2026-07-30 12:50 | denver | catchments_r400 | derived: 01d + 01b | 2964 | 5253854 | 2ed53108246be13e | `data/processed/denver/catchments_r400.parquet` |
| 2026-07-30 12:50 | denver | catchments_r800 | derived: 01d + 01b | 2964 | 5056698 | e5ce79d698aa8bcf | `data/processed/denver/catchments_r800.parquet` |
| 2026-07-30 12:50 | denver | catchments_r1200 | derived: 01d + 01b | 2964 | 4928656 | a21f1703d5880a8c | `data/processed/denver/catchments_r1200.parquet` |
| 2026-07-30 12:50 | denver | catchments_r1600 | derived: 01d + 01b | 2964 | 4836320 | d83724ea2ef570aa | `data/processed/denver/catchments_r1600.parquet` |
| 2026-07-30 12:50 | denver | analysis_segments | derived: 01d | 2964 | 1161145 | 651e358820442e65 | `data/processed/denver/segments.parquet` |
| 2026-07-30 12:50 | denver | grid_1mi2 | derived: 01b | 844 | 46040 | 73a91f7e223b7ea8 | `data/processed/denver/grid.parquet` |
| 2026-07-30 12:50 | denver | permeability_r400 | derived: 01a local subgraph + 02a catchments | 2964 | 272371 | 4883f65460b3a103 | `data/processed/denver/permeability_r400.parquet` |
| 2026-07-30 12:50 | denver | permeability_r800 | derived: 01a local subgraph + 02a catchments | 2964 | 295222 | ef40399a75ebba00 | `data/processed/denver/permeability_r800.parquet` |
| 2026-07-30 12:50 | denver | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 2964 | 308621 | 8cbe9277239e7632 | `data/processed/denver/permeability_r1200.parquet` |
| 2026-07-30 12:50 | denver | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 2964 | 315581 | 4ba856a14bbcc5b5 | `data/processed/denver/permeability_r1600.parquet` |
| 2026-07-30 13:02 | denver | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2964 | 457031 | b5fb4257453c1bc5 | `data/processed/denver/controls_r800.parquet` |
| 2026-07-30 13:02 | denver | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2964 | 445619 | 4e35120b7ffccb48 | `data/processed/denver/controls_r400.parquet` |
| 2026-07-30 13:02 | denver | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2964 | 457031 | b5fb4257453c1bc5 | `data/processed/denver/controls_r800.parquet` |
| 2026-07-30 13:02 | denver | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2964 | 461737 | 1b583e0a652eac76 | `data/processed/denver/controls_r1200.parquet` |
| 2026-07-30 13:02 | denver | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2964 | 464257 | da4480a3c615c16d | `data/processed/denver/controls_r1600.parquet` |
| 2026-07-30 13:08 | denver | segment_betweenness | derived: 01a major subgraph | 2964 | 74424 | 3e3164a032cb0af3 | `data/processed/denver/segment_betweenness.parquet` |
| 2026-07-30 13:08 | denver | analysis_table_r400 | derived: 02a/02b/02c + 03a | 2964 | 689743 | 4161ec466494df8f | `data/analysis/analysis_table_r400.parquet` |
| 2026-07-30 13:08 | denver | analysis_table_r800 | derived: 02a/02b/02c + 03a | 2964 | 721758 | 64c71d1bd5550e45 | `data/analysis/analysis_table_r800.parquet` |
| 2026-07-30 13:08 | denver | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 2964 | 738164 | a43427124ff59219 | `data/analysis/analysis_table_r1200.parquet` |
| 2026-07-30 13:08 | denver | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 2964 | 746008 | 7c9b40a1a751b8a4 | `data/analysis/analysis_table_r1600.parquet` |
| 2026-07-30 13:09 | denver | analysis_table_r400 | derived: 02a/02b/02c + 03a | 2964 | 719188 | 806b3eeb1551379c | `data/analysis/analysis_table_r400.parquet` |
| 2026-07-30 13:09 | denver | analysis_table_r800 | derived: 02a/02b/02c + 03a | 2964 | 751203 | daf5b953d4b0f66f | `data/analysis/analysis_table_r800.parquet` |
| 2026-07-30 13:09 | denver | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 2964 | 767609 | 9f782b0e9f7a8d7c | `data/analysis/analysis_table_r1200.parquet` |
| 2026-07-30 13:09 | denver | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 2964 | 775453 | 86d805dd7e998d71 | `data/analysis/analysis_table_r1600.parquet` |
| 2026-07-30 13:09 | denver | analysis_table_r400 | derived: 02a/02b/02c + 03a | 2964 | 719188 | 806b3eeb1551379c | `data/analysis/analysis_table_r400.parquet` |
| 2026-07-30 13:09 | denver | analysis_table_r800 | derived: 02a/02b/02c + 03a | 2964 | 751203 | daf5b953d4b0f66f | `data/analysis/analysis_table_r800.parquet` |
| 2026-07-30 13:09 | denver | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 2964 | 767609 | 9f782b0e9f7a8d7c | `data/analysis/analysis_table_r1200.parquet` |
| 2026-07-30 13:09 | denver | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 2964 | 775453 | 86d805dd7e998d71 | `data/analysis/analysis_table_r1600.parquet` |
| 2026-07-30 13:51 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 52346 | 2da87d3941f202c5 | `data/processed/denver/through_routes_r800.parquet` |
| 2026-07-30 13:52 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 100500 | 38cbbd26313a11f6 | `data/processed/denver/through_routes_r800.parquet` |
| 2026-07-30 13:53 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 101243 | 0beaf6eec00b07ce | `data/processed/denver/through_routes_r800.parquet` |
| 2026-07-30 13:53 | denver | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 98495 | 3e478af2fb2adb66 | `data/processed/denver/through_routes_r400.parquet` |
| 2026-07-30 13:53 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 101243 | 0beaf6eec00b07ce | `data/processed/denver/through_routes_r800.parquet` |
| 2026-07-30 13:53 | denver | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 102280 | 2813455d55e8abcd | `data/processed/denver/through_routes_r1200.parquet` |
| 2026-07-30 13:53 | denver | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 102763 | 92819274cd664359 | `data/processed/denver/through_routes_r1600.parquet` |
| 2026-07-30 13:54 | denver | analysis_table_r400 | derived: 02a/02b/02c + 03a | 2964 | 770441 | 7f4bd20311a04a8d | `data/analysis/analysis_table_r400.parquet` |
| 2026-07-30 13:54 | denver | analysis_table_r800 | derived: 02a/02b/02c + 03a | 2964 | 805204 | 594e9a5b52d4018b | `data/analysis/analysis_table_r800.parquet` |
| 2026-07-30 13:54 | denver | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 2964 | 822647 | 3453a04d3720e1f3 | `data/analysis/analysis_table_r1200.parquet` |
| 2026-07-30 13:54 | denver | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 2964 | 830974 | 62e7fc76d5bb2956 | `data/analysis/analysis_table_r1600.parquet` |
| 2026-07-30 14:40 | portland | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 434176 | 3af1e1b1ae0aac9c | `data/raw/portland/census/urban_area.gpkg` |
| 2026-07-30 14:40 | portland | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_53_tract.zip | 503 | 2625536 | 58e90c27353961ae | `data/raw/portland/census/tracts.gpkg` |
| 2026-07-30 16:15 | portland | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 434176 | e866346bf27bec2c | `data/raw/portland/census/urban_area.gpkg` |
| 2026-07-30 16:15 | portland | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_53_tract.zip | 503 | 2625536 | 73e06df6dc026b10 | `data/raw/portland/census/tracts.gpkg` |
| 2026-07-30 16:15 | phoenix | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 417792 | 57a6ebf7939225b4 | `data/raw/phoenix/census/urban_area.gpkg` |
| 2026-07-30 16:15 | phoenix | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_04_tract.zip | 954 | 2830336 | c9fe57350cf455ea | `data/raw/phoenix/census/tracts.gpkg` |
| 2026-07-30 16:15 | boston | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 1388544 | 3ef932dfbcbd8460 | `data/raw/boston/census/urban_area.gpkg` |
| 2026-07-30 16:15 | boston | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_33_tract.zip | 1088 | 5201920 | 176eeb7a13a31e79 | `data/raw/boston/census/tracts.gpkg` |
| 2026-07-30 16:16 | phoenix | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 417792 | 4e131399530e4438 | `data/raw/phoenix/census/urban_area.gpkg` |
| 2026-07-30 16:16 | phoenix | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_04_tract.zip | 954 | 2830336 | 62156d41bf5a4bd1 | `data/raw/phoenix/census/tracts.gpkg` |
| 2026-07-30 16:16 | boston | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 1388544 | 0bc76db7a857a14c | `data/raw/boston/census/urban_area.gpkg` |
| 2026-07-30 16:16 | boston | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_33_tract.zip | 1088 | 5201920 | 9661dd19475ac1e9 | `data/raw/boston/census/tracts.gpkg` |
| 2026-07-30 16:16 | portland | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 434176 | bb3f8a9c04f0ae32 | `data/raw/portland/census/urban_area.gpkg` |
| 2026-07-30 16:16 | portland | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_53_tract.zip | 503 | 2625536 | 9c11fa8a631a61dd | `data/raw/portland/census/tracts.gpkg` |
| 2026-07-30 16:16 | phoenix | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 954 | 2871296 | 298e1d5d54b2fc38 | `data/processed/phoenix/tract_density.gpkg` |
| 2026-07-30 16:16 | boston | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 1088 | 5251072 | 9d7c0293c9b1dcbf | `data/processed/boston/tract_density.gpkg` |
| 2026-07-30 16:16 | portland | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 503 | 2654208 | 607fbe1d59dc9d50 | `data/processed/portland/tract_density.gpkg` |
| 2026-07-30 16:21 | phoenix | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 417792 | 3206b5a37d41c291 | `data/raw/phoenix/census/urban_area.gpkg` |
| 2026-07-30 16:21 | phoenix | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_04_tract.zip | 954 | 2830336 | a72d3755e8aad776 | `data/raw/phoenix/census/tracts.gpkg` |
| 2026-07-30 16:21 | portland | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 434176 | 9240d823d96a27f6 | `data/raw/portland/census/urban_area.gpkg` |
| 2026-07-30 16:21 | portland | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_53_tract.zip | 503 | 2625536 | 37f38767271e5ca5 | `data/raw/portland/census/tracts.gpkg` |
| 2026-07-30 16:21 | boston | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 1388544 | 8109ce13f3b5a046 | `data/raw/boston/census/urban_area.gpkg` |
| 2026-07-30 16:21 | boston | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_33_tract.zip | 1088 | 5201920 | 112a69b4fabebbaf | `data/raw/boston/census/tracts.gpkg` |
| 2026-07-30 16:21 | phoenix | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 954 | 2871296 | e62ca81a7c802735 | `data/processed/phoenix/tract_density.gpkg` |
| 2026-07-30 16:21 | boston | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 1088 | 5251072 | 8d9c07543277514d | `data/processed/boston/tract_density.gpkg` |
| 2026-07-30 16:21 | portland | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 503 | 2654208 | a4f9240a445aef80 | `data/processed/portland/tract_density.gpkg` |
| 2026-07-30 16:28 | phoenix | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 417792 | 89145418d6b84ecf | `data/raw/phoenix/census/urban_area.gpkg` |
| 2026-07-30 16:28 | phoenix | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_04_tract.zip | 954 | 2830336 | 4b0d2aa0b56a8386 | `data/raw/phoenix/census/tracts.gpkg` |
| 2026-07-30 16:28 | boston | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 1388544 | b18e6ff246dbb6a0 | `data/raw/boston/census/urban_area.gpkg` |
| 2026-07-30 16:28 | boston | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_33_tract.zip | 1088 | 5201920 | 9cbbafb9c43d9e2a | `data/raw/boston/census/tracts.gpkg` |
| 2026-07-30 16:28 | portland | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 434176 | a2cf4a73cfba25ec | `data/raw/portland/census/urban_area.gpkg` |
| 2026-07-30 16:28 | portland | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_53_tract.zip | 503 | 2625536 | 341cb81eb2c6a1e0 | `data/raw/portland/census/tracts.gpkg` |
| 2026-07-30 16:28 | phoenix | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 954 | 2871296 | 3c9c7fafb9eb3d88 | `data/processed/phoenix/tract_density.gpkg` |
| 2026-07-30 16:28 | boston | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 1088 | 5251072 | d1e158766844ced9 | `data/processed/boston/tract_density.gpkg` |
| 2026-07-30 16:28 | portland | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 503 | 2654208 | 8f26b23533e4f1ce | `data/processed/portland/tract_density.gpkg` |
| 2026-07-30 16:28 | phoenix | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Arizona_2018_PR/FeatureServer/0 | 20902 | 6828032 | 220b9d3034ef9020 | `data/raw/phoenix/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 16:28 | phoenix | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Arizona_2018_PR/FeatureServer/0 | 11219 | 4218880 | 2e0f324c0e930e5f | `data/raw/phoenix/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 16:32 | phoenix | osm_network_urban_area_all | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 314498 | 110936064 | 90b4bb0f53234f67 | `data/raw/phoenix/osm/network_urban_area_all.gpkg` |
| 2026-07-30 16:32 | phoenix | osm_network_urban_area_major | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 70974 | 22388736 | c53a52a28dc8cfd3 | `data/raw/phoenix/osm/network_urban_area_major.gpkg` |
| 2026-07-30 16:32 | phoenix | osm_network_urban_area_local | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 243509 | 72499200 | 8a6704ccd4bd3548 | `data/raw/phoenix/osm/network_urban_area_local.gpkg` |
| 2026-07-30 16:38 | phoenix | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 417792 | deccce43d66d0965 | `data/raw/phoenix/census/urban_area.gpkg` |
| 2026-07-30 16:38 | phoenix | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_04_tract.zip | 954 | 2830336 | 9082ee4a22bc6de5 | `data/raw/phoenix/census/tracts.gpkg` |
| 2026-07-30 16:38 | portland | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 434176 | 1ffb8c8096b55cff | `data/raw/portland/census/urban_area.gpkg` |
| 2026-07-30 16:38 | portland | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_53_tract.zip | 503 | 2625536 | be0f5a6376c29137 | `data/raw/portland/census/tracts.gpkg` |
| 2026-07-30 16:38 | boston | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 1388544 | 4dab2bf3eda1822e | `data/raw/boston/census/urban_area.gpkg` |
| 2026-07-30 16:38 | boston | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_33_tract.zip | 1088 | 5201920 | 58d11ab391d72c5b | `data/raw/boston/census/tracts.gpkg` |
| 2026-07-30 16:38 | phoenix | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 954 | 2871296 | 89a484079f439189 | `data/processed/phoenix/tract_density.gpkg` |
| 2026-07-30 16:38 | boston | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 1088 | 5251072 | 14508407f5d7df3c | `data/processed/boston/tract_density.gpkg` |
| 2026-07-30 16:38 | portland | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 503 | 2654208 | 24881ec58d55c304 | `data/processed/portland/tract_density.gpkg` |
| 2026-07-30 16:39 | phoenix | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Arizona_2018_PR/FeatureServer/0 | 20902 | 6975488 | c1d4cbab3033e994 | `data/raw/phoenix/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 16:39 | phoenix | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Arizona_2018_PR/FeatureServer/0 | 11219 | 4296704 | 51a1f5264ab6dc02 | `data/raw/phoenix/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 16:39 | phoenix | osm_network_urban_area_all | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 314498 | 110936064 | 969856bfc867593f | `data/raw/phoenix/osm/network_urban_area_all.gpkg` |
| 2026-07-30 16:39 | phoenix | osm_network_urban_area_major | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 70974 | 22388736 | 4c45ffa601b42655 | `data/raw/phoenix/osm/network_urban_area_major.gpkg` |
| 2026-07-30 16:39 | phoenix | osm_network_urban_area_local | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 243509 | 72499200 | 60426a3d1485e19e | `data/raw/phoenix/osm/network_urban_area_local.gpkg` |
| 2026-07-30 16:40 | phoenix | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/az/wac/az_wac_S000_JT00_2018.csv.gz | 19099 | 2752512 | f1004fd1f6a2417a | `data/processed/phoenix/lodes_blocks.gpkg` |
| 2026-07-30 16:48 | phoenix | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 417792 | a703eef50a16ac51 | `data/raw/phoenix/census/urban_area.gpkg` |
| 2026-07-30 16:48 | phoenix | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_04_tract.zip | 954 | 2830336 | 76f25175649dc384 | `data/raw/phoenix/census/tracts.gpkg` |
| 2026-07-30 16:48 | boston | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 1388544 | 7c66ad38aa305b23 | `data/raw/boston/census/urban_area.gpkg` |
| 2026-07-30 16:48 | boston | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_33_tract.zip | 1088 | 5201920 | 89e3334981012e23 | `data/raw/boston/census/tracts.gpkg` |
| 2026-07-30 16:48 | portland | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 434176 | 0fe65eebffd4eafc | `data/raw/portland/census/urban_area.gpkg` |
| 2026-07-30 16:48 | portland | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_53_tract.zip | 503 | 2625536 | e1e8d337bb26d9f0 | `data/raw/portland/census/tracts.gpkg` |
| 2026-07-30 16:49 | phoenix | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 954 | 2871296 | cc9cd15ccfee2258 | `data/processed/phoenix/tract_density.gpkg` |
| 2026-07-30 16:49 | boston | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 1088 | 5251072 | 454841e1331969a7 | `data/processed/boston/tract_density.gpkg` |
| 2026-07-30 16:49 | portland | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 503 | 2654208 | 0fe94f865a4eb16e | `data/processed/portland/tract_density.gpkg` |
| 2026-07-30 16:49 | phoenix | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Arizona_2018_PR/FeatureServer/0 | 20902 | 6975488 | 00d3f80b6ad61dc6 | `data/raw/phoenix/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 16:49 | phoenix | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Arizona_2018_PR/FeatureServer/0 | 11219 | 4296704 | 863daa83182bf3e3 | `data/raw/phoenix/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 16:50 | phoenix | osm_network_urban_area_all | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 314498 | 110936064 | 4fd8e4f0932b11b0 | `data/raw/phoenix/osm/network_urban_area_all.gpkg` |
| 2026-07-30 16:50 | phoenix | osm_network_urban_area_major | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 70974 | 22388736 | 52746710b5c9af75 | `data/raw/phoenix/osm/network_urban_area_major.gpkg` |
| 2026-07-30 16:50 | phoenix | osm_network_urban_area_local | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 243509 | 72499200 | fcceb6d4e367ce3f | `data/raw/phoenix/osm/network_urban_area_local.gpkg` |
| 2026-07-30 16:50 | phoenix | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/az/wac/az_wac_S000_JT00_2018.csv.gz | 19099 | 2752512 | ed2b01670b71dd62 | `data/processed/phoenix/lodes_blocks.gpkg` |
| 2026-07-30 16:54 | boston | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Massachusetts_2018_PR/FeatureServer/0 | 62350 | 21925888 | 7e6afadfc56b705f | `data/raw/boston/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 16:54 | boston | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Massachusetts_2018_PR/FeatureServer/0 | 47137 | 18006016 | adb82570a12c3826 | `data/raw/boston/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 16:57 | boston | osm_network_urban_area_all | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 330142 | 132001792 | 30540e764b8bdc8c | `data/raw/boston/osm/network_urban_area_all.gpkg` |
| 2026-07-30 16:57 | boston | osm_network_urban_area_major | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 108824 | 38035456 | 84a554c8644dfde9 | `data/raw/boston/osm/network_urban_area_major.gpkg` |
| 2026-07-30 16:57 | boston | osm_network_urban_area_local | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 221166 | 77213696 | 94ca0c820debadbb | `data/raw/boston/osm/network_urban_area_local.gpkg` |
| 2026-07-30 16:58 | boston | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/ma/wac/ma_wac_S000_JT00_2018.csv.gz | 27628 | 4001792 | bad0b5ab271da443 | `data/processed/boston/lodes_blocks.gpkg` |
| 2026-07-30 16:59 | phoenix | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 417792 | 191a0e3750157306 | `data/raw/phoenix/census/urban_area.gpkg` |
| 2026-07-30 16:59 | phoenix | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_04_tract.zip | 954 | 2830336 | 1adbcd19d866eb72 | `data/raw/phoenix/census/tracts.gpkg` |
| 2026-07-30 16:59 | portland | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 434176 | ac0e306d353288b4 | `data/raw/portland/census/urban_area.gpkg` |
| 2026-07-30 16:59 | portland | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_53_tract.zip | 503 | 2625536 | 6d1c3809e97171c6 | `data/raw/portland/census/tracts.gpkg` |
| 2026-07-30 16:59 | boston | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 1388544 | 0f4fe5fc986d0027 | `data/raw/boston/census/urban_area.gpkg` |
| 2026-07-30 16:59 | boston | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_33_tract.zip | 1088 | 5201920 | fa1362ff42d38d3d | `data/raw/boston/census/tracts.gpkg` |
| 2026-07-30 16:59 | phoenix | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 954 | 2871296 | 10cf5be78c1ea411 | `data/processed/phoenix/tract_density.gpkg` |
| 2026-07-30 16:59 | boston | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 1088 | 5251072 | 6999db3ec6d29c2d | `data/processed/boston/tract_density.gpkg` |
| 2026-07-30 16:59 | portland | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 503 | 2654208 | e7616e6c28c24cd2 | `data/processed/portland/tract_density.gpkg` |
| 2026-07-30 16:59 | phoenix | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Arizona_2018_PR/FeatureServer/0 | 20902 | 6975488 | 3d35fe316aedeb69 | `data/raw/phoenix/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 16:59 | phoenix | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Arizona_2018_PR/FeatureServer/0 | 11219 | 4296704 | 3012b3c93c1f8164 | `data/raw/phoenix/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 16:59 | portland | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Oregon_2018_PR/FeatureServer/0 | 11836 | 5001216 | dac70d41c4648092 | `data/raw/portland/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 16:59 | portland | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Oregon_2018_PR/FeatureServer/0 | 8199 | 3723264 | 3b6620be22b3bce9 | `data/raw/portland/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 17:00 | phoenix | osm_network_urban_area_all | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 314498 | 110936064 | 4939cb1021230ef8 | `data/raw/phoenix/osm/network_urban_area_all.gpkg` |
| 2026-07-30 17:00 | phoenix | osm_network_urban_area_major | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 70974 | 22388736 | 1704a527006a3807 | `data/raw/phoenix/osm/network_urban_area_major.gpkg` |
| 2026-07-30 17:00 | phoenix | osm_network_urban_area_local | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 243509 | 72499200 | 8e32138daebd3392 | `data/raw/phoenix/osm/network_urban_area_local.gpkg` |
| 2026-07-30 17:00 | phoenix | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/az/wac/az_wac_S000_JT00_2018.csv.gz | 19099 | 2752512 | 6d4d6d5b5cb2f159 | `data/processed/phoenix/lodes_blocks.gpkg` |
| 2026-07-30 17:01 | portland | osm_network_urban_area_all | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 182406 | 66293760 | 555cce77a7aa62aa | `data/raw/portland/osm/network_urban_area_all.gpkg` |
| 2026-07-30 17:01 | portland | osm_network_urban_area_major | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 43751 | 15036416 | 4cf9480c143d4fa9 | `data/raw/portland/osm/network_urban_area_major.gpkg` |
| 2026-07-30 17:01 | portland | osm_network_urban_area_local | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 138598 | 42180608 | d2c1fa6de2312da4 | `data/raw/portland/osm/network_urban_area_local.gpkg` |
| 2026-07-30 17:02 | portland | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/or/wac/or_wac_S000_JT00_2018.csv.gz | 14035 | 2052096 | 559511a4c21f4d95 | `data/processed/portland/lodes_blocks.gpkg` |
| 2026-07-30 17:02 | boston | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Massachusetts_2018_PR/FeatureServer/0 | 62350 | 22114304 | 36dec81a6243fb3b | `data/raw/boston/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 17:02 | boston | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Massachusetts_2018_PR/FeatureServer/0 | 47137 | 18120704 | 58e392699751e28f | `data/raw/boston/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 17:04 | boston | osm_network_urban_area_all | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 330142 | 132001792 | e82fbf64a5565813 | `data/raw/boston/osm/network_urban_area_all.gpkg` |
| 2026-07-30 17:04 | boston | osm_network_urban_area_major | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 108824 | 38035456 | fea1cfdbc12f7ae7 | `data/raw/boston/osm/network_urban_area_major.gpkg` |
| 2026-07-30 17:04 | boston | osm_network_urban_area_local | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 221166 | 77213696 | c9b4caa82bb969e1 | `data/raw/boston/osm/network_urban_area_local.gpkg` |
| 2026-07-30 17:05 | portland | osm_poi | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 57202 | 7282688 | 7ef23feb6bcdffd9 | `data/raw/portland/osm_poi/pois.gpkg` |
| 2026-07-30 17:05 | boston | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/ma/wac/ma_wac_S000_JT00_2018.csv.gz | 27628 | 4001792 | 633e9acbe66d6779 | `data/processed/boston/lodes_blocks.gpkg` |
| 2026-07-30 17:07 | portland | building_footprints | https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv | 687342 | 80947344 | 274bf762a44fd095 | `data/raw/portland/building_footprints/footprints_ua.parquet` |
| 2026-07-30 17:07 | portland | catchments_r400 | derived: 01d + 01b | 3478 | 6241433 | d13fa850f910eb24 | `data/processed/portland/catchments_r400.parquet` |
| 2026-07-30 17:07 | portland | catchments_r800 | derived: 01d + 01b | 3478 | 5880048 | ea1b273488f7c104 | `data/processed/portland/catchments_r800.parquet` |
| 2026-07-30 17:07 | portland | catchments_r1200 | derived: 01d + 01b | 3478 | 5682144 | 062231b8476dc8a0 | `data/processed/portland/catchments_r1200.parquet` |
| 2026-07-30 17:07 | portland | catchments_r1600 | derived: 01d + 01b | 3478 | 5552875 | 28bfdc27f341faca | `data/processed/portland/catchments_r1600.parquet` |
| 2026-07-30 17:07 | portland | analysis_segments | derived: 01d | 3478 | 1430054 | 8d6397630d2a8678 | `data/processed/portland/segments.parquet` |
| 2026-07-30 17:07 | portland | grid_1mi2 | derived: 01b | 740 | 42569 | eb8fe4278a3dabc9 | `data/processed/portland/grid.parquet` |
| 2026-07-30 17:07 | portland | permeability_r400 | derived: 01a local subgraph + 02a catchments | 3478 | 309714 | 7cc208f64a41dda1 | `data/processed/portland/permeability_r400.parquet` |
| 2026-07-30 17:07 | portland | permeability_r800 | derived: 01a local subgraph + 02a catchments | 3478 | 336659 | 630575b5ec28b0a3 | `data/processed/portland/permeability_r800.parquet` |
| 2026-07-30 17:07 | portland | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 3478 | 352338 | 05a20883318e22b5 | `data/processed/portland/permeability_r1200.parquet` |
| 2026-07-30 17:07 | portland | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 3478 | 362106 | 628be1cd79bad1c3 | `data/processed/portland/permeability_r1600.parquet` |
| 2026-07-30 17:08 | portland | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 3478 | 111719 | 43fcb66c6aa1efb4 | `data/processed/portland/through_routes_r400.parquet` |
| 2026-07-30 17:08 | portland | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3478 | 115988 | 003c5279beeb8cf1 | `data/processed/portland/through_routes_r800.parquet` |
| 2026-07-30 17:08 | portland | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 3478 | 117395 | 796a0683be948671 | `data/processed/portland/through_routes_r1200.parquet` |
| 2026-07-30 17:08 | portland | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 3478 | 118197 | bd58461d369131cc | `data/processed/portland/through_routes_r1600.parquet` |
| 2026-07-30 17:19 | portland | segment_betweenness | derived: 01a major subgraph | 3478 | 85458 | 7a80365202a8042d | `data/processed/portland/segment_betweenness.parquet` |
| 2026-07-30 17:19 | portland | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3478 | 493098 | 568f949beb7e9685 | `data/processed/portland/controls_r400.parquet` |
| 2026-07-30 17:19 | portland | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3478 | 509171 | ea78e3ad473fa103 | `data/processed/portland/controls_r800.parquet` |
| 2026-07-30 17:19 | portland | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3478 | 515814 | 07241cdb798fe95e | `data/processed/portland/controls_r1200.parquet` |
| 2026-07-30 17:19 | portland | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3478 | 518888 | a15dfff85b0f39b1 | `data/processed/portland/controls_r1600.parquet` |
| 2026-07-30 17:19 | portland | analysis_table_r400 | derived: 02a/02b/02c + 03a | 3478 | 875990 | 9c33fb9cd1304342 | `data/analysis/analysis_table_r400.parquet` |
| 2026-07-30 17:19 | portland | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3478 | 920070 | f82124377f2800a9 | `data/analysis/analysis_table_r800.parquet` |
| 2026-07-30 17:19 | portland | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 3478 | 941760 | 60d319c9691dd124 | `data/analysis/analysis_table_r1200.parquet` |
| 2026-07-30 17:19 | portland | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 3478 | 953282 | 3acbe46b962bba34 | `data/analysis/analysis_table_r1600.parquet` |
| 2026-07-30 17:38 | portland | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/or/wac/or_wac_S000_JT00_2018.csv.gz | 16540 | 2473984 | 1a1db25e701e2f5c | `data/processed/portland/lodes_blocks.gpkg` |
| 2026-07-30 17:39 | portland | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/or/wac/or_wac_S000_JT00_2018.csv.gz | 16540 | 2473984 | 04b82424372225eb | `data/processed/portland/lodes_blocks.gpkg` |
| 2026-07-30 17:39 | portland | osm_poi | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 57202 | 7282688 | 7ef23feb6bcdffd9 | `data/raw/portland/osm_poi/pois.gpkg` |
| 2026-07-30 17:40 | portland | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3478 | 512299 | df565b8af8f74c37 | `data/processed/portland/controls_r400.parquet` |
| 2026-07-30 17:40 | portland | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3478 | 530738 | fd6344d0b726d6d2 | `data/processed/portland/controls_r800.parquet` |
| 2026-07-30 17:40 | portland | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3478 | 537916 | 14bd168c1fc6f012 | `data/processed/portland/controls_r1200.parquet` |
| 2026-07-30 17:40 | portland | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3478 | 541037 | 6566f2255426c93c | `data/processed/portland/controls_r1600.parquet` |
| 2026-07-30 17:40 | portland | analysis_table_r400 | derived: 02a/02b/02c + 03a | 3478 | 895191 | 328bdfb4e00135b7 | `data/analysis/analysis_table_r400.parquet` |
| 2026-07-30 17:40 | portland | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3478 | 941637 | a753970654d92a82 | `data/analysis/analysis_table_r800.parquet` |
| 2026-07-30 17:40 | portland | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 3478 | 963862 | 337c3bb184a5ce2c | `data/analysis/analysis_table_r1200.parquet` |
| 2026-07-30 17:40 | portland | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 3478 | 975431 | 5b6a81c7d3946c23 | `data/analysis/analysis_table_r1600.parquet` |
| 2026-07-30 17:48 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 3482d22b80be29d8 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 17:48 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 63193ab364f8d3c8 | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 17:48 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | 9ddf0d7d2e6ef836 | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 17:49 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 04192f6cd38cd07d | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 17:49 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | acfea8d982a6ade3 | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 17:50 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | 7f2898d8b55cb7f5 | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 17:50 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | f96b49a12d814e57 | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 17:50 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | 3d9d1628a6e3785a | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 17:54 | phoenix | osm_poi | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 723 | 196608 | 0676b45f85a30974 | `data/raw/phoenix/osm_poi/pois.gpkg` |
| 2026-07-30 17:57 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 3b306fae66507912 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 17:57 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 1f3ad2bf6c4171db | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 17:57 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | bfb35f6868743058 | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 17:57 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | 089340e577a9393e | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 17:57 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | 604ab23ff08bf5fe | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 17:58 | phoenix | building_footprints | https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv | 1358789 | 166652547 | 5dabf290c2df1c90 | `data/raw/phoenix/building_footprints/footprints_ua.parquet` |
| 2026-07-30 17:58 | phoenix | catchments_r400 | derived: 01d + 01b | 3941 | 6682272 | 092e0e81bdbdd060 | `data/processed/phoenix/catchments_r400.parquet` |
| 2026-07-30 17:58 | phoenix | catchments_r800 | derived: 01d + 01b | 3941 | 6551915 | 89276ebcc1d32d5b | `data/processed/phoenix/catchments_r800.parquet` |
| 2026-07-30 17:58 | phoenix | catchments_r1200 | derived: 01d + 01b | 3941 | 6460961 | b808ca96a2c5d99c | `data/processed/phoenix/catchments_r1200.parquet` |
| 2026-07-30 17:58 | phoenix | catchments_r1600 | derived: 01d + 01b | 3941 | 6409413 | 00c538c1b2cee208 | `data/processed/phoenix/catchments_r1600.parquet` |
| 2026-07-30 17:58 | phoenix | analysis_segments | derived: 01d | 3941 | 1330438 | 23983076e0c5b06a | `data/processed/phoenix/segments.parquet` |
| 2026-07-30 17:58 | phoenix | grid_1mi2 | derived: 01b | 1413 | 71025 | 12900c8ef2320d46 | `data/processed/phoenix/grid.parquet` |
| 2026-07-30 17:58 | phoenix | permeability_r400 | derived: 01a local subgraph + 02a catchments | 3941 | 344818 | 84f36d16913238b2 | `data/processed/phoenix/permeability_r400.parquet` |
| 2026-07-30 17:58 | phoenix | permeability_r800 | derived: 01a local subgraph + 02a catchments | 3941 | 375731 | d4a7b20e8c6516f7 | `data/processed/phoenix/permeability_r800.parquet` |
| 2026-07-30 17:58 | phoenix | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 3941 | 395645 | 871ae598879213eb | `data/processed/phoenix/permeability_r1200.parquet` |
| 2026-07-30 17:58 | phoenix | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 3941 | 405363 | 5261ba57cc1dfc8b | `data/processed/phoenix/permeability_r1600.parquet` |
| 2026-07-30 17:58 | phoenix | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 3941 | 120655 | 9c4b62f3226707e0 | `data/processed/phoenix/through_routes_r400.parquet` |
| 2026-07-30 17:58 | phoenix | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3941 | 125176 | 303c2b1d4b44b15e | `data/processed/phoenix/through_routes_r800.parquet` |
| 2026-07-30 17:58 | phoenix | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 3941 | 126589 | 851d0a750457ba0c | `data/processed/phoenix/through_routes_r1200.parquet` |
| 2026-07-30 17:58 | phoenix | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 3941 | 127072 | 2d18d9b656e482a2 | `data/processed/phoenix/through_routes_r1600.parquet` |
| 2026-07-30 18:01 | boston | osm_poi | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 3965 | 589824 | fe287d354547bb71 | `data/raw/boston/osm_poi/pois.gpkg` |
| 2026-07-30 18:03 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | f57f9755394141bd | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 18:03 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 7fad4f3518d723f4 | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 18:03 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | 2999b292d9230f60 | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 18:03 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | 00d9f8b4e7a9454a | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 18:03 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | 2a4e1d02978014e2 | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 18:10 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 95ec7e125a2a8de6 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 18:10 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 758b082baff194fe | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 18:10 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | b1fd3810c38c06ef | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 18:10 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | 01f0accfebcbd7c2 | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 18:10 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | 396cac8840d0bd51 | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 18:12 | boston | building_footprints | https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv | 1102826 | 124244210 | 95de12962e91342a | `data/raw/boston/building_footprints/footprints_ua.parquet` |
| 2026-07-30 18:15 | boston | catchments_r400 | derived: 01d + 01b | 24774 | 36311014 | dc490b780737bca4 | `data/processed/boston/catchments_r400.parquet` |
| 2026-07-30 18:15 | boston | catchments_r800 | derived: 01d + 01b | 24774 | 34925388 | c2157b7dd29b5486 | `data/processed/boston/catchments_r800.parquet` |
| 2026-07-30 18:15 | boston | catchments_r1200 | derived: 01d + 01b | 24774 | 34147223 | 168f1ff863f3dac7 | `data/processed/boston/catchments_r1200.parquet` |
| 2026-07-30 18:15 | boston | catchments_r1600 | derived: 01d + 01b | 24774 | 33551788 | 995963a6357289d1 | `data/processed/boston/catchments_r1600.parquet` |
| 2026-07-30 18:15 | boston | analysis_segments | derived: 01d | 24774 | 6195104 | 2c6786f72d861b2b | `data/processed/boston/segments.parquet` |
| 2026-07-30 18:15 | boston | grid_1mi2 | derived: 01b | 2348 | 115198 | 3687f38bd7cb522e | `data/processed/boston/grid.parquet` |
| 2026-07-30 18:15 | boston | permeability_r400 | derived: 01a local subgraph + 02a catchments | 24774 | 2015777 | dda01a8dc796674d | `data/processed/boston/permeability_r400.parquet` |
| 2026-07-30 18:15 | boston | permeability_r800 | derived: 01a local subgraph + 02a catchments | 24774 | 2137007 | 751883fb51700a88 | `data/processed/boston/permeability_r800.parquet` |
| 2026-07-30 18:15 | boston | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 24774 | 2226182 | 6b03462794762929 | `data/processed/boston/permeability_r1200.parquet` |
| 2026-07-30 18:15 | boston | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 24774 | 2305606 | ee26cffbbf7f6dbb | `data/processed/boston/permeability_r1600.parquet` |
| 2026-07-30 18:18 | boston | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 24774 | 702153 | 8b118a7a74d75f07 | `data/processed/boston/through_routes_r400.parquet` |
| 2026-07-30 18:18 | boston | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 24774 | 737200 | 4bab712ef9c7c8ce | `data/processed/boston/through_routes_r800.parquet` |
| 2026-07-30 18:18 | boston | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 24774 | 751171 | b3c16d1ad3b6a6fa | `data/processed/boston/through_routes_r1200.parquet` |
| 2026-07-30 18:18 | boston | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 24774 | 754429 | 8e6cec9766a24bea | `data/processed/boston/through_routes_r1600.parquet` |
| 2026-07-30 18:23 | phoenix | segment_betweenness | derived: 01a major subgraph | 3941 | 98216 | a3f8b6cfbd0f117a | `data/processed/phoenix/segment_betweenness.parquet` |
| 2026-07-30 18:23 | phoenix | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3941 | 540036 | 2b2ba526eb1287db | `data/processed/phoenix/controls_r400.parquet` |
| 2026-07-30 18:23 | phoenix | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3941 | 557195 | bfe1f13ee98dcc6f | `data/processed/phoenix/controls_r800.parquet` |
| 2026-07-30 18:23 | phoenix | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3941 | 563253 | 9f521d2c6266a1ff | `data/processed/phoenix/controls_r1200.parquet` |
| 2026-07-30 18:23 | phoenix | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3941 | 565414 | 9b765ee61bf688d6 | `data/processed/phoenix/controls_r1600.parquet` |
| 2026-07-30 18:23 | phoenix | analysis_table_r400 | derived: 02a/02b/02c + 03a | 3941 | 997077 | 1b3a9bbc7d7c0cf3 | `data/analysis/analysis_table_r400.parquet` |
| 2026-07-30 18:23 | phoenix | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3941 | 1045764 | 673897af0b54e7ba | `data/analysis/analysis_table_r800.parquet` |
| 2026-07-30 18:23 | phoenix | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 3941 | 1070385 | 0a9028ac7a8738c9 | `data/analysis/analysis_table_r1200.parquet` |
| 2026-07-30 18:23 | phoenix | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 3941 | 1081167 | 183761df984ec6e3 | `data/analysis/analysis_table_r1600.parquet` |
| 2026-07-30 18:50 | boston | segment_betweenness | derived: 01a major subgraph | 24774 | 606863 | 44f51a05720b707f | `data/processed/boston/segment_betweenness.parquet` |
| 2026-07-30 18:52 | boston | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 24774 | 3119185 | 41ddb67a908554e5 | `data/processed/boston/controls_r400.parquet` |
| 2026-07-30 18:52 | boston | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 24774 | 3366860 | b99e84dfd26f51c3 | `data/processed/boston/controls_r800.parquet` |
| 2026-07-30 18:52 | boston | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 24774 | 3466357 | 3b7f74be07006c48 | `data/processed/boston/controls_r1200.parquet` |
| 2026-07-30 18:52 | boston | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 24774 | 3515405 | f85e1d0716b5a0b1 | `data/processed/boston/controls_r1600.parquet` |
| 2026-07-30 18:52 | boston | analysis_table_r400 | derived: 02a/02b/02c + 03a | 24774 | 5645636 | 970c5ef387b1d91c | `data/analysis/analysis_table_r400.parquet` |
| 2026-07-30 18:52 | boston | analysis_table_r800 | derived: 02a/02b/02c + 03a | 24774 | 6021830 | c50c181f0a4eb30d | `data/analysis/analysis_table_r800.parquet` |
| 2026-07-30 18:52 | boston | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 24774 | 6218187 | 2ad196b1aeee97fd | `data/analysis/analysis_table_r1200.parquet` |
| 2026-07-30 18:52 | boston | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 24774 | 6338600 | 8030c161e64497dd | `data/analysis/analysis_table_r1600.parquet` |
| 2026-07-30 18:53 | denver | analysis_table_r400 | derived: 02a/02b/02c + 03a | 2964 | 770925 | 77cfaf1ed7d9be84 | `data/analysis/analysis_table_denver_r400.parquet` |
| 2026-07-30 18:53 | denver | analysis_table_r800 | derived: 02a/02b/02c + 03a | 2964 | 805688 | f7340fa92eaab0a9 | `data/analysis/analysis_table_denver_r800.parquet` |
| 2026-07-30 18:53 | denver | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 2964 | 823131 | 1c378b9035be431f | `data/analysis/analysis_table_denver_r1200.parquet` |
| 2026-07-30 18:53 | denver | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 2964 | 831458 | a15fa4767311b1d4 | `data/analysis/analysis_table_denver_r1600.parquet` |
| 2026-07-30 18:53 | portland | analysis_table_r400 | derived: 02a/02b/02c + 03a | 3478 | 895685 | c55baa50c67545b2 | `data/analysis/analysis_table_portland_r400.parquet` |
| 2026-07-30 18:53 | portland | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3478 | 942131 | d5ae6d15a750c1f3 | `data/analysis/analysis_table_portland_r800.parquet` |
| 2026-07-30 18:53 | portland | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 3478 | 964356 | 562abd250bb7efb4 | `data/analysis/analysis_table_portland_r1200.parquet` |
| 2026-07-30 18:53 | portland | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 3478 | 975925 | 898f98ae89fd3b09 | `data/analysis/analysis_table_portland_r1600.parquet` |
| 2026-07-30 18:53 | phoenix | analysis_table_r400 | derived: 02a/02b/02c + 03a | 3941 | 997566 | 76f3b4faeba2dbb1 | `data/analysis/analysis_table_phoenix_r400.parquet` |
| 2026-07-30 18:53 | phoenix | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3941 | 1046253 | 2269c38d7b87ea01 | `data/analysis/analysis_table_phoenix_r800.parquet` |
| 2026-07-30 18:53 | phoenix | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 3941 | 1070874 | 12d41025d9a32103 | `data/analysis/analysis_table_phoenix_r1200.parquet` |
| 2026-07-30 18:53 | phoenix | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 3941 | 1081658 | 21882f0c344a58c2 | `data/analysis/analysis_table_phoenix_r1600.parquet` |
| 2026-07-30 18:53 | boston | analysis_table_r400 | derived: 02a/02b/02c + 03a | 24774 | 5646180 | e0015f03d8e006e5 | `data/analysis/analysis_table_boston_r400.parquet` |
| 2026-07-30 18:53 | boston | analysis_table_r800 | derived: 02a/02b/02c + 03a | 24774 | 6022374 | 94c951fa494c95e9 | `data/analysis/analysis_table_boston_r800.parquet` |
| 2026-07-30 18:53 | boston | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 24774 | 6218731 | 39705e599541f308 | `data/analysis/analysis_table_boston_r1200.parquet` |
| 2026-07-30 18:53 | boston | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 24774 | 6339144 | bfa7e780f1250846 | `data/analysis/analysis_table_boston_r1600.parquet` |
| 2026-07-30 18:54 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | b5900add0f3ae882 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 18:54 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 09c3490101ae62d8 | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 18:54 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | 699cff3eb8cf2ead | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 18:57 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 32d558b524ba48c0 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 18:57 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 4416935e68817307 | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 18:57 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | 8f810c62093b04d5 | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 19:00 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 373e4871da9cc173 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 19:00 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 8e237ddffc46afe5 | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 19:00 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | 02b4c524031460fa | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 19:03 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 86e92a0d5b1c6180 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 19:03 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | b476467b9e19316a | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 19:03 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | d30c615bacc99055 | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 19:38 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | e44d22eacc67c9c5 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 19:38 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 7b1979bd83b83c69 | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 19:38 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | 9b101578da023127 | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 19:38 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | ef3ebc3506e5cb7b | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 19:38 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | 3663e4598edb8363 | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 19:46 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 6bfbdd986cac23a3 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 19:46 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 152df8cfc335bce7 | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 19:46 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | 912aa9005cc5df8e | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 19:46 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | 58e214928931e524 | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 19:46 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | a3fab70c0e257bee | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 19:46 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 7d72b51418a9e8b8 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 19:46 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 2eecad2ee47dad2c | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 19:46 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | 7e2665347ae01a07 | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 19:46 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | 49c30076fd0d842f | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 19:46 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | 2b240bbfdbb79010 | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 19:55 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 6723ac6127d505ab | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 19:55 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | db1794ab56f3119c | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 19:55 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | 135ac3338645b54d | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 19:55 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | 8205db580b0e0e20 | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 19:55 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | 2cb1dc8c42bd2347 | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 20:04 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 876b93009a51d447 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 20:04 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | e4f8284261d8bbd4 | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 20:04 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | be8b2b6b7d62866e | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 20:04 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | 2f69c4578dcff8d0 | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 20:04 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | eefd71eba75051d4 | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 20:13 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 9f04806277539454 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 20:13 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 18f854bed603cbe2 | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 20:13 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | ebb84d9059189eb2 | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 20:13 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | 0d12a7f708e5d66e | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 20:13 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | 19248ba7442c3711 | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 20:21 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 0c5474bbe0dcd84e | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 20:21 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 5ee8c07665c787e2 | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 20:21 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | 298c4f3753e6072e | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 20:22 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | 92a05445588c63d6 | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 20:22 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | d993568d8e9fa1bf | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-30 20:30 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | ec30b1085d273b7c | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-30 20:30 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | b5f5f871d0104a03 | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-30 20:30 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | e340681a0af99783 | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-30 20:30 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | 9654fd7a5bb33769 | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-30 20:30 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | 3180f2787aa7f906 | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-31 00:52 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | bc2d26a47d675ae8 | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-31 00:52 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 86624217efb9fa8d | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-31 00:52 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | e3d3e64c283fd439 | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-31 00:53 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | 9a4bb2e24f57cb90 | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-31 00:53 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | 33b075c731333bc6 | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-31 01:20 | wasatch_front | osm_network_urban_area_all | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 153582 | 54112256 | b47d524228a654c8 | `data/raw/wasatch_front/osm/network_urban_area_all.gpkg` |
| 2026-07-31 01:20 | wasatch_front | osm_network_urban_area_major | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 34461 | 10670080 | a3605ea44c50c15e | `data/raw/wasatch_front/osm/network_urban_area_major.gpkg` |
| 2026-07-31 01:20 | wasatch_front | osm_network_urban_area_local | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 119059 | 35663872 | 81436452effc815c | `data/raw/wasatch_front/osm/network_urban_area_local.gpkg` |
| 2026-07-31 01:20 | wasatch_front | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/ut/wac/ut_wac_S000_JT00_2018.csv.gz | 15590 | 2330624 | 339b7aee4eba2ac6 | `data/processed/wasatch_front/lodes_blocks.gpkg` |
| 2026-07-31 01:43 | wasatch_front | osm_poi | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 38017 | 4853760 | 3c4cd598bbe088e7 | `data/raw/wasatch_front/osm_poi/pois.gpkg` |
| 2026-07-31 01:45 | wasatch_front | building_footprints | https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv | 729677 | 86253938 | 64ca58ad9a6cdc70 | `data/raw/wasatch_front/building_footprints/footprints_ua.parquet` |
| 2026-07-31 01:45 | wasatch_front | catchments_r400 | derived: 01d + 01b | 2372 | 3920078 | 3eaa1a085a419d1c | `data/processed/wasatch_front/catchments_r400.parquet` |
| 2026-07-31 01:45 | wasatch_front | catchments_r800 | derived: 01d + 01b | 2372 | 3790146 | 6692f774eeaa692d | `data/processed/wasatch_front/catchments_r800.parquet` |
| 2026-07-31 01:45 | wasatch_front | catchments_r1200 | derived: 01d + 01b | 2372 | 3711700 | e0deb8947740d548 | `data/processed/wasatch_front/catchments_r1200.parquet` |
| 2026-07-31 01:45 | wasatch_front | catchments_r1600 | derived: 01d + 01b | 2372 | 3660547 | e2bc06dde4aac50c | `data/processed/wasatch_front/catchments_r1600.parquet` |
| 2026-07-31 01:45 | wasatch_front | analysis_segments | derived: 01d | 2372 | 783836 | b3f6bbe3321a5141 | `data/processed/wasatch_front/segments.parquet` |
| 2026-07-31 01:45 | wasatch_front | grid_1mi2 | derived: 01b | 933 | 51900 | ed95cfc13a3a8cd2 | `data/processed/wasatch_front/grid.parquet` |
| 2026-07-31 01:45 | wasatch_front | permeability_r400 | derived: 01a local subgraph + 02a catchments | 2372 | 189665 | bc0460f242f66f6e | `data/processed/wasatch_front/permeability_r400.parquet` |
| 2026-07-31 01:45 | wasatch_front | permeability_r800 | derived: 01a local subgraph + 02a catchments | 2372 | 204850 | 3c2b56452941fe08 | `data/processed/wasatch_front/permeability_r800.parquet` |
| 2026-07-31 01:45 | wasatch_front | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 2372 | 214081 | b0830dce0a268b1f | `data/processed/wasatch_front/permeability_r1200.parquet` |
| 2026-07-31 01:45 | wasatch_front | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 2372 | 218306 | 4d6c566daf63516b | `data/processed/wasatch_front/permeability_r1600.parquet` |
| 2026-07-31 01:46 | wasatch_front | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 69451 | 4e87d4ba254c79d9 | `data/processed/wasatch_front/through_routes_r400.parquet` |
| 2026-07-31 01:46 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 71403 | d4b62c364942cf28 | `data/processed/wasatch_front/through_routes_r800.parquet` |
| 2026-07-31 01:46 | wasatch_front | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 72227 | 09294d8f5d31766d | `data/processed/wasatch_front/through_routes_r1200.parquet` |
| 2026-07-31 01:46 | wasatch_front | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 72711 | f4dcf8e31a1ad8a4 | `data/processed/wasatch_front/through_routes_r1600.parquet` |
| 2026-07-31 01:53 | wasatch_front | segment_betweenness | derived: 01a major subgraph | 2372 | 55479 | a55200dd3d0ef28c | `data/processed/wasatch_front/segment_betweenness.parquet` |
| 2026-07-31 01:53 | wasatch_front | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2372 | 351141 | f504a5486addae0d | `data/processed/wasatch_front/controls_r400.parquet` |
| 2026-07-31 01:53 | wasatch_front | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2372 | 360220 | 04eff4ff338c08e3 | `data/processed/wasatch_front/controls_r800.parquet` |
| 2026-07-31 01:53 | wasatch_front | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2372 | 364743 | 848351ad83084d16 | `data/processed/wasatch_front/controls_r1200.parquet` |
| 2026-07-31 01:53 | wasatch_front | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2372 | 365862 | 49629b0f04db48ba | `data/processed/wasatch_front/controls_r1600.parquet` |
| 2026-07-31 01:53 | wasatch_front | analysis_table_r400 | derived: 02a/02b/02c + 03a | 2372 | 609810 | c49cdcd5d2674c6d | `data/analysis/analysis_table_wasatch_front_r400.parquet` |
| 2026-07-31 01:53 | wasatch_front | analysis_table_r800 | derived: 02a/02b/02c + 03a | 2372 | 634143 | 10493f4f8391ea70 | `data/analysis/analysis_table_wasatch_front_r800.parquet` |
| 2026-07-31 01:53 | wasatch_front | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 2372 | 647000 | c529cd09d00a507a | `data/analysis/analysis_table_wasatch_front_r1200.parquet` |
| 2026-07-31 01:53 | wasatch_front | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 2372 | 651764 | b989a29bf61cdf1f | `data/analysis/analysis_table_wasatch_front_r1600.parquet` |
| 2026-07-31 01:54 | wasatch_front | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 389120 | 6fc5e94de9f4f48a | `data/raw/wasatch_front/census/urban_area.gpkg` |
| 2026-07-31 01:54 | wasatch_front | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_49_tract.zip | 520 | 2920448 | 096898c395dca25f | `data/raw/wasatch_front/census/tracts.gpkg` |
| 2026-07-31 01:55 | wasatch_front | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 520 | 2936832 | 00c593df67c63081 | `data/processed/wasatch_front/tract_density.gpkg` |
| 2026-07-31 01:55 | wasatch_front | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 14541 | 4575232 | 5c909b6cd79ccf99 | `data/raw/wasatch_front/hpms/hpms2018_ua_all.gpkg` |
| 2026-07-31 01:55 | wasatch_front | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/Utah_2018_PR/FeatureServer/0 | 10547 | 3432448 | 496aa9041488e253 | `data/raw/wasatch_front/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-07-31 02:05 | wasatch_front | osm_network_urban_area_all | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 203512 | 71254016 | ec95a903dd09590a | `data/raw/wasatch_front/osm/network_urban_area_all.gpkg` |
| 2026-07-31 02:05 | wasatch_front | osm_network_urban_area_major | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 47022 | 14434304 | fc79bb934abc1d19 | `data/raw/wasatch_front/osm/network_urban_area_major.gpkg` |
| 2026-07-31 02:05 | wasatch_front | osm_network_urban_area_local | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 156382 | 46501888 | 79bc25ed27f24f57 | `data/raw/wasatch_front/osm/network_urban_area_local.gpkg` |
| 2026-07-31 02:05 | wasatch_front | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/ut/wac/ut_wac_S000_JT00_2018.csv.gz | 15590 | 2330624 | 4331f649e5258cac | `data/processed/wasatch_front/lodes_blocks.gpkg` |
| 2026-07-31 02:05 | wasatch_front | osm_poi | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 38017 | 4853760 | 3c4cd598bbe088e7 | `data/raw/wasatch_front/osm_poi/pois.gpkg` |
| 2026-07-31 02:05 | wasatch_front | catchments_r400 | derived: 01d + 01b | 2372 | 3920078 | 3eaa1a085a419d1c | `data/processed/wasatch_front/catchments_r400.parquet` |
| 2026-07-31 02:05 | wasatch_front | catchments_r800 | derived: 01d + 01b | 2372 | 3790146 | 6692f774eeaa692d | `data/processed/wasatch_front/catchments_r800.parquet` |
| 2026-07-31 02:05 | wasatch_front | catchments_r1200 | derived: 01d + 01b | 2372 | 3711700 | e0deb8947740d548 | `data/processed/wasatch_front/catchments_r1200.parquet` |
| 2026-07-31 02:05 | wasatch_front | catchments_r1600 | derived: 01d + 01b | 2372 | 3660547 | e2bc06dde4aac50c | `data/processed/wasatch_front/catchments_r1600.parquet` |
| 2026-07-31 02:05 | wasatch_front | analysis_segments | derived: 01d | 2372 | 783836 | b3f6bbe3321a5141 | `data/processed/wasatch_front/segments.parquet` |
| 2026-07-31 02:05 | wasatch_front | grid_1mi2 | derived: 01b | 933 | 51900 | ed95cfc13a3a8cd2 | `data/processed/wasatch_front/grid.parquet` |
| 2026-07-31 02:05 | wasatch_front | permeability_r400 | derived: 01a local subgraph + 02a catchments | 2372 | 219264 | 6b0f627776dbd31e | `data/processed/wasatch_front/permeability_r400.parquet` |
| 2026-07-31 02:05 | wasatch_front | permeability_r800 | derived: 01a local subgraph + 02a catchments | 2372 | 238219 | 8d70d8b16b97308a | `data/processed/wasatch_front/permeability_r800.parquet` |
| 2026-07-31 02:05 | wasatch_front | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 2372 | 249699 | 40b51eb95ba9f2c4 | `data/processed/wasatch_front/permeability_r1200.parquet` |
| 2026-07-31 02:05 | wasatch_front | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 2372 | 255130 | b9844f96a108ab97 | `data/processed/wasatch_front/permeability_r1600.parquet` |
| 2026-07-31 02:06 | wasatch_front | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 76443 | 99a29aafbd8052a5 | `data/processed/wasatch_front/through_routes_r400.parquet` |
| 2026-07-31 02:06 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 78757 | 1306110b0ba390d1 | `data/processed/wasatch_front/through_routes_r800.parquet` |
| 2026-07-31 02:06 | wasatch_front | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 79737 | e61e5e28c1abb502 | `data/processed/wasatch_front/through_routes_r1200.parquet` |
| 2026-07-31 02:06 | wasatch_front | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 80241 | dfec18ac972d3fcf | `data/processed/wasatch_front/through_routes_r1600.parquet` |
| 2026-07-31 02:13 | wasatch_front | segment_betweenness | derived: 01a major subgraph | 2372 | 60353 | ea1b3016e0934aff | `data/processed/wasatch_front/segment_betweenness.parquet` |
| 2026-07-31 02:13 | wasatch_front | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2372 | 351141 | f504a5486addae0d | `data/processed/wasatch_front/controls_r400.parquet` |
| 2026-07-31 02:13 | wasatch_front | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2372 | 360220 | 04eff4ff338c08e3 | `data/processed/wasatch_front/controls_r800.parquet` |
| 2026-07-31 02:13 | wasatch_front | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2372 | 364743 | 848351ad83084d16 | `data/processed/wasatch_front/controls_r1200.parquet` |
| 2026-07-31 02:13 | wasatch_front | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2372 | 365862 | 49629b0f04db48ba | `data/processed/wasatch_front/controls_r1600.parquet` |
| 2026-07-31 02:13 | wasatch_front | analysis_table_r400 | derived: 02a/02b/02c + 03a | 2372 | 640588 | df90a3dabc44e675 | `data/analysis/analysis_table_wasatch_front_r400.parquet` |
| 2026-07-31 02:13 | wasatch_front | analysis_table_r800 | derived: 02a/02b/02c + 03a | 2372 | 668666 | d68b92819be0b09d | `data/analysis/analysis_table_wasatch_front_r800.parquet` |
| 2026-07-31 02:13 | wasatch_front | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 2372 | 683886 | b7c926e8dc567097 | `data/analysis/analysis_table_wasatch_front_r1200.parquet` |
| 2026-07-31 02:13 | wasatch_front | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 2372 | 689860 | 2e6b13c42db06a4a | `data/analysis/analysis_table_wasatch_front_r1600.parquet` |
| 2026-07-31 17:10 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 123690 | 44fbfe8ab1026bcc | `data/processed/denver/through_routes_r800.parquet` |
| 2026-07-31 17:10 | portland | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3478 | 140729 | 7fbf90ee0e185b3f | `data/processed/portland/through_routes_r800.parquet` |
| 2026-07-31 17:10 | phoenix | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3941 | 144190 | f182c8e160ffe1e0 | `data/processed/phoenix/through_routes_r800.parquet` |
| 2026-07-31 17:10 | boston | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 24774 | 790651 | 93428d13bd3b87c7 | `data/processed/boston/through_routes_r800.parquet` |
| 2026-07-31 17:11 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 92476 | 793a15c37c073520 | `data/processed/wasatch_front/through_routes_r800.parquet` |
| 2026-07-31 18:25 | denver | cell_metrics | derived: 01a OSM + TIGER blocks + ACS + LODES | 844 | 71394 | a60c908d99517916 | `data/processed/denver/cell_metrics.parquet` |
| 2026-07-31 18:26 | denver | cell_metrics | derived: 01a OSM + TIGER blocks + ACS + LODES | 844 | 82367 | 5cb3635845f60474 | `data/processed/denver/cell_metrics.parquet` |
| 2026-07-31 18:27 | portland | cell_metrics | derived: 01a OSM + TIGER blocks + ACS + LODES | 740 | 73287 | d8acac0e8840405b | `data/processed/portland/cell_metrics.parquet` |
| 2026-07-31 18:27 | phoenix | cell_metrics | derived: 01a OSM + TIGER blocks + ACS + LODES | 1413 | 119375 | 2404e869dcea8505 | `data/processed/phoenix/cell_metrics.parquet` |
| 2026-07-31 18:27 | boston | cell_metrics | derived: 01a OSM + TIGER blocks + ACS + LODES | 2348 | 168230 | 1c98875de7ded998 | `data/processed/boston/cell_metrics.parquet` |
| 2026-07-31 18:27 | wasatch_front | cell_metrics | derived: 01a OSM + TIGER blocks + ACS + LODES | 933 | 86239 | 9cbbaca8e51520bf | `data/processed/wasatch_front/cell_metrics.parquet` |
| 2026-07-31 18:59 | denver | permeability_r800 | derived: 01a local subgraph + 02a catchments | 2964 | 308375 | f406d736e434aa4c | `data/processed/denver/permeability_r800.parquet` |
| 2026-07-31 18:59 | denver | permeability_r400 | derived: 01a local subgraph + 02a catchments | 2964 | 282493 | 63cc0e45ec106089 | `data/processed/denver/permeability_r400.parquet` |
| 2026-07-31 18:59 | denver | permeability_r800 | derived: 01a local subgraph + 02a catchments | 2964 | 308375 | f406d736e434aa4c | `data/processed/denver/permeability_r800.parquet` |
| 2026-07-31 18:59 | denver | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 2964 | 325008 | cbfa830f849a85b7 | `data/processed/denver/permeability_r1200.parquet` |
| 2026-07-31 18:59 | denver | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 2964 | 334132 | a28d898a56f07521 | `data/processed/denver/permeability_r1600.parquet` |
| 2026-07-31 18:59 | portland | permeability_r400 | derived: 01a local subgraph + 02a catchments | 3478 | 322331 | 8a0228727d5f1797 | `data/processed/portland/permeability_r400.parquet` |
| 2026-07-31 18:59 | portland | permeability_r800 | derived: 01a local subgraph + 02a catchments | 3478 | 351897 | 057ca31ff8195de5 | `data/processed/portland/permeability_r800.parquet` |
| 2026-07-31 18:59 | portland | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 3478 | 371518 | eca4cd4825819a1c | `data/processed/portland/permeability_r1200.parquet` |
| 2026-07-31 18:59 | portland | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 3478 | 383467 | 6de835491f27ae78 | `data/processed/portland/permeability_r1600.parquet` |
| 2026-07-31 18:59 | phoenix | permeability_r400 | derived: 01a local subgraph + 02a catchments | 3941 | 357767 | 5d850fdb8954faf6 | `data/processed/phoenix/permeability_r400.parquet` |
| 2026-07-31 18:59 | phoenix | permeability_r800 | derived: 01a local subgraph + 02a catchments | 3941 | 392814 | 610faacd4dbe617b | `data/processed/phoenix/permeability_r800.parquet` |
| 2026-07-31 18:59 | phoenix | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 3941 | 415672 | 0f74e05f45e90592 | `data/processed/phoenix/permeability_r1200.parquet` |
| 2026-07-31 18:59 | phoenix | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 3941 | 427372 | fc03790e5ad55143 | `data/processed/phoenix/permeability_r1600.parquet` |
| 2026-07-31 19:00 | wasatch_front | permeability_r400 | derived: 01a local subgraph + 02a catchments | 2372 | 228933 | 2268f2a507759a0e | `data/processed/wasatch_front/permeability_r400.parquet` |
| 2026-07-31 19:00 | wasatch_front | permeability_r800 | derived: 01a local subgraph + 02a catchments | 2372 | 250289 | 4030b7e02ef9a485 | `data/processed/wasatch_front/permeability_r800.parquet` |
| 2026-07-31 19:00 | wasatch_front | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 2372 | 264207 | 48390fe52f9afccc | `data/processed/wasatch_front/permeability_r1200.parquet` |
| 2026-07-31 19:00 | wasatch_front | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 2372 | 271219 | ca918eba6a8af5d3 | `data/processed/wasatch_front/permeability_r1600.parquet` |
| 2026-07-31 19:00 | boston | permeability_r400 | derived: 01a local subgraph + 02a catchments | 24774 | 2076397 | 86ec3a45607a1d5a | `data/processed/boston/permeability_r400.parquet` |
| 2026-07-31 19:00 | boston | permeability_r800 | derived: 01a local subgraph + 02a catchments | 24774 | 2210730 | a71abb0885a514a9 | `data/processed/boston/permeability_r800.parquet` |
| 2026-07-31 19:00 | boston | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 24774 | 2311495 | 56268e570f27879c | `data/processed/boston/permeability_r1200.parquet` |
| 2026-07-31 19:00 | boston | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 24774 | 2403511 | d0320784ebfa4e87 | `data/processed/boston/permeability_r1600.parquet` |
| 2026-07-31 19:01 | denver | analysis_table_r400 | derived: 02a/02b/02c + 03a | 2964 | 771259 | 8da1c295bc17effb | `data/analysis/analysis_table_denver_r400.parquet` |
| 2026-07-31 19:01 | denver | analysis_table_r800 | derived: 02a/02b/02c + 03a | 2964 | 828393 | fe5639b38ed3a1bb | `data/analysis/analysis_table_denver_r800.parquet` |
| 2026-07-31 19:01 | denver | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 2964 | 823604 | 8dc467bc5a99888d | `data/analysis/analysis_table_denver_r1200.parquet` |
| 2026-07-31 19:01 | denver | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 2964 | 831941 | 16e2e4611d3141da | `data/analysis/analysis_table_denver_r1600.parquet` |
| 2026-07-31 19:01 | portland | analysis_table_r400 | derived: 02a/02b/02c + 03a | 3478 | 897278 | 5b6a017ec33add80 | `data/analysis/analysis_table_portland_r400.parquet` |
| 2026-07-31 19:01 | portland | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3478 | 967600 | 9266cb517e2a12de | `data/analysis/analysis_table_portland_r800.parquet` |
| 2026-07-31 19:01 | portland | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 3478 | 965431 | dc892397ce0d1714 | `data/analysis/analysis_table_portland_r1200.parquet` |
| 2026-07-31 19:01 | portland | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 3478 | 976885 | 8a8eb6c2c42eb6ec | `data/analysis/analysis_table_portland_r1600.parquet` |
| 2026-07-31 19:01 | phoenix | analysis_table_r400 | derived: 02a/02b/02c + 03a | 3941 | 998762 | 555d3b6b413fa12d | `data/analysis/analysis_table_phoenix_r400.parquet` |
| 2026-07-31 19:01 | phoenix | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3941 | 1067125 | e11d467c3f6ab70d | `data/analysis/analysis_table_phoenix_r800.parquet` |
| 2026-07-31 19:01 | phoenix | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 3941 | 1072191 | 97a803407459da0c | `data/analysis/analysis_table_phoenix_r1200.parquet` |
| 2026-07-31 19:01 | phoenix | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 3941 | 1082641 | 8b2f4c28eb69f67f | `data/analysis/analysis_table_phoenix_r1600.parquet` |
| 2026-07-31 19:01 | wasatch_front | analysis_table_r400 | derived: 02a/02b/02c + 03a | 2372 | 641821 | 92374205436820de | `data/analysis/analysis_table_wasatch_front_r400.parquet` |
| 2026-07-31 19:01 | wasatch_front | analysis_table_r800 | derived: 02a/02b/02c + 03a | 2372 | 683229 | 6ae71fa7741ff5c9 | `data/analysis/analysis_table_wasatch_front_r800.parquet` |
| 2026-07-31 19:01 | wasatch_front | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 2372 | 684786 | 255bb27df20535db | `data/analysis/analysis_table_wasatch_front_r1200.parquet` |
| 2026-07-31 19:01 | wasatch_front | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 2372 | 690350 | a25dfbfb64e55b56 | `data/analysis/analysis_table_wasatch_front_r1600.parquet` |
| 2026-07-31 19:01 | boston | analysis_table_r400 | derived: 02a/02b/02c + 03a | 24774 | 5651869 | 195afae21df43aa4 | `data/analysis/analysis_table_boston_r400.parquet` |
| 2026-07-31 19:01 | boston | analysis_table_r800 | derived: 02a/02b/02c + 03a | 24774 | 6085913 | 90addae6a489e0ee | `data/analysis/analysis_table_boston_r800.parquet` |
| 2026-07-31 19:01 | boston | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 24774 | 6230885 | 9e9596de51748b8c | `data/analysis/analysis_table_boston_r1200.parquet` |
| 2026-07-31 19:01 | boston | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 24774 | 6356692 | da3139c4083e8bd0 | `data/analysis/analysis_table_boston_r1600.parquet` |
| 2026-08-02 15:12 | charlotte | census_urban_area | https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip | 1 | 782336 | f526b7511360001c | `data/raw/charlotte/census/urban_area.gpkg` |
| 2026-08-02 15:12 | charlotte | census_tracts | https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_45_tract.zip | 395 | 2306048 | 5995dd6adaf0bd03 | `data/raw/charlotte/census/tracts.gpkg` |
| 2026-08-02 15:13 | charlotte | acs2020_tract_density | https://api.census.gov/data/2020/acs/acs5 | 395 | 2322432 | 1367054bec3b257a | `data/processed/charlotte/tract_density.gpkg` |
| 2026-08-02 15:14 | charlotte | hpms2018_ua_all | https://geo.dot.gov/server/rest/services/Hosted/NorthCarolina_2018_PR/FeatureServer/0 | 8751 | 3829760 | 3589f25673363315 | `data/raw/charlotte/hpms/hpms2018_ua_all.gpkg` |
| 2026-08-02 15:14 | charlotte | hpms2018_ua_analysis | https://geo.dot.gov/server/rest/services/Hosted/NorthCarolina_2018_PR/FeatureServer/0 | 5498 | 2461696 | 6b16e74b9336f7f7 | `data/raw/charlotte/hpms/hpms2018_ua_analysis.gpkg` |
| 2026-08-02 17:35 | charlotte | osm_network_urban_area_all | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 136820 | 52662272 | 6fe719375acdad37 | `data/raw/charlotte/osm/network_urban_area_all.gpkg` |
| 2026-08-02 17:35 | charlotte | osm_network_urban_area_major | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 25264 | 8859648 | 9e416cbd5373ec7c | `data/raw/charlotte/osm/network_urban_area_major.gpkg` |
| 2026-08-02 17:35 | charlotte | osm_network_urban_area_local | https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx) | 111543 | 36450304 | ca7c6f42c279f7f5 | `data/raw/charlotte/osm/network_urban_area_local.gpkg` |
| 2026-08-02 17:38 | charlotte | lodes2018_wac_blocks | https://lehd.ces.census.gov/data/lodes/LODES8/nc/wac/nc_wac_S000_JT00_2018.csv.gz | 8251 | 1286144 | 34a74eb928553bfb | `data/processed/charlotte/lodes_blocks.gpkg` |
| 2026-08-02 17:57 | charlotte | building_footprints | https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv | 447708 | 52046994 | ace942dd9c775168 | `data/raw/charlotte/building_footprints/footprints_ua.parquet` |
| 2026-08-02 17:57 | charlotte | catchments_r400 | derived: 01d + 01b | 1726 | 3664903 | 12d48d73449746d0 | `data/processed/charlotte/catchments_r400.parquet` |
| 2026-08-02 17:57 | charlotte | catchments_r800 | derived: 01d + 01b | 1726 | 3418173 | b70f7e2e2579273d | `data/processed/charlotte/catchments_r800.parquet` |
| 2026-08-02 17:57 | charlotte | catchments_r1200 | derived: 01d + 01b | 1726 | 3256420 | 11d977cce7bc26a2 | `data/processed/charlotte/catchments_r1200.parquet` |
| 2026-08-02 17:57 | charlotte | catchments_r1600 | derived: 01d + 01b | 1726 | 3152862 | d7b668e02e534e15 | `data/processed/charlotte/catchments_r1600.parquet` |
| 2026-08-02 17:57 | charlotte | analysis_segments | derived: 01d | 1726 | 927248 | 693bdfe20460b51c | `data/processed/charlotte/segments.parquet` |
| 2026-08-02 17:57 | charlotte | grid_1mi2 | derived: 01b | 903 | 49168 | f7c95e95ddcdc1a9 | `data/processed/charlotte/grid.parquet` |
| 2026-08-02 17:57 | charlotte | permeability_r400 | derived: 01a local subgraph + 02a catchments | 1726 | 163734 | 67e1d3355cf7bb9e | `data/processed/charlotte/permeability_r400.parquet` |
| 2026-08-02 17:57 | charlotte | permeability_r800 | derived: 01a local subgraph + 02a catchments | 1726 | 180266 | f82ed73635389a90 | `data/processed/charlotte/permeability_r800.parquet` |
| 2026-08-02 17:57 | charlotte | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 1726 | 189490 | 0f3039ba17db92ed | `data/processed/charlotte/permeability_r1200.parquet` |
| 2026-08-02 17:57 | charlotte | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 1726 | 196899 | 01c7949a41fd176d | `data/processed/charlotte/permeability_r1600.parquet` |
| 2026-08-02 17:58 | charlotte | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 1726 | 63180 | 5fe017bb2d68556c | `data/processed/charlotte/through_routes_r400.parquet` |
| 2026-08-02 17:58 | charlotte | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 1726 | 65651 | d5016454e2f7d784 | `data/processed/charlotte/through_routes_r800.parquet` |
| 2026-08-02 17:58 | charlotte | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 1726 | 66195 | 3507dcf189cf0e80 | `data/processed/charlotte/through_routes_r1200.parquet` |
| 2026-08-02 17:58 | charlotte | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 1726 | 66743 | 504a856299e1f558 | `data/processed/charlotte/through_routes_r1600.parquet` |
| 2026-08-02 18:03 | charlotte | segment_betweenness | derived: 01a major subgraph | 1726 | 43499 | 2ceed0d2d0269c01 | `data/processed/charlotte/segment_betweenness.parquet` |
| 2026-08-02 18:03 | charlotte | cell_metrics | derived: 01a OSM + TIGER blocks + ACS + LODES | 903 | 80791 | aa43814fcd581776 | `data/processed/charlotte/cell_metrics.parquet` |
| 2026-08-02 18:04 | charlotte | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 1726 | 240502 | 778d3761deb35d9c | `data/processed/charlotte/controls_r400.parquet` |
| 2026-08-02 18:04 | charlotte | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 1726 | 247224 | 0764cb31f9ae03d0 | `data/processed/charlotte/controls_r800.parquet` |
| 2026-08-02 18:04 | charlotte | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 1726 | 249612 | aea75e9023c7574c | `data/processed/charlotte/controls_r1200.parquet` |
| 2026-08-02 18:04 | charlotte | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 1726 | 250086 | 9fb32012789306c6 | `data/processed/charlotte/controls_r1600.parquet` |
| 2026-08-02 18:04 | charlotte | analysis_table_r400 | derived: 02a/02b/02c + 03a | 1726 | 440421 | 0b7114091388b23b | `data/analysis/analysis_table_charlotte_r400.parquet` |
| 2026-08-02 18:04 | charlotte | analysis_table_r800 | derived: 02a/02b/02c + 03a | 1726 | 462057 | 1f85e72ecee7c349 | `data/analysis/analysis_table_charlotte_r800.parquet` |
| 2026-08-02 18:04 | charlotte | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 1726 | 471712 | 310d596b8477a74d | `data/analysis/analysis_table_charlotte_r1200.parquet` |
| 2026-08-02 18:04 | charlotte | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 1726 | 477323 | aa3340a22e77fc4c | `data/analysis/analysis_table_charlotte_r1600.parquet` |
| 2026-08-03 16:53 | denver | catchments_r400 | derived: 01d + 01b | 3456 | 5755130 | 181958aa4c7b967b | `data/processed/denver__aadtfree/catchments_r400.parquet` |
| 2026-08-03 16:53 | denver | catchments_r800 | derived: 01d + 01b | 3456 | 5586747 | 2479097107af7395 | `data/processed/denver__aadtfree/catchments_r800.parquet` |
| 2026-08-03 16:53 | denver | catchments_r1200 | derived: 01d + 01b | 3456 | 5462515 | 0c5ca4cd5d8a4359 | `data/processed/denver__aadtfree/catchments_r1200.parquet` |
| 2026-08-03 16:53 | denver | catchments_r1600 | derived: 01d + 01b | 3456 | 5375216 | ed9a71ee6e7cdfbe | `data/processed/denver__aadtfree/catchments_r1600.parquet` |
| 2026-08-03 16:53 | denver | analysis_segments | derived: 01d | 3456 | 1192202 | d5cc3250c070b510 | `data/processed/denver__aadtfree/segments.parquet` |
| 2026-08-03 16:53 | denver | grid_1mi2 | derived: 01b | 844 | 46040 | 73a91f7e223b7ea8 | `data/processed/denver__aadtfree/grid.parquet` |
| 2026-08-03 16:53 | denver | permeability_r400 | derived: 01a local subgraph + 02a catchments | 3456 | 321048 | d1e76dbb948fd38e | `data/processed/denver__aadtfree/permeability_r400.parquet` |
| 2026-08-03 16:53 | denver | permeability_r800 | derived: 01a local subgraph + 02a catchments | 3456 | 351788 | 2cf6dc5b39c8bb08 | `data/processed/denver__aadtfree/permeability_r800.parquet` |
| 2026-08-03 16:53 | denver | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 3456 | 370321 | 4fac45b2b047b459 | `data/processed/denver__aadtfree/permeability_r1200.parquet` |
| 2026-08-03 16:53 | denver | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 3456 | 381270 | 328a22e4c8279a62 | `data/processed/denver__aadtfree/permeability_r1600.parquet` |
| 2026-08-03 16:54 | denver | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 3456 | 139169 | 3ddbfa68e901b151 | `data/processed/denver__aadtfree/through_routes_r400.parquet` |
| 2026-08-03 16:54 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3456 | 142945 | e95cb700c9131d3b | `data/processed/denver__aadtfree/through_routes_r800.parquet` |
| 2026-08-03 16:54 | denver | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 3456 | 143855 | afcc4eec131cd39b | `data/processed/denver__aadtfree/through_routes_r1200.parquet` |
| 2026-08-03 16:54 | denver | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 3456 | 144871 | 002a81ce558af75c | `data/processed/denver__aadtfree/through_routes_r1600.parquet` |
| 2026-08-03 16:55 | denver | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3456 | 513308 | c825340bc11d7bd0 | `data/processed/denver__aadtfree/controls_r400.parquet` |
| 2026-08-03 16:55 | denver | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3456 | 529054 | 9551b5dae5dc81da | `data/processed/denver__aadtfree/controls_r800.parquet` |
| 2026-08-03 16:55 | denver | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3456 | 534285 | 0e58bed623079f6d | `data/processed/denver__aadtfree/controls_r1200.parquet` |
| 2026-08-03 16:55 | denver | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3456 | 538094 | cf13e37a527abcd5 | `data/processed/denver__aadtfree/controls_r1600.parquet` |
| 2026-08-03 16:55 | denver | analysis_table_r400 | derived: 02a/02b/02c + 03a | 3456 | 855271 | e6a7793cf4d4a8a6 | `data/analysis__aadtfree/analysis_table_denver_r400.parquet` |
| 2026-08-03 16:55 | denver | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3456 | 899928 | 5bca5fe4281e7ddf | `data/analysis__aadtfree/analysis_table_denver_r800.parquet` |
| 2026-08-03 16:55 | denver | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 3456 | 919065 | 9134ea7c07f31287 | `data/analysis__aadtfree/analysis_table_denver_r1200.parquet` |
| 2026-08-03 16:55 | denver | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 3456 | 930626 | 5db02c80aec11416 | `data/analysis__aadtfree/analysis_table_denver_r1600.parquet` |
| 2026-08-03 16:55 | portland | catchments_r400 | derived: 01d + 01b | 3521 | 6279950 | 1749b1a9a4d3929d | `data/processed/portland__aadtfree/catchments_r400.parquet` |
| 2026-08-03 16:55 | portland | catchments_r800 | derived: 01d + 01b | 3521 | 5915989 | f292012e6728a03d | `data/processed/portland__aadtfree/catchments_r800.parquet` |
| 2026-08-03 16:55 | portland | catchments_r1200 | derived: 01d + 01b | 3521 | 5723687 | 2e02c3ca3f703ada | `data/processed/portland__aadtfree/catchments_r1200.parquet` |
| 2026-08-03 16:55 | portland | catchments_r1600 | derived: 01d + 01b | 3521 | 5597082 | 19d7e7cac79a07d6 | `data/processed/portland__aadtfree/catchments_r1600.parquet` |
| 2026-08-03 16:55 | portland | analysis_segments | derived: 01d | 3521 | 1440942 | 456b8d57b63214b2 | `data/processed/portland__aadtfree/segments.parquet` |
| 2026-08-03 16:55 | portland | grid_1mi2 | derived: 01b | 740 | 42569 | eb8fe4278a3dabc9 | `data/processed/portland__aadtfree/grid.parquet` |
| 2026-08-03 16:55 | portland | permeability_r400 | derived: 01a local subgraph + 02a catchments | 3521 | 323831 | 8ac2344449ea4593 | `data/processed/portland__aadtfree/permeability_r400.parquet` |
| 2026-08-03 16:55 | portland | permeability_r800 | derived: 01a local subgraph + 02a catchments | 3521 | 353575 | e86150299dda232e | `data/processed/portland__aadtfree/permeability_r800.parquet` |
| 2026-08-03 16:55 | portland | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 3521 | 373747 | 90b264720536b6b9 | `data/processed/portland__aadtfree/permeability_r1200.parquet` |
| 2026-08-03 16:55 | portland | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 3521 | 386289 | cbb1d449af48d8b2 | `data/processed/portland__aadtfree/permeability_r1600.parquet` |
| 2026-08-03 16:55 | portland | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 3521 | 137308 | ae4277095a83c9f9 | `data/processed/portland__aadtfree/through_routes_r400.parquet` |
| 2026-08-03 16:55 | portland | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3521 | 142507 | fc90d6b72a590c4a | `data/processed/portland__aadtfree/through_routes_r800.parquet` |
| 2026-08-03 16:55 | portland | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 3521 | 144073 | 244852c6effda870 | `data/processed/portland__aadtfree/through_routes_r1200.parquet` |
| 2026-08-03 16:55 | portland | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 3521 | 144963 | 117c0c93bd20957f | `data/processed/portland__aadtfree/through_routes_r1600.parquet` |
| 2026-08-03 16:56 | portland | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3521 | 516570 | 4acecbe516274e94 | `data/processed/portland__aadtfree/controls_r400.parquet` |
| 2026-08-03 16:56 | portland | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3521 | 536668 | 70aa9d93045b0846 | `data/processed/portland__aadtfree/controls_r800.parquet` |
| 2026-08-03 16:56 | portland | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3521 | 544054 | f58cbdd273e2124f | `data/processed/portland__aadtfree/controls_r1200.parquet` |
| 2026-08-03 16:56 | portland | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3521 | 547501 | 74fa7afdf57daf97 | `data/processed/portland__aadtfree/controls_r1600.parquet` |
| 2026-08-03 16:56 | portland | analysis_table_r400 | derived: 02a/02b/02c + 03a | 3521 | 874093 | 5d40e9257885c74f | `data/analysis__aadtfree/analysis_table_portland_r400.parquet` |
| 2026-08-03 16:56 | portland | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3521 | 922354 | f146411b8f3e9cfd | `data/analysis__aadtfree/analysis_table_portland_r800.parquet` |
| 2026-08-03 16:56 | portland | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 3521 | 945774 | a0f98a0e052e7d48 | `data/analysis__aadtfree/analysis_table_portland_r1200.parquet` |
| 2026-08-03 16:56 | portland | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 3521 | 958103 | 544401b204df3b05 | `data/analysis__aadtfree/analysis_table_portland_r1600.parquet` |
| 2026-08-03 16:56 | phoenix | catchments_r400 | derived: 01d + 01b | 4325 | 7083231 | 917c47b73f22bd36 | `data/processed/phoenix__aadtfree/catchments_r400.parquet` |
| 2026-08-03 16:56 | phoenix | catchments_r800 | derived: 01d + 01b | 4325 | 6987505 | 9f0e6bd097d4e3e5 | `data/processed/phoenix__aadtfree/catchments_r800.parquet` |
| 2026-08-03 16:56 | phoenix | catchments_r1200 | derived: 01d + 01b | 4325 | 6900902 | f9e4604576062739 | `data/processed/phoenix__aadtfree/catchments_r1200.parquet` |
| 2026-08-03 16:56 | phoenix | catchments_r1600 | derived: 01d + 01b | 4325 | 6829156 | 46cef5c80c8b6bc4 | `data/processed/phoenix__aadtfree/catchments_r1600.parquet` |
| 2026-08-03 16:56 | phoenix | analysis_segments | derived: 01d | 4325 | 1356792 | a1fcf139bb88b25d | `data/processed/phoenix__aadtfree/segments.parquet` |
| 2026-08-03 16:56 | phoenix | grid_1mi2 | derived: 01b | 1413 | 71025 | 12900c8ef2320d46 | `data/processed/phoenix__aadtfree/grid.parquet` |
| 2026-08-03 16:56 | phoenix | permeability_r400 | derived: 01a local subgraph + 02a catchments | 4325 | 391830 | a1e137df6b07cd55 | `data/processed/phoenix__aadtfree/permeability_r400.parquet` |
| 2026-08-03 16:56 | phoenix | permeability_r800 | derived: 01a local subgraph + 02a catchments | 4325 | 429995 | cef3fb531e9e241d | `data/processed/phoenix__aadtfree/permeability_r800.parquet` |
| 2026-08-03 16:56 | phoenix | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 4325 | 455947 | 94b1cd4b5ec4c3f0 | `data/processed/phoenix__aadtfree/permeability_r1200.parquet` |
| 2026-08-03 16:56 | phoenix | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 4325 | 468527 | 5b279f62ce3ce01b | `data/processed/phoenix__aadtfree/permeability_r1600.parquet` |
| 2026-08-03 16:56 | phoenix | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 4325 | 155250 | 524583959c479225 | `data/processed/phoenix__aadtfree/through_routes_r400.parquet` |
| 2026-08-03 16:56 | phoenix | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 4325 | 161568 | 4daad847d45fa610 | `data/processed/phoenix__aadtfree/through_routes_r800.parquet` |
| 2026-08-03 16:56 | phoenix | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 4325 | 162987 | 688db9edebc69267 | `data/processed/phoenix__aadtfree/through_routes_r1200.parquet` |
| 2026-08-03 16:56 | phoenix | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 4325 | 163490 | bd8cbaf35ed8f705 | `data/processed/phoenix__aadtfree/through_routes_r1600.parquet` |
| 2026-08-03 16:57 | phoenix | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 4325 | 596813 | 2fde895bf8f1cfff | `data/processed/phoenix__aadtfree/controls_r400.parquet` |
| 2026-08-03 16:57 | phoenix | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 4325 | 616726 | d982465cf29a06f1 | `data/processed/phoenix__aadtfree/controls_r800.parquet` |
| 2026-08-03 16:57 | phoenix | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 4325 | 623976 | 677de7fe7aa30126 | `data/processed/phoenix__aadtfree/controls_r1200.parquet` |
| 2026-08-03 16:57 | phoenix | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 4325 | 628055 | e93f1a7446de053a | `data/processed/phoenix__aadtfree/controls_r1600.parquet` |
| 2026-08-03 16:57 | phoenix | analysis_table_r400 | derived: 02a/02b/02c + 03a | 4325 | 1043968 | 8c2483b4b095b40f | `data/analysis__aadtfree/analysis_table_phoenix_r400.parquet` |
| 2026-08-03 16:57 | phoenix | analysis_table_r800 | derived: 02a/02b/02c + 03a | 4325 | 1099995 | fcf0ea76e7e7e16a | `data/analysis__aadtfree/analysis_table_phoenix_r800.parquet` |
| 2026-08-03 16:57 | phoenix | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 4325 | 1128492 | 5f51b571915b221d | `data/analysis__aadtfree/analysis_table_phoenix_r1200.parquet` |
| 2026-08-03 16:57 | phoenix | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 4325 | 1141513 | 469bbe8e2cd07115 | `data/analysis__aadtfree/analysis_table_phoenix_r1600.parquet` |
| 2026-08-03 16:58 | boston | catchments_r400 | derived: 01d + 01b | 11088 | 22031732 | 78608d2c28714428 | `data/processed/boston__aadtfree/catchments_r400.parquet` |
| 2026-08-03 16:58 | boston | catchments_r800 | derived: 01d + 01b | 11088 | 20071796 | 3bae4be375f42bbf | `data/processed/boston__aadtfree/catchments_r800.parquet` |
| 2026-08-03 16:58 | boston | catchments_r1200 | derived: 01d + 01b | 11088 | 18956930 | 7f1dd749cfbc8108 | `data/processed/boston__aadtfree/catchments_r1200.parquet` |
| 2026-08-03 16:58 | boston | catchments_r1600 | derived: 01d + 01b | 11088 | 18207375 | 82f7b9c165207876 | `data/processed/boston__aadtfree/catchments_r1600.parquet` |
| 2026-08-03 16:58 | boston | analysis_segments | derived: 01d | 11088 | 5683299 | df0fb84e99ca2298 | `data/processed/boston__aadtfree/segments.parquet` |
| 2026-08-03 16:58 | boston | grid_1mi2 | derived: 01b | 2348 | 115198 | 3687f38bd7cb522e | `data/processed/boston__aadtfree/grid.parquet` |
| 2026-08-03 16:59 | boston | permeability_r400 | derived: 01a local subgraph + 02a catchments | 11088 | 969903 | 5926202daf78e95d | `data/processed/boston__aadtfree/permeability_r400.parquet` |
| 2026-08-03 16:59 | boston | permeability_r800 | derived: 01a local subgraph + 02a catchments | 11088 | 1036892 | b35d314c635ed969 | `data/processed/boston__aadtfree/permeability_r800.parquet` |
| 2026-08-03 16:59 | boston | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 11088 | 1084948 | 611dea9cca85d0b0 | `data/processed/boston__aadtfree/permeability_r1200.parquet` |
| 2026-08-03 16:59 | boston | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 11088 | 1129734 | 3c6278c9d06440ef | `data/processed/boston__aadtfree/permeability_r1600.parquet` |
| 2026-08-03 17:00 | boston | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 11088 | 368439 | f784888e84b82cb8 | `data/processed/boston__aadtfree/through_routes_r400.parquet` |
| 2026-08-03 17:00 | boston | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 11088 | 383823 | b1802bb41c911141 | `data/processed/boston__aadtfree/through_routes_r800.parquet` |
| 2026-08-03 17:00 | boston | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 11088 | 390184 | 67bf69647e47f6a5 | `data/processed/boston__aadtfree/through_routes_r1200.parquet` |
| 2026-08-03 17:00 | boston | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 11088 | 392508 | 1e14dc58dc7c1fc9 | `data/processed/boston__aadtfree/through_routes_r1600.parquet` |
| 2026-08-03 17:00 | boston | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 11088 | 1426670 | 277cb218513e2f02 | `data/processed/boston__aadtfree/controls_r400.parquet` |
| 2026-08-03 17:00 | boston | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 11088 | 1513607 | e1a3f54606a79ab3 | `data/processed/boston__aadtfree/controls_r800.parquet` |
| 2026-08-03 17:00 | boston | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 11088 | 1554178 | 0c29b5e703cd88d9 | `data/processed/boston__aadtfree/controls_r1200.parquet` |
| 2026-08-03 17:00 | boston | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 11088 | 1575687 | a4b921762fa979e6 | `data/processed/boston__aadtfree/controls_r1600.parquet` |
| 2026-08-03 17:00 | boston | analysis_table_r400 | derived: 02a/02b/02c + 03a | 11088 | 2505428 | dd6aaa2f4303bdc5 | `data/analysis__aadtfree/analysis_table_boston_r400.parquet` |
| 2026-08-03 17:00 | boston | analysis_table_r800 | derived: 02a/02b/02c + 03a | 11088 | 2660164 | 622fe17674d4c1ca | `data/analysis__aadtfree/analysis_table_boston_r800.parquet` |
| 2026-08-03 17:00 | boston | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 11088 | 2744977 | f8e5667e86bd2533 | `data/analysis__aadtfree/analysis_table_boston_r1200.parquet` |
| 2026-08-03 17:00 | boston | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 11088 | 2802765 | b322038546010e91 | `data/analysis__aadtfree/analysis_table_boston_r1600.parquet` |
| 2026-08-03 17:01 | charlotte | catchments_r400 | derived: 01d + 01b | 1805 | 3761957 | a3b2be444a5b68d6 | `data/processed/charlotte__aadtfree/catchments_r400.parquet` |
| 2026-08-03 17:01 | charlotte | catchments_r800 | derived: 01d + 01b | 1805 | 3512530 | d1dca4940797d507 | `data/processed/charlotte__aadtfree/catchments_r800.parquet` |
| 2026-08-03 17:01 | charlotte | catchments_r1200 | derived: 01d + 01b | 1805 | 3362554 | bbbd15407aee3336 | `data/processed/charlotte__aadtfree/catchments_r1200.parquet` |
| 2026-08-03 17:01 | charlotte | catchments_r1600 | derived: 01d + 01b | 1805 | 3256030 | c78c96a2d98f5e82 | `data/processed/charlotte__aadtfree/catchments_r1600.parquet` |
| 2026-08-03 17:01 | charlotte | analysis_segments | derived: 01d | 1805 | 938623 | 644d601b41a5792d | `data/processed/charlotte__aadtfree/segments.parquet` |
| 2026-08-03 17:01 | charlotte | grid_1mi2 | derived: 01b | 903 | 49168 | f7c95e95ddcdc1a9 | `data/processed/charlotte__aadtfree/grid.parquet` |
| 2026-08-03 17:01 | charlotte | permeability_r400 | derived: 01a local subgraph + 02a catchments | 1805 | 170564 | 259c26704e70a731 | `data/processed/charlotte__aadtfree/permeability_r400.parquet` |
| 2026-08-03 17:01 | charlotte | permeability_r800 | derived: 01a local subgraph + 02a catchments | 1805 | 186989 | 331c235836f41a0a | `data/processed/charlotte__aadtfree/permeability_r800.parquet` |
| 2026-08-03 17:01 | charlotte | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 1805 | 197619 | 3937ffcc36300325 | `data/processed/charlotte__aadtfree/permeability_r1200.parquet` |
| 2026-08-03 17:01 | charlotte | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 1805 | 204588 | cac3b2268d809af3 | `data/processed/charlotte__aadtfree/permeability_r1600.parquet` |
| 2026-08-03 17:01 | charlotte | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 1805 | 64195 | d1064c08111a50c7 | `data/processed/charlotte__aadtfree/through_routes_r400.parquet` |
| 2026-08-03 17:01 | charlotte | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 1805 | 66984 | 10cedbd71663eaeb | `data/processed/charlotte__aadtfree/through_routes_r800.parquet` |
| 2026-08-03 17:01 | charlotte | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 1805 | 67654 | 814807bd7cb4b24f | `data/processed/charlotte__aadtfree/through_routes_r1200.parquet` |
| 2026-08-03 17:01 | charlotte | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 1805 | 68280 | 201e1693886b5ff3 | `data/processed/charlotte__aadtfree/through_routes_r1600.parquet` |
| 2026-08-03 17:01 | charlotte | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 1805 | 248689 | 3da6fd06b6b5df4d | `data/processed/charlotte__aadtfree/controls_r400.parquet` |
| 2026-08-03 17:01 | charlotte | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 1805 | 257245 | b2bc416cb942f7c5 | `data/processed/charlotte__aadtfree/controls_r800.parquet` |
| 2026-08-03 17:01 | charlotte | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 1805 | 260166 | 4ae678c0d7f1e3dc | `data/processed/charlotte__aadtfree/controls_r1200.parquet` |
| 2026-08-03 17:01 | charlotte | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 1805 | 260866 | 3d1d717224354a90 | `data/processed/charlotte__aadtfree/controls_r1600.parquet` |
| 2026-08-03 17:01 | charlotte | analysis_table_r400 | derived: 02a/02b/02c + 03a | 1805 | 431602 | 6bdc1594fe8dbd81 | `data/analysis__aadtfree/analysis_table_charlotte_r400.parquet` |
| 2026-08-03 17:01 | charlotte | analysis_table_r800 | derived: 02a/02b/02c + 03a | 1805 | 455801 | 9e5ea58ae40b4a6a | `data/analysis__aadtfree/analysis_table_charlotte_r800.parquet` |
| 2026-08-03 17:01 | charlotte | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 1805 | 467069 | 6d725fb3f2dc8e2c | `data/analysis__aadtfree/analysis_table_charlotte_r1200.parquet` |
| 2026-08-03 17:01 | charlotte | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 1805 | 472383 | ea067b26eca8b0f0 | `data/analysis__aadtfree/analysis_table_charlotte_r1600.parquet` |
| 2026-08-03 17:01 | wasatch_front | catchments_r400 | derived: 01d + 01b | 2996 | 4583868 | 1616dfad76f15ef4 | `data/processed/wasatch_front__aadtfree/catchments_r400.parquet` |
| 2026-08-03 17:01 | wasatch_front | catchments_r800 | derived: 01d + 01b | 2996 | 4451759 | 3c44e5c94f29714b | `data/processed/wasatch_front__aadtfree/catchments_r800.parquet` |
| 2026-08-03 17:01 | wasatch_front | catchments_r1200 | derived: 01d + 01b | 2996 | 4399551 | a7f6f51f820b938e | `data/processed/wasatch_front__aadtfree/catchments_r1200.parquet` |
| 2026-08-03 17:01 | wasatch_front | catchments_r1600 | derived: 01d + 01b | 2996 | 4348510 | 1ed7d4b30494a082 | `data/processed/wasatch_front__aadtfree/catchments_r1600.parquet` |
| 2026-08-03 17:01 | wasatch_front | analysis_segments | derived: 01d | 2996 | 814494 | 58e7bcf80678c0dd | `data/processed/wasatch_front__aadtfree/segments.parquet` |
| 2026-08-03 17:01 | wasatch_front | grid_1mi2 | derived: 01b | 933 | 51900 | ed95cfc13a3a8cd2 | `data/processed/wasatch_front__aadtfree/grid.parquet` |
| 2026-08-03 17:01 | wasatch_front | permeability_r400 | derived: 01a local subgraph + 02a catchments | 2996 | 280346 | c6f0ea8ec2fe9c13 | `data/processed/wasatch_front__aadtfree/permeability_r400.parquet` |
| 2026-08-03 17:01 | wasatch_front | permeability_r800 | derived: 01a local subgraph + 02a catchments | 2996 | 306518 | 4961748460da5ffe | `data/processed/wasatch_front__aadtfree/permeability_r800.parquet` |
| 2026-08-03 17:01 | wasatch_front | permeability_r1200 | derived: 01a local subgraph + 02a catchments | 2996 | 323807 | 05848be8009e8c50 | `data/processed/wasatch_front__aadtfree/permeability_r1200.parquet` |
| 2026-08-03 17:01 | wasatch_front | permeability_r1600 | derived: 01a local subgraph + 02a catchments | 2996 | 333140 | 737774dd3d94b40c | `data/processed/wasatch_front__aadtfree/permeability_r1600.parquet` |
| 2026-08-03 17:02 | wasatch_front | through_routes_r400 | derived: 01a local/major subgraphs + 02a catchments | 2996 | 110504 | bc30c7ec0ebb0ac6 | `data/processed/wasatch_front__aadtfree/through_routes_r400.parquet` |
| 2026-08-03 17:02 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2996 | 114196 | eadb634f8c367ee3 | `data/processed/wasatch_front__aadtfree/through_routes_r800.parquet` |
| 2026-08-03 17:02 | wasatch_front | through_routes_r1200 | derived: 01a local/major subgraphs + 02a catchments | 2996 | 115389 | 539958b4654b4f17 | `data/processed/wasatch_front__aadtfree/through_routes_r1200.parquet` |
| 2026-08-03 17:02 | wasatch_front | through_routes_r1600 | derived: 01a local/major subgraphs + 02a catchments | 2996 | 115894 | a091b74aded6b96c | `data/processed/wasatch_front__aadtfree/through_routes_r1600.parquet` |
| 2026-08-03 17:02 | wasatch_front | controls_r400 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2996 | 435452 | 07a4b5eb2b7223d1 | `data/processed/wasatch_front__aadtfree/controls_r400.parquet` |
| 2026-08-03 17:02 | wasatch_front | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2996 | 450661 | dd98a82482fe89b3 | `data/processed/wasatch_front__aadtfree/controls_r800.parquet` |
| 2026-08-03 17:02 | wasatch_front | controls_r1200 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2996 | 457223 | 5508d6d2d19c990c | `data/processed/wasatch_front__aadtfree/controls_r1200.parquet` |
| 2026-08-03 17:02 | wasatch_front | controls_r1600 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2996 | 459325 | 8dbfa95f4d57cb12 | `data/processed/wasatch_front__aadtfree/controls_r1600.parquet` |
| 2026-08-03 17:02 | wasatch_front | analysis_table_r400 | derived: 02a/02b/02c + 03a | 2996 | 750387 | 5f7870adad5d70ce | `data/analysis__aadtfree/analysis_table_wasatch_front_r400.parquet` |
| 2026-08-03 17:02 | wasatch_front | analysis_table_r800 | derived: 02a/02b/02c + 03a | 2996 | 790076 | 971ade05ecd0af7b | `data/analysis__aadtfree/analysis_table_wasatch_front_r800.parquet` |
| 2026-08-03 17:02 | wasatch_front | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 2996 | 810470 | 5c590435bc3f5c1d | `data/analysis__aadtfree/analysis_table_wasatch_front_r1200.parquet` |
| 2026-08-03 17:02 | wasatch_front | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 2996 | 818895 | d777804f8a96a88b | `data/analysis__aadtfree/analysis_table_wasatch_front_r1600.parquet` |
| 2026-08-03 17:12 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 139971 | aa1971696447b47e | `data/processed/denver__ablall/through_routes_r800.parquet` |
| 2026-08-03 17:13 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 139971 | aa1971696447b47e | `data/processed/denver__ablall/through_routes_r800.parquet` |
| 2026-08-03 17:13 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 141789 | 8a014acb68371b8b | `data/processed/denver__ablnocap/through_routes_r800.parquet` |
| 2026-08-03 17:13 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 126222 | 990719b6ca6cda6b | `data/processed/denver__ablnospan/through_routes_r800.parquet` |
| 2026-08-03 17:13 | portland | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3478 | 161860 | df636bc9c5c4e25e | `data/processed/portland__ablall/through_routes_r800.parquet` |
| 2026-08-03 17:13 | portland | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3478 | 158254 | ea723055178cf612 | `data/processed/portland__ablnocap/through_routes_r800.parquet` |
| 2026-08-03 17:13 | portland | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3478 | 145866 | 7e73b71fa24f025c | `data/processed/portland__ablnospan/through_routes_r800.parquet` |
| 2026-08-03 17:14 | phoenix | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3941 | 165982 | 78659a7aecc9ffeb | `data/processed/phoenix__ablall/through_routes_r800.parquet` |
| 2026-08-03 17:14 | phoenix | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3941 | 165208 | 9d3b3e01fde897e2 | `data/processed/phoenix__ablnocap/through_routes_r800.parquet` |
| 2026-08-03 17:14 | phoenix | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3941 | 146032 | 1d3e27da3df383eb | `data/processed/phoenix__ablnospan/through_routes_r800.parquet` |
| 2026-08-03 17:15 | boston | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 24774 | 872145 | b6408bdb393af0a2 | `data/processed/boston__ablall/through_routes_r800.parquet` |
| 2026-08-03 17:15 | boston | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 24774 | 950393 | a2cfa3fc1deaa2cb | `data/processed/boston__ablnocap/through_routes_r800.parquet` |
| 2026-08-03 17:16 | boston | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 24774 | 799023 | 8bec62cbeb13a2cf | `data/processed/boston__ablnospan/through_routes_r800.parquet` |
| 2026-08-03 17:16 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 114063 | 15625ef878b7cbc3 | `data/processed/wasatch_front__ablall/through_routes_r800.parquet` |
| 2026-08-03 17:16 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 104043 | 4393246bee04f76a | `data/processed/wasatch_front__ablnocap/through_routes_r800.parquet` |
| 2026-08-03 17:16 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 93343 | fc6e743a23a0a7a2 | `data/processed/wasatch_front__ablnospan/through_routes_r800.parquet` |
| 2026-08-03 17:16 | charlotte | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 1726 | 72686 | afed2317ad6b72bc | `data/processed/charlotte__ablall/through_routes_r800.parquet` |
| 2026-08-03 17:16 | charlotte | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 1726 | 73471 | 9ea9d9b5004a3359 | `data/processed/charlotte__ablnocap/through_routes_r800.parquet` |
| 2026-08-03 17:16 | charlotte | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 1726 | 66527 | bcc38db76fb689e5 | `data/processed/charlotte__ablnospan/through_routes_r800.parquet` |
| 2026-08-03 17:18 | denver | catchments_r400 | derived: 01d + 01b | 3265 | 5665828 | f424a3616dc32bb9 | `data/processed/denver__oneway/catchments_r400.parquet` |
| 2026-08-03 17:18 | denver | catchments_r800 | derived: 01d + 01b | 3265 | 5468605 | 46c6ad2c3881b107 | `data/processed/denver__oneway/catchments_r800.parquet` |
| 2026-08-03 17:18 | denver | catchments_r1200 | derived: 01d + 01b | 3265 | 5358559 | 6bd5eb5f0f15914b | `data/processed/denver__oneway/catchments_r1200.parquet` |
| 2026-08-03 17:18 | denver | catchments_r1600 | derived: 01d + 01b | 3265 | 5258177 | e060ec736f2c175f | `data/processed/denver__oneway/catchments_r1600.parquet` |
| 2026-08-03 17:18 | denver | analysis_segments | derived: 01d | 3265 | 1229424 | 5146c9b515bbd7c8 | `data/processed/denver__oneway/segments.parquet` |
| 2026-08-03 17:18 | denver | grid_1mi2 | derived: 01b | 844 | 46040 | 73a91f7e223b7ea8 | `data/processed/denver__oneway/grid.parquet` |
| 2026-08-03 17:18 | denver | permeability_r800 | derived: 01a local subgraph + 02a catchments | 3265 | 335847 | c9da99bb00f6bccc | `data/processed/denver__oneway/permeability_r800.parquet` |
| 2026-08-03 17:19 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3265 | 135233 | c37aa05055dc804c | `data/processed/denver__oneway/through_routes_r800.parquet` |
| 2026-08-03 17:19 | denver | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3265 | 503752 | 9c7860aa8d4c4b8e | `data/processed/denver__oneway/controls_r800.parquet` |
| 2026-08-03 17:19 | denver | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3265 | 846510 | 8262fe1746f1d9a4 | `data/analysis__oneway/analysis_table_denver_r800.parquet` |
| 2026-08-03 17:19 | portland | catchments_r400 | derived: 01d + 01b | 3776 | 6628419 | 0ecefa8a73a1fee8 | `data/processed/portland__oneway/catchments_r400.parquet` |
| 2026-08-03 17:19 | portland | catchments_r800 | derived: 01d + 01b | 3776 | 6287764 | db186f4e7e8d9476 | `data/processed/portland__oneway/catchments_r800.parquet` |
| 2026-08-03 17:19 | portland | catchments_r1200 | derived: 01d + 01b | 3776 | 6097426 | 38bb901017846e4c | `data/processed/portland__oneway/catchments_r1200.parquet` |
| 2026-08-03 17:19 | portland | catchments_r1600 | derived: 01d + 01b | 3776 | 5965005 | edda167eae2c502e | `data/processed/portland__oneway/catchments_r1600.parquet` |
| 2026-08-03 17:19 | portland | analysis_segments | derived: 01d | 3776 | 1480208 | e023a676042a7d35 | `data/processed/portland__oneway/segments.parquet` |
| 2026-08-03 17:19 | portland | grid_1mi2 | derived: 01b | 740 | 42569 | eb8fe4278a3dabc9 | `data/processed/portland__oneway/grid.parquet` |
| 2026-08-03 17:19 | portland | permeability_r800 | derived: 01a local subgraph + 02a catchments | 3776 | 380487 | 31c2fa921be2446d | `data/processed/portland__oneway/permeability_r800.parquet` |
| 2026-08-03 17:19 | portland | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3776 | 152835 | c8c8e672dbdafe93 | `data/processed/portland__oneway/through_routes_r800.parquet` |
| 2026-08-03 17:19 | portland | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 3776 | 576277 | 9012895443f74222 | `data/processed/portland__oneway/controls_r800.parquet` |
| 2026-08-03 17:19 | portland | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3776 | 980292 | cc12b616f51021a3 | `data/analysis__oneway/analysis_table_portland_r800.parquet` |
| 2026-08-03 17:19 | phoenix | catchments_r400 | derived: 01d + 01b | 4008 | 6783356 | 2eccbdb802c00c57 | `data/processed/phoenix__oneway/catchments_r400.parquet` |
| 2026-08-03 17:19 | phoenix | catchments_r800 | derived: 01d + 01b | 4008 | 6662151 | c36fd16350518540 | `data/processed/phoenix__oneway/catchments_r800.parquet` |
| 2026-08-03 17:19 | phoenix | catchments_r1200 | derived: 01d + 01b | 4008 | 6587445 | 9531d83d9e4ebe9c | `data/processed/phoenix__oneway/catchments_r1200.parquet` |
| 2026-08-03 17:19 | phoenix | catchments_r1600 | derived: 01d + 01b | 4008 | 6516440 | d5f59b56752bb294 | `data/processed/phoenix__oneway/catchments_r1600.parquet` |
| 2026-08-03 17:19 | phoenix | analysis_segments | derived: 01d | 4008 | 1333508 | 2b2291b35f6ea414 | `data/processed/phoenix__oneway/segments.parquet` |
| 2026-08-03 17:19 | phoenix | grid_1mi2 | derived: 01b | 1413 | 71025 | 12900c8ef2320d46 | `data/processed/phoenix__oneway/grid.parquet` |
| 2026-08-03 17:19 | phoenix | permeability_r800 | derived: 01a local subgraph + 02a catchments | 4008 | 398411 | 12089d50482f0e52 | `data/processed/phoenix__oneway/permeability_r800.parquet` |
| 2026-08-03 17:20 | phoenix | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 4008 | 147473 | 8a1ac303cad5c3c6 | `data/processed/phoenix__oneway/through_routes_r800.parquet` |
| 2026-08-03 17:20 | phoenix | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 4008 | 566446 | e982a2febdb5769a | `data/processed/phoenix__oneway/controls_r800.parquet` |
| 2026-08-03 17:20 | phoenix | analysis_table_r800 | derived: 02a/02b/02c + 03a | 4008 | 1010037 | 9c0401c7fcc6d3f9 | `data/analysis__oneway/analysis_table_phoenix_r800.parquet` |
| 2026-08-03 17:24 | boston | catchments_r400 | derived: 01d + 01b | 26181 | 38152344 | b33c1696a87a8570 | `data/processed/boston__oneway/catchments_r400.parquet` |
| 2026-08-03 17:24 | boston | catchments_r800 | derived: 01d + 01b | 26181 | 36685106 | 607e3374a8abc780 | `data/processed/boston__oneway/catchments_r800.parquet` |
| 2026-08-03 17:24 | boston | catchments_r1200 | derived: 01d + 01b | 26181 | 35890377 | a7890ac16c431394 | `data/processed/boston__oneway/catchments_r1200.parquet` |
| 2026-08-03 17:24 | boston | catchments_r1600 | derived: 01d + 01b | 26181 | 35338104 | 7f315f26fb6014ee | `data/processed/boston__oneway/catchments_r1600.parquet` |
| 2026-08-03 17:24 | boston | analysis_segments | derived: 01d | 26181 | 6468949 | 610bfa211b11b1d0 | `data/processed/boston__oneway/segments.parquet` |
| 2026-08-03 17:24 | boston | grid_1mi2 | derived: 01b | 2348 | 115198 | 3687f38bd7cb522e | `data/processed/boston__oneway/grid.parquet` |
| 2026-08-03 17:24 | boston | permeability_r800 | derived: 01a local subgraph + 02a catchments | 26181 | 2338762 | edf25c9fa994a321 | `data/processed/boston__oneway/permeability_r800.parquet` |
| 2026-08-03 17:24 | boston | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 26181 | 841766 | aeb2a4f7291e3839 | `data/processed/boston__oneway/through_routes_r800.parquet` |
| 2026-08-03 17:25 | boston | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 26181 | 3564315 | aaf825b1f9f53da5 | `data/processed/boston__oneway/controls_r800.parquet` |
| 2026-08-03 17:25 | boston | analysis_table_r800 | derived: 02a/02b/02c + 03a | 26181 | 5979227 | 858cdfaa5c4a2b71 | `data/analysis__oneway/analysis_table_boston_r800.parquet` |
| 2026-08-03 17:25 | wasatch_front | catchments_r400 | derived: 01d + 01b | 2398 | 3951161 | 0fd5d340ef10f392 | `data/processed/wasatch_front__oneway/catchments_r400.parquet` |
| 2026-08-03 17:25 | wasatch_front | catchments_r800 | derived: 01d + 01b | 2398 | 3824990 | 11adb6e4052788b8 | `data/processed/wasatch_front__oneway/catchments_r800.parquet` |
| 2026-08-03 17:25 | wasatch_front | catchments_r1200 | derived: 01d + 01b | 2398 | 3745572 | bfa009ed047ef865 | `data/processed/wasatch_front__oneway/catchments_r1200.parquet` |
| 2026-08-03 17:25 | wasatch_front | catchments_r1600 | derived: 01d + 01b | 2398 | 3684026 | 5bb5d1fa03a2b8e3 | `data/processed/wasatch_front__oneway/catchments_r1600.parquet` |
| 2026-08-03 17:25 | wasatch_front | analysis_segments | derived: 01d | 2398 | 788649 | 520fb4efc053b7a8 | `data/processed/wasatch_front__oneway/segments.parquet` |
| 2026-08-03 17:25 | wasatch_front | grid_1mi2 | derived: 01b | 933 | 51900 | ed95cfc13a3a8cd2 | `data/processed/wasatch_front__oneway/grid.parquet` |
| 2026-08-03 17:25 | wasatch_front | permeability_r800 | derived: 01a local subgraph + 02a catchments | 2398 | 252633 | a9de967ade458618 | `data/processed/wasatch_front__oneway/permeability_r800.parquet` |
| 2026-08-03 17:25 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2398 | 93455 | 989b578bde06aa73 | `data/processed/wasatch_front__oneway/through_routes_r800.parquet` |
| 2026-08-03 17:25 | wasatch_front | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 2398 | 363888 | b4a2447cc73267dc | `data/processed/wasatch_front__oneway/controls_r800.parquet` |
| 2026-08-03 17:25 | wasatch_front | analysis_table_r800 | derived: 02a/02b/02c + 03a | 2398 | 643894 | 0088a7a3f83943de | `data/analysis__oneway/analysis_table_wasatch_front_r800.parquet` |
| 2026-08-03 17:25 | charlotte | catchments_r400 | derived: 01d + 01b | 1762 | 3703360 | ff563f6789ecd561 | `data/processed/charlotte__oneway/catchments_r400.parquet` |
| 2026-08-03 17:25 | charlotte | catchments_r800 | derived: 01d + 01b | 1762 | 3472438 | c4da30de26998c1b | `data/processed/charlotte__oneway/catchments_r800.parquet` |
| 2026-08-03 17:25 | charlotte | catchments_r1200 | derived: 01d + 01b | 1762 | 3312957 | fbe4f86d4c266c81 | `data/processed/charlotte__oneway/catchments_r1200.parquet` |
| 2026-08-03 17:25 | charlotte | catchments_r1600 | derived: 01d + 01b | 1762 | 3203664 | a467b343bc1ecf65 | `data/processed/charlotte__oneway/catchments_r1600.parquet` |
| 2026-08-03 17:25 | charlotte | analysis_segments | derived: 01d | 1762 | 940131 | aa02359ce2c253eb | `data/processed/charlotte__oneway/segments.parquet` |
| 2026-08-03 17:25 | charlotte | grid_1mi2 | derived: 01b | 903 | 49168 | f7c95e95ddcdc1a9 | `data/processed/charlotte__oneway/grid.parquet` |
| 2026-08-03 17:25 | charlotte | permeability_r800 | derived: 01a local subgraph + 02a catchments | 1762 | 183591 | a6f9d283b33c8db5 | `data/processed/charlotte__oneway/permeability_r800.parquet` |
| 2026-08-03 17:25 | charlotte | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 1762 | 66733 | 197c080a781b5c73 | `data/processed/charlotte__oneway/through_routes_r800.parquet` |
| 2026-08-03 17:25 | charlotte | controls_r800 | derived: 01c ACS + 01e LODES/POI + 01f footprints | 1762 | 252178 | 6ae7a92ba637dcf5 | `data/processed/charlotte__oneway/controls_r800.parquet` |
| 2026-08-03 17:25 | charlotte | analysis_table_r800 | derived: 02a/02b/02c + 03a | 1762 | 437212 | 22c9e04d4cf30880 | `data/analysis__oneway/analysis_table_charlotte_r800.parquet` |
| 2026-08-03 17:28 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 106396 | f38245b4610748db | `data/processed/denver__ar100/through_routes_r800.parquet` |
| 2026-08-03 17:28 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2964 | 130358 | b6fbbadea4ff026a | `data/processed/denver__ar300/through_routes_r800.parquet` |
| 2026-08-03 17:28 | portland | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3478 | 126738 | 59add20bd272c6bd | `data/processed/portland__ar100/through_routes_r800.parquet` |
| 2026-08-03 17:28 | portland | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3478 | 145340 | 3594ce86ec575ec3 | `data/processed/portland__ar300/through_routes_r800.parquet` |
| 2026-08-03 17:28 | phoenix | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3941 | 126117 | c9ca58173f217a53 | `data/processed/phoenix__ar100/through_routes_r800.parquet` |
| 2026-08-03 17:28 | phoenix | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3941 | 160448 | 72cbcf7c32803aae | `data/processed/phoenix__ar300/through_routes_r800.parquet` |
| 2026-08-03 17:29 | boston | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 24774 | 761097 | 779dea92bc4534c2 | `data/processed/boston__ar100/through_routes_r800.parquet` |
| 2026-08-03 17:29 | boston | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 24774 | 785872 | 0443836310f1b533 | `data/processed/boston__ar300/through_routes_r800.parquet` |
| 2026-08-03 17:29 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 77437 | 09be5d67173edcb6 | `data/processed/wasatch_front__ar100/through_routes_r800.parquet` |
| 2026-08-03 17:29 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2372 | 102266 | 02756ab803d161d7 | `data/processed/wasatch_front__ar300/through_routes_r800.parquet` |
| 2026-08-03 17:30 | charlotte | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 1726 | 57347 | 7dbd7c38462430b0 | `data/processed/charlotte__ar100/through_routes_r800.parquet` |
| 2026-08-03 17:30 | charlotte | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 1726 | 68354 | d0cf45b303801395 | `data/processed/charlotte__ar300/through_routes_r800.parquet` |
| 2026-08-03 19:11 | denver | betweenness_transfer_aadtfree | derived: 02c on the primary frame | 2688 | 45163 | 0ba05c84d52624f3 | `data/processed/denver__aadtfree/segment_betweenness.parquet` |
| 2026-08-03 19:11 | portland | betweenness_transfer_aadtfree | derived: 02c on the primary frame | 2986 | 47589 | c6faaa3874272374 | `data/processed/portland__aadtfree/segment_betweenness.parquet` |
| 2026-08-03 19:11 | phoenix | betweenness_transfer_aadtfree | derived: 02c on the primary frame | 3307 | 56779 | bdaf87259b7a9766 | `data/processed/phoenix__aadtfree/segment_betweenness.parquet` |
| 2026-08-03 19:11 | boston | betweenness_transfer_aadtfree | derived: 02c on the primary frame | 9667 | 150186 | 32bca9b3c70f2cd6 | `data/processed/boston__aadtfree/segment_betweenness.parquet` |
| 2026-08-03 19:11 | wasatch_front | betweenness_transfer_aadtfree | derived: 02c on the primary frame | 2145 | 36983 | 9d00d239b46fd3fb | `data/processed/wasatch_front__aadtfree/segment_betweenness.parquet` |
| 2026-08-03 19:11 | charlotte | betweenness_transfer_aadtfree | derived: 02c on the primary frame | 1415 | 23684 | 100d516758d2394f | `data/processed/charlotte__aadtfree/segment_betweenness.parquet` |
| 2026-08-03 19:11 | denver | analysis_table_r400 | derived: 02a/02b/02c + 03a | 3456 | 879196 | 4419f1e162e45882 | `data/analysis__aadtfree/analysis_table_denver_r400.parquet` |
| 2026-08-03 19:11 | denver | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3456 | 923853 | 69a66090fef2f11c | `data/analysis__aadtfree/analysis_table_denver_r800.parquet` |
| 2026-08-03 19:11 | denver | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 3456 | 942990 | b8266d9f2e0ac52a | `data/analysis__aadtfree/analysis_table_denver_r1200.parquet` |
| 2026-08-03 19:11 | denver | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 3456 | 954551 | 0607dd3e9e78b224 | `data/analysis__aadtfree/analysis_table_denver_r1600.parquet` |
| 2026-08-03 19:11 | portland | analysis_table_r400 | derived: 02a/02b/02c + 03a | 3521 | 900099 | 74f2ed9f7aaab510 | `data/analysis__aadtfree/analysis_table_portland_r400.parquet` |
| 2026-08-03 19:11 | portland | analysis_table_r800 | derived: 02a/02b/02c + 03a | 3521 | 948360 | bcf5a3277bddb5c6 | `data/analysis__aadtfree/analysis_table_portland_r800.parquet` |
| 2026-08-03 19:11 | portland | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 3521 | 971780 | a241c935299ecc38 | `data/analysis__aadtfree/analysis_table_portland_r1200.parquet` |
| 2026-08-03 19:11 | portland | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 3521 | 984109 | 6c6b7f0c75d2977f | `data/analysis__aadtfree/analysis_table_portland_r1600.parquet` |
| 2026-08-03 19:11 | phoenix | analysis_table_r400 | derived: 02a/02b/02c + 03a | 4325 | 1073829 | d098fea3024d50b0 | `data/analysis__aadtfree/analysis_table_phoenix_r400.parquet` |
| 2026-08-03 19:11 | phoenix | analysis_table_r800 | derived: 02a/02b/02c + 03a | 4325 | 1129858 | 8fd239feb5431585 | `data/analysis__aadtfree/analysis_table_phoenix_r800.parquet` |
| 2026-08-03 19:11 | phoenix | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 4325 | 1158354 | 1b912510be87c368 | `data/analysis__aadtfree/analysis_table_phoenix_r1200.parquet` |
| 2026-08-03 19:11 | phoenix | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 4325 | 1171381 | 4e6c7db270f5be62 | `data/analysis__aadtfree/analysis_table_phoenix_r1600.parquet` |
| 2026-08-03 19:11 | boston | analysis_table_r400 | derived: 02a/02b/02c + 03a | 11088 | 2585047 | d04ddf9f5f70eb9b | `data/analysis__aadtfree/analysis_table_boston_r400.parquet` |
| 2026-08-03 19:11 | boston | analysis_table_r800 | derived: 02a/02b/02c + 03a | 11088 | 2739783 | 1fd2d6ec6acf9684 | `data/analysis__aadtfree/analysis_table_boston_r800.parquet` |
| 2026-08-03 19:11 | boston | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 11088 | 2824596 | 6a21e18c76983e39 | `data/analysis__aadtfree/analysis_table_boston_r1200.parquet` |
| 2026-08-03 19:11 | boston | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 11088 | 2882384 | b1f3b152bc0dd70a | `data/analysis__aadtfree/analysis_table_boston_r1600.parquet` |
| 2026-08-03 19:11 | wasatch_front | analysis_table_r400 | derived: 02a/02b/02c + 03a | 2996 | 769458 | 2e8bf3c47bc95383 | `data/analysis__aadtfree/analysis_table_wasatch_front_r400.parquet` |
| 2026-08-03 19:11 | wasatch_front | analysis_table_r800 | derived: 02a/02b/02c + 03a | 2996 | 809147 | 4db466529c360635 | `data/analysis__aadtfree/analysis_table_wasatch_front_r800.parquet` |
| 2026-08-03 19:11 | wasatch_front | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 2996 | 829541 | bf2f01b3310c947d | `data/analysis__aadtfree/analysis_table_wasatch_front_r1200.parquet` |
| 2026-08-03 19:11 | wasatch_front | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 2996 | 837966 | 96ee4de0c7a39b86 | `data/analysis__aadtfree/analysis_table_wasatch_front_r1600.parquet` |
| 2026-08-03 19:12 | charlotte | analysis_table_r400 | derived: 02a/02b/02c + 03a | 1805 | 444577 | d189953cc290b39b | `data/analysis__aadtfree/analysis_table_charlotte_r400.parquet` |
| 2026-08-03 19:12 | charlotte | analysis_table_r800 | derived: 02a/02b/02c + 03a | 1805 | 468776 | 68d8260cc5810f4e | `data/analysis__aadtfree/analysis_table_charlotte_r800.parquet` |
| 2026-08-03 19:12 | charlotte | analysis_table_r1200 | derived: 02a/02b/02c + 03a | 1805 | 480044 | bc7e95c2ed1e8cfb | `data/analysis__aadtfree/analysis_table_charlotte_r1200.parquet` |
| 2026-08-03 19:12 | charlotte | analysis_table_r1600 | derived: 02a/02b/02c + 03a | 1805 | 485358 | 8ddf07ca4a356c4b | `data/analysis__aadtfree/analysis_table_charlotte_r1600.parquet` |
| 2026-08-03 19:52 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3456 | 159647 | 6e579aadb5d2af6d | `data/processed/denver__af_ablall/through_routes_r800.parquet` |
| 2026-08-03 19:52 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3456 | 167181 | 7a6f6dbdffae4356 | `data/processed/denver__af_ablnocap/through_routes_r800.parquet` |
| 2026-08-03 19:52 | denver | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3456 | 145680 | 7203dec0509dc3e4 | `data/processed/denver__af_ablnospan/through_routes_r800.parquet` |
| 2026-08-03 19:53 | portland | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3521 | 163010 | 85974c451057192d | `data/processed/portland__af_ablall/through_routes_r800.parquet` |
| 2026-08-03 19:53 | portland | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3521 | 160720 | 8dbc56893c4fac88 | `data/processed/portland__af_ablnocap/through_routes_r800.parquet` |
| 2026-08-03 19:53 | portland | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 3521 | 146977 | 68f7474e0b882322 | `data/processed/portland__af_ablnospan/through_routes_r800.parquet` |
| 2026-08-03 19:53 | phoenix | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 4325 | 181411 | 3174c3dd79857171 | `data/processed/phoenix__af_ablall/through_routes_r800.parquet` |
| 2026-08-03 19:53 | phoenix | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 4325 | 189587 | 16b7c245a27b94b5 | `data/processed/phoenix__af_ablnocap/through_routes_r800.parquet` |
| 2026-08-03 19:53 | phoenix | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 4325 | 163863 | 73310e0d4f27a8ae | `data/processed/phoenix__af_ablnospan/through_routes_r800.parquet` |
| 2026-08-03 19:54 | boston | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 11088 | 462053 | a8ca04d18c48ab35 | `data/processed/boston__af_ablall/through_routes_r800.parquet` |
| 2026-08-03 19:54 | boston | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 11088 | 425743 | ed9f94c8207c3424 | `data/processed/boston__af_ablnocap/through_routes_r800.parquet` |
| 2026-08-03 19:54 | boston | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 11088 | 392375 | d203e8bda01dd201 | `data/processed/boston__af_ablnospan/through_routes_r800.parquet` |
| 2026-08-03 19:54 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2996 | 134560 | 3d6bff2997a12e5e | `data/processed/wasatch_front__af_ablall/through_routes_r800.parquet` |
| 2026-08-03 19:55 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2996 | 133709 | c07733ce47cca24d | `data/processed/wasatch_front__af_ablnocap/through_routes_r800.parquet` |
| 2026-08-03 19:55 | wasatch_front | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 2996 | 115336 | ce0ddf19012e139b | `data/processed/wasatch_front__af_ablnospan/through_routes_r800.parquet` |
| 2026-08-03 19:55 | charlotte | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 1805 | 73860 | e90c999c9543975c | `data/processed/charlotte__af_ablall/through_routes_r800.parquet` |
| 2026-08-03 19:55 | charlotte | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 1805 | 76365 | 2ed5be23de0022ba | `data/processed/charlotte__af_ablnocap/through_routes_r800.parquet` |
| 2026-08-03 19:55 | charlotte | through_routes_r800 | derived: 01a local/major subgraphs + 02a catchments | 1805 | 67842 | fbbbd8668c6a285a | `data/processed/charlotte__af_ablnospan/through_routes_r800.parquet` |
