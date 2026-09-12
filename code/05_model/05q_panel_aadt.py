#!/usr/bin/env python
"""Stage 5 — count-based AADT subsample (D-085; charlie's request).

HPMS 2018 carries no field distinguishing counted from factored or modelled AADT,
so the requested "counted-only" re-estimation cannot be done on the primary outcome.
HPMS 2024 (NTAD) does carry `sample_id`, which flags HPMS sample-panel sections —
the sections for which states are required to report measured data, and therefore
the closest available proxy for a count-based subsample. Re-estimating there tests
whether the association depends on segments whose AADT may be model output.

Usage
-----
    uv run python code/05_model/05q_panel_aadt.py
"""
from __future__ import annotations
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import geopandas as gpd, numpy as np, pandas as pd, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

GDB = paths.ROOT / "data" / "raw" / "_hpms_currency" / "HPMS2024.gdb"
ABBR = {"08":"CO","41":"OR","53":"WA","04":"AZ","25":"MA","33":"NH","49":"UT","37":"NC","45":"SC"}
CTRL = ["pop_z","ent_z","dcbd_z","dcbd2_z","yr_z","ln_z"]


def z(s):
    sd = s.std(ddof=0); return (s-s.mean())/sd if sd and sd>0 else s*0.0


def fit(d, y):
    d = d.copy()
    for dst, src in [("pop_z","pop_density_km2"),("ent_z","lu_entropy"),
                     ("dcbd_z","dist_cbd_km_c"),("dcbd2_z","dist_cbd_km_c_sq"),
                     ("yr_z","median_year_structure_built"),("ln_z","through_lanes")]:
        d[dst] = z(d[src])
    d["p1"] = d["p1_any"].astype(float)
    d = d.dropna(subset=[y,"p1","f_system","cell_id"]+CTRL)
    if len(d) < 150 or d.p1.nunique() < 2 or d.f_system.nunique() < 2:
        return None, len(d)
    f = f"{y} ~ " + " + ".join(CTRL) + " + C(f_system) + p1"
    return smf.mixedlm(f, d, groups=d["cell_id"].astype(str)).fit(method="lbfgs", reml=True), len(d)


def main() -> int:
    conf = cfg.config(); metric = conf["crs"]["metric"]
    pooled = pd.read_parquet(paths.ANALYSIS / "analysis_pooled_r800.parquet")
    print(f"Environment: {provenance.environment_stamp()}")
    print("HPMS 2018 has no AADT-derivation field; using 2024 sample-panel flag as the proxy.\n")
    rows, frames = [], []
    for c in sorted(set(pooled.city)):
        ua = gpd.read_file(paths.raw(c,"census")/"urban_area.gpkg").to_crs(metric)
        ua_geom = ua.union_all() if hasattr(ua,"union_all") else ua.unary_union
        bbox = tuple(gpd.GeoSeries([ua_geom],crs=metric).to_crs(4326).total_bounds)
        parts=[]
        for st in cfg.states(c):
            ab = ABBR.get(st["fips"])
            if not ab: continue
            g = gpd.read_file(GDB, layer=f"HPMS_FULL_{ab}_2024", bbox=bbox,
                              columns=["aadt","f_system","facility_type","sample_id"]).to_crs(metric)
            g = g[g.geometry.notna() & (g.aadt>0) & g.f_system.isin([3,4,5])]
            if "facility_type" in g.columns: g = g[g.facility_type==2]
            parts.append(g[["aadt","sample_id","geometry"]])
        if not parts: continue
        g24 = gpd.GeoDataFrame(pd.concat(parts,ignore_index=True), crs=metric)
        sid = g24.sample_id.astype(str).str.strip()
        g24["panel"] = sid.notna() & (sid!="") & (sid!="0") & (sid.str.lower()!="none")
        seg = gpd.read_parquet(paths.processed(c)/"segments.parquet").to_crs(metric)
        mid = gpd.GeoDataFrame(seg[["segment_uid"]].reset_index(drop=True),
                geometry=[gm.interpolate(.5,normalized=True) for gm in seg.geometry], crs=metric)
        j = gpd.sjoin_nearest(mid, g24[["aadt","panel","geometry"]], how="left",
                              max_distance=100.0, distance_col="dd")
        j = j.sort_values("dd").drop_duplicates("segment_uid")
        j["segment_uid"] = c + "|" + j["segment_uid"].astype(str)
        b = pooled[pooled.city==c].merge(j[["segment_uid","aadt","panel"]].rename(
              columns={"aadt":"aadt24"}), on="segment_uid", how="left")
        b["log_aadt24"] = np.log(b.aadt24.where(b.aadt24>0))
        share = 100*b.panel.fillna(False).mean()
        m_all,n_all = fit(b, "log_aadt24")
        m_pan,n_pan = fit(b[b.panel==True], "log_aadt24")
        row = {"city":c,"pct_sample_panel":share,"n_all":n_all,
               "beta_all": m_all.params["p1"] if m_all is not None else np.nan,
               "p_all": m_all.pvalues["p1"] if m_all is not None else np.nan,
               "n_panel":n_pan,
               "beta_panel": m_pan.params["p1"] if m_pan is not None else np.nan,
               "p_panel": m_pan.pvalues["p1"] if m_pan is not None else np.nan}
        rows.append(row); frames.append(b)
        print(f"  {c:<15} panel {share:5.1f}%  |  all n={n_all:>6,} β={row['beta_all']:+.4f}"
              f"  |  panel n={n_pan:>5,} β={row['beta_panel']:+.4f} (p={row['p_panel']:.4f})")
    t = pd.DataFrame(rows)
    print(f"\n{'='*84}\nSUMMARY — 2024 outcome, all segments vs HPMS sample-panel sections\n{'='*84}")
    print(t.round(4).to_string(index=False))
    neg = int((t.beta_panel<0).sum()); sig = int(((t.beta_panel<0)&(t.p_panel<0.05)).sum())
    print(f"\n  panel-only: negative in {neg}/{len(t)}, negative and significant in {sig}/{len(t)}")
    fp = paths.TABLES/"aadt_sample_panel.csv"; t.to_csv(fp,index=False)
    print(f"  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05q_panel_aadt","count-proxy subsample re-estimation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
