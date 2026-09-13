# Does Local Street Permeability Relieve the Major Roads? Measuring Substitutability, Not Connectivity, in Six US Urban Areas

Research code and frozen data supporting the paper above.

**Paper authors (in order): Abdulaziz M. Alhassan and Ibrahim Altasan**

Department of Urban Planning, King Saud University.

[Current release: v1.0.2](https://github.com/AzizAlhassan-ai/Does-Local-Street-Permeability-Relieve-the-Major-Roads/releases/tag/v1.0.2) · [Frozen data: v1.0.1](https://github.com/AzizAlhassan-ai/Does-Local-Street-Permeability-Relieve-the-Major-Roads/releases/tag/v1.0.1) · [Reproduction instructions](REPRODUCING.md) · [Data dictionary](DATA_DICTIONARY.md) · [Data licences](DATA_LICENSES.md)

## Study

The study evaluates whether road-specific local-network substitutability is associated with lower arterial and collector traffic volumes across Boston, Charlotte, Denver, Phoenix, Portland and the Wasatch Front. The primary outcome is FHWA HPMS 2018 AADT; the local street network comes from the frozen OpenStreetMap acquisitions included in the release.

The final specification uses exogenous-attribute analysis units, a minimum segment length of 400 m, activity controls including job density, and 800 m catchments. The stored primary table contains 27,191 units; the final complete-case model uses 18,684. The design is observational: the estimated associations do not establish causal relief or observed traffic redistribution.

## Contents

| Location | Contents |
|---|---|
| `code/` | Original acquisition, network, modelling and figure scripts, unchanged. |
| `config/` | Original city and analysis parameters, unchanged. |
| `pyproject.toml`, `uv.lock` | Original dependency specification and lock file. |
| `data/analysis__aadtfree/` | Revised primary analysis tables, including catchment-radius variants. |
| `data/analysis/` | Earlier analysis frame used in comparisons and supporting checks. |
| `data/analysis__oneway/` | Directed-network sensitivity tables. |
| `outputs/tables/`, `outputs/figures/`, `outputs/models/` | Saved original results; see the reproduction guide for the final-versus-earlier distinction. |
| `notes/data-provenance.md` | Original acquisition provenance log. |
| `FILE_MANIFEST.csv` | SHA-256, byte count and repository/archive location for each included research file. |
| `RELEASE_ASSETS_SHA256.txt` | Checksums of the unchanged v1.0.1 release assets. |

Large inputs remain attached to the [v1.0.1 data release](https://github.com/AzizAlhassan-ai/Does-Local-Street-Permeability-Relieve-the-Major-Roads/releases/tag/v1.0.1) as intact archives or verified smaller pieces. Download and reassemble them automatically from the repository root:

```bash
python3 download_data.py
```

The helper uses the ordered files and SHA-256 checksums in `data-assets.json`, downloads the licence companions, and restores these unchanged archive files in `release-assets/`:

- `processed-data.tar.gz`: all processed city data and analysis variants.
- `raw-<city>.tar.gz`: six archives containing the original city inputs, including the exact OSM networks.
- `hpms_2024_national.zip`: the original national HPMS 2024 download for supporting outcome checks.

The helper does not extract files or run analysis. Follow [REPRODUCING.md](REPRODUCING.md) to install the archives. `--only processed`, `--only raw`, or `--only hpms` downloads a subset; the primary model below needs none of these large archives.

The archives preserve the original research file contents. Symbolic links are materialized as ordinary files so the download is portable. Private drafts, reviewer discussions, credentials, local environments and redundant HTTP caches are excluded.

## Reproduce the primary analysis

Python 3.12 was used for the archived environment. From the repository root:

```bash
uv sync --frozen --python 3.12
env -u PIPE_VARIANT uv run python code/05_model/05x_primary_v2.py
```

The primary model reads the analysis tables already in the repository; no download credentials are required. For all final comparison tables, diagnostics, figures, earlier sensitivity analyses, and rebuilding from source inputs, follow [REPRODUCING.md](REPRODUCING.md).

Run reproductions in a working copy: original scripts write results to `outputs/` and append progress/provenance logs. The numbered acquisition scripts and `run_city.sh` default to the earlier analysis branch; they are not a one-command rebuild of the final paper. The guide identifies the required revised branches and remaining differences among supporting analyses.

## Version and citation

**v1.0.2 (13 September 2026)** updates the displayed paper title, repository address and paper-author metadata. The research code, configurations, data, saved results and download helper are unchanged from v1.0.1. The original research directory and manuscript were not edited.

The first completed code-and-data deposit remains **v1.0.1**. Its frozen attachments, download manifest and checksums are preserved. The helper retains the original repository address, which GitHub redirects to this renamed repository.

Paper citation (manuscript in preparation):

> Alhassan, A. M., & Altasan, I. (2026). *Does Local Street Permeability Relieve the Major Roads? Measuring Substitutability, Not Connectivity, in Six US Urban Areas*. Manuscript in preparation.

Code and data citation:

> Alhassan, A. M. (2026). *Does Local Street Permeability Relieve the Major Roads? Measuring Substitutability, Not Connectivity, in Six US Urban Areas* [Research code and data] (Version 1.0.2; frozen data from Version 1.0.1). GitHub. https://github.com/AzizAlhassan-ai/Does-Local-Street-Permeability-Relieve-the-Major-Roads/releases/tag/v1.0.2

[CITATION.cff](CITATION.cff) records the software author and provides the two-author paper as the preferred article citation. Paper authorship and software/data contributions are recorded separately. No DOI or journal acceptance is claimed.

## Licences and attribution

Original analysis code is released under the [MIT licence](LICENSE). Data retain the separate terms described in [DATA_LICENSES.md](DATA_LICENSES.md).

**© OpenStreetMap contributors.** OpenStreetMap extracts and derived network/database products are available under the [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Microsoft Global Building Footprints are supplied under CDLA Permissive 2.0; the full agreement accompanies the release. These data are not relicensed under MIT.

## Verification

See [VERIFICATION.md](VERIFICATION.md) for the checks performed on this publication package and their scope.

