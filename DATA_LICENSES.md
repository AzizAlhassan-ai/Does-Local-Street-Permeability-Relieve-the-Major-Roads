# Data licences and attribution

The MIT licence in `LICENSE` applies to the original research code and its associated software documentation. It does not replace the licences of the datasets.

| Material | Source and applicable terms |
|---|---|
| OpenStreetMap street networks and points of interest | © OpenStreetMap contributors; [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/). See [OSM copyright and attribution](https://www.openstreetmap.org/copyright). |
| OSM-derived processed networks and analysis databases | Distributed subject to ODbL obligations applicable to the underlying OSM database and derivative databases. Preserve attribution and applicable share-alike terms when redistributing. |
| Microsoft Global Building Footprints | Microsoft; [Global ML Building Footprints](https://github.com/microsoft/GlobalMLBuildingFootprints), distributed under [CDLA Permissive 2.0](LICENSES/CDLA-Permissive-2.0.txt). |
| FHWA HPMS 2018 and BTS/NTAD HPMS 2024 | US federal government data; public domain as identified in the original project licence. Retain source and year when citing. |
| US Census TIGER/Line geography, ACS estimates and LEHD LODES | US federal government data; public domain as identified in the original project licence. Retain programme and vintage when citing. |

The analysis databases combine measures derived from these sources. OSM-derived database content is supplied subject to ODbL. Microsoft source data are supplied under CDLA Permissive 2.0, which does not impose restrictions on computational Results. Inclusion does not restrict the independent public-domain federal source data.

The original provenance log at `notes/data-provenance.md` records acquisition sources and dates. The frozen release files and SHA-256 manifest identify the exact supplied material; a fresh live-source download may differ.

The archived inputs concern streets, geography and aggregate census/employment measures. No Census API key or other access credential is included.


## Provider licence update

The original project `LICENSE` is retained verbatim, including its older Microsoft ODbL note. Microsoft changed the Global ML Building Footprints licence to CDLA Permissive 2.0 on 11 March 2026, before this study's July 2026 acquisitions: [provider licence change](https://github.com/microsoft/GlobalMLBuildingFootprints/commit/ef94ee3dfb5da3bd2c9dd9c36815eff66fa0b66d). The current source terms documented here govern the distributed Microsoft data. The full [CDLA agreement](LICENSES/CDLA-Permissive-2.0.txt) is supplied both in the repository and as a release asset; redistribute it with the Microsoft source data. This is a publication-metadata clarification, not a change to the research files.
