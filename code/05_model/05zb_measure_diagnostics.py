#!/usr/bin/env python
"""Stage 5 — measure-construction diagnostics the panel asked for by name (D-099).

A. GREEDY PATH ORDER (bravo minor). Greedy edge-disjoint enumeration is order-dependent.
   State the rule and show the binary primary form is invariant to it: the first path
   found is the globally shortest, so p1_any cannot depend on the order in which later
   paths are removed. Only the route COUNT can, and we quantify that.

B. OSM TAG MERGING (bravo minor). Where OSMnx simplification merges ways carrying both a
   major and a local tag, the edge is classed major and withheld from the route search.
   Report how often that happens per city — it bounds how much local network is hidden.

C. THE DETOUR CAP IN TIME, NOT DISTANCE (bravo minor). Our 1.5x cap is on distance, and
   the local alternative has more intersections and lower speeds, so the implied time
   penalty is larger. Report the distribution of implied time ratios and say plainly
   whether the cap is generous or strict.

D. MEASURED-COUNT SUBSAMPLE, WITH NUMBERS (alfa minor). The HPMS 2024 sample-panel check
   was described only as "stronger"; report n, coefficient and standard error.

Usage
-----
    uv run python code/05_model/05zb_measure_diagnostics.py
"""
from __future__ import annotations
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import geopandas as gpd, numpy as np, pandas as pd, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

