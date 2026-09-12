First completed public release of the research code and frozen data supporting *Does Local Street Permeability Relieve the Major Roads? Measuring Substitutability, Not Connectivity, in Six US Urban Areas*.

The repository contains unchanged research scripts, configurations, all three analysis-table branches, saved results, provenance, a data dictionary and reproduction instructions. The final primary model uses the revised AADT-free frame and 18,684 complete cases. An isolated rerun reproduced the archived primary CSV exactly.

Large data are provided as intact archives or verified smaller parts. From the repository source, run `python3 download_data.py` to download the data and licence companions and reconstruct the original archives in `release-assets/`. See `data-assets.json` for the ordered pieces and checksums, and `REPRODUCING.md` for extraction and analysis commands. The primary model can be rerun from the repository tables without downloading these larger inputs.

The download restores `processed-data.tar.gz`, six `raw-<city>.tar.gz` archives, and `hpms_2024_national.zip`. All 6.4 GB of compressed source/processed data are preserved. `RELEASE_ASSETS_SHA256.txt` provides attachment checksums and `FILE_MANIFEST.csv` records the original research file hashes.

Original research files were preserved unchanged; publication documentation and the download helper were added separately. Research code is MIT licensed. OSM-derived databases retain ODbL terms and attribution. Microsoft source data use CDLA Permissive 2.0; the full agreement accompanies the release. See `DATA_LICENSES.md`.

The initial v1.0.0 tag is a staging snapshot; v1.0.1 is the first completed public release, with smaller pieces for reliable download. This versioned GitHub release has no assigned DOI.
