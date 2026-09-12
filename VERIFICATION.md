# Publication-package verification

Prepared on 13 September 2026. These checks concern the integrity and usability of this deposit, not independent validation of the study's scientific conclusions.

## Original-file preservation

- 801 included research files were fingerprinted with SHA-256 and byte counts before packaging.
- All 195 research files copied directly into the public repository matched the original bytes.
- Every member of the seven data archives was read back and checked against its source-file SHA-256. Links were dereferenced to portable ordinary files with identical contents.
- The three national HPMS parts reconstruct the original ZIP byte-for-byte. The original ZIP passed its full member CRC integrity check.
- After packaging, all 801 included source files again matched their original hashes. Size and modification timestamps of 456 other research files also remained unchanged.
- Research code, configuration, data, manuscript files and saved results in the original working directory were not edited. Publication README, data dictionary, reproduction guide, citation metadata, licence clarification and manifests were prepared in a separate directory.

## Primary numerical reproduction

The unchanged `code/05_model/05x_primary_v2.py` was run to completion in an isolated temporary copy using the archived primary data and the existing Python 3.12.13 environment.

The resulting `outputs/tables/primary_v2.csv` was compared with the deposited original across all **36 rows and 34 columns**. Numeric comparisons used relative tolerance 1e-8 and absolute tolerance 1e-10; the observed maximum absolute numeric difference was **0**. Non-numeric values and missing-value placement also matched.

The sample was 27,191 stored units, 19,022 after the 400 m floor, and **18,684 complete cases** across six cities. The primary script also regenerated its per-city, pooled, corridor, balance and supporting estimates in that CSV.

Key installed package versions: NumPy 2.5.1; pandas 3.0.5; statsmodels 0.14.6; PyArrow 25.0.0. The original dependency lock file accompanies the release.

## Other checks and limits

- All included Python sources parsed successfully.
- The primary dictionary covers each of the 60 stored fields and documents the three analysis branches.
- Publication file selection was reviewed for credentials, private drafts, reviewer documents, absolute user paths and oversized Git files; none were included.
- No fresh environment installation or complete acquisition-to-figures rerun was performed. Other saved result tables and figures were preserved and fingerprinted, not all independently regenerated.
- Some earlier supporting scripts retain older sample/specification rules. See `REPRODUCING.md`; this release does not claim a verified command for every manuscript number.
- Microsoft data-licence documentation was checked against the provider's March 2026 licence change. The original project licence file remains unchanged; `DATA_LICENSES.md` clarifies the current source terms.

`FILE_MANIFEST.csv` identifies the included research bytes. `RELEASE_ASSETS_SHA256.txt` identifies the downloadable archive and licence files.