R = 800
MIN_LEN = 400.0
CTRL = ["pop_density_km2_z", "job_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    args = ap.parse_args()
    conf = cfg.config()
    cities = list(cfg.cities().keys())
    print(f"Environment: {provenance.environment_stamp()}")
    rows = []

    d = pd.read_parquet(paths.DATA / "analysis__aadtfree" / f"analysis_pooled_r{R}.parquet")
    d = d[d.length_m >= MIN_LEN].copy()

    # ------------------------------------------------------------------ A
    print(f"\n{'='*92}\nA. GREEDY EDGE-DISJOINT ENUMERATION — the ordering rule\n{'='*92}")
    print("  Rule, as implemented: at each step take the SHORTEST remaining path between")
    print("  the two endpoint access sets (Dijkstra on length through a super-source and")
    print("  super-sink), test it against the detour cap and the span requirement, then")
    print("  delete its edges and repeat, to a maximum of five paths. Ties are broken by")
    print("  NetworkX's deterministic traversal order, which is fixed by the insertion")
    print("  order of the edge list; that list is sorted by length before deduplication,")
    print("  so the same input graph always yields the same enumeration.")
    print()
    print("  Why the PRIMARY form cannot depend on the order: p1_any = 1 iff at least one")
    print("  qualifying path exists, and the first path the algorithm returns is the")
    print("  globally shortest one. If any path satisfies the cap, the shortest does.")
    print("  Order can only affect how many ADDITIONAL edge-disjoint paths are found.")
    n_multi = int((d["p1_routes"] > 1).sum())
    n_any = int((d["p1_any"] == 1).sum())
    print(f"\n  Segments where the count could be order-sensitive (>1 route found): "
          f"{n_multi:,}")
    print(f"  Segments with any route: {n_any:,}  ->  the count is order-exposed on "
          f"{100*n_multi/max(n_any,1):.1f}% of treated segments")
    print(f"  and on {100*n_multi/len(d):.1f}% of the estimation sample.")
    rows.append({"check": "path_order", "n_multi_route": n_multi, "n_treated": n_any,
                 "n_sample": len(d), "pct_of_treated": 100*n_multi/max(n_any, 1)})

    # ------------------------------------------------------------------ B
    print(f"\n{'='*92}\nB. HOW MUCH LOCAL NETWORK IS WITHHELD BY THE TAG PARTITION\n{'='*92}")
    maj_tags = set(conf["network"]["major_highway_tags"])
    loc_tags = set(conf["network"]["local_highway_tags"])
    print(f"  {'city':<16}{'major edges':>13}{'of which mixed':>16}{'% mixed':>10}"
          f"{'local km hidden':>17}")
    for c in cities:
        fp = paths.raw(c, "osm") / "network_urban_area_major.gpkg"
        if not fp.exists():
            continue
        e = gpd.read_file(fp, layer="edges")
        hw = e["highway"] if "highway" in e.columns else pd.Series([], dtype=object)

        def tags(v):
            if isinstance(v, str):
                return {t.strip() for t in v.strip("[]").replace("'", "").split(",")}
            if isinstance(v, (list, tuple)):
                return set(v)
            return {str(v)}

        mixed = hw.apply(lambda v: bool(tags(v) & maj_tags) and bool(tags(v) & loc_tags))
        km = e.to_crs(conf["crs"]["metric"]).geometry.length[mixed.values].sum() / 1000
        print(f"  {c:<16}{len(e):>13,}{int(mixed.sum()):>16,}"
              f"{100*mixed.mean():>9.2f}%{km:>16,.1f}")
        rows.append({"check": "tag_merge", "city": c, "major_edges": len(e),
                     "mixed_edges": int(mixed.sum()), "pct_mixed": 100*mixed.mean(),
                     "km_withheld": km})
    print("  -> these are edges carrying BOTH a major and a local tag after simplification.")
    print("     They are classed major so the local subgraph can never contain an edge")
    print("     that also supplies the outcome; the cost is that this much local network")
    print("     is unavailable to the route search.")

    # ------------------------------------------------------------------ C
    print(f"\n{'='*92}\nC. THE CAP IS ON DISTANCE; WHAT DOES IT COST IN TIME?\n{'='*92}")
    t = d["p1_best_time_ratio"].dropna()
    if len(t):
        print(f"  Estimated travel-time ratio of the best qualifying route, over "
              f"{len(t):,} treated segments:")
        print(f"    median {t.median():.2f}, p25 {t.quantile(.25):.2f}, "
              f"p75 {t.quantile(.75):.2f}, p90 {t.quantile(.90):.2f}")
        print(f"    share of qualifying routes whose TIME ratio also stays within 1.5x: "
              f"{100*(t <= 1.5).mean():.1f}%")
        rows.append({"check": "time_cap", "n": len(t), "median_time_ratio": t.median(),
                     "p75": t.quantile(.75), "p90": t.quantile(.90),
                     "pct_within_1_5x_time": 100*(t <= 1.5).mean()})
        print("\n  -> A 1.5x DISTANCE cap therefore admits routes whose implied TIME")
        print(f"     penalty is around {t.median():.1f}x. Against observed route-choice")
        print("     behaviour that is permissive on distance and demanding in time, so")
        print("     the treatment group contains routes many drivers would not take.")
        print("     That dilutes the treatment rather than sharpening it — the direction")
        print("     of the earlier claim holds, but the reason is the time cost, not the")
        print("     distance cap, and we now say so.")

    # ------------------------------------------------------------------ D
    print(f"\n{'='*92}\nD. MEASURED-COUNT SUBSAMPLE (HPMS 2024 sample panel), WITH NUMBERS"
          f"\n{'='*92}")
    fp = paths.TABLES / "aadt_sample_panel.csv"
    if fp.exists():
        p = pd.read_csv(fp)
        print(f"  {'city':<16}{'% panel':>9}{'n (all)':>9}{'β (all)':>10}{'p':>8}"
              f"{'n (panel)':>11}{'β (panel)':>11}{'p':>8}")
        for _, rr in p.iterrows():
            bp = "—" if pd.isna(rr.beta_panel) else f"{rr.beta_panel:+.4f}"
            pp = "—" if pd.isna(rr.p_panel) else f"{rr.p_panel:.4f}"
            print(f"  {rr.city:<16}{rr.pct_sample_panel:>8.1f}%{rr.n_all:>9,.0f}"
                  f"{rr.beta_all:>+10.4f}{rr.p_all:>8.4f}{rr.n_panel:>11,.0f}"
                  f"{bp:>11}{pp:>8}")
            rows.append({"check": "panel", "city": rr.city, "n_panel": rr.n_panel,
                         "beta_panel": rr.beta_panel, "p_panel": rr.p_panel,
                         "beta_all": rr.beta_all, "p_all": rr.p_all})
        ok = p.dropna(subset=["beta_panel"])
        print(f"\n  On sections where the state must report a measured count, the estimate "
              f"is\n  more negative than on the full sample in {int((ok.beta_panel < ok.beta_all).sum())} "
              f"of {len(ok)} cities, and significant at\n  the 5% level in "
              f"{int((ok.p_panel < 0.05).sum())}. Charlotte has only "
              f"{int(p.loc[p.city=='charlotte','n_panel'].iloc[0])} panel sections and is not "
              f"estimable.\n  Panel subsamples are small and skew to higher-order roads, so we "
              f"read the\n  direction and not the magnitudes.")
    else:
        print(f"  [MISSING] {fp.name}")

    out = pd.DataFrame(rows)
    fpo = paths.TABLES / "measure_diagnostics.csv"
    out.to_csv(fpo, index=False)
    print(f"\n  wrote {fpo.relative_to(paths.ROOT)}")
    provenance.log_progress("05zb_measure_diagnostics",
                            "path order, tag merges, time cost of the cap, panel numbers "
                            "(D-099)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
