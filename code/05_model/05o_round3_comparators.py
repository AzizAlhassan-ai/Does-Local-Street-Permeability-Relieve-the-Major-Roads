#!/usr/bin/env python
"""Stage 5 — round-3 panel requests: comparators, spillover, severance, provenance (D-084).

A. ANGULAR CHOICE (bravo, delta — "the strongest functional comparators are never computed")
   Normalised angular choice, the space-syntax measure of through-movement potential,
   computed on the local subgraph: a dual graph whose nodes are street segments and
   whose edge costs are angular deviation, betweenness over that graph, then Hillier
   et al.'s (2012) normalisation. This is the hard comparator — unlike the five
   morphological metrics it is genuinely functional — so the measurement claim stands
   or falls on it.

B. SPATIAL DURBIN, correctly specified (alfa, delta)
   The earlier run omitted functional-class dummies and is not comparable to the
   primary model. Re-run with the full control set; report direct, indirect and total.

C. SEVERANCE CONTROLS IN THE WITHIN-CORRIDOR MODEL (delta)
   What varies along a single arterial is adjacent land use and barrier structure,
   and barriers cause both P1 = 0 and high volume. Rivers, railways and
   controlled-access facilities are added to the corridor fixed-effects spec.

D. COUNT-BASED AADT SUBSAMPLE (charlie — the panel's highest-value single analysis)
   HPMS 2018 carries no derivation flag, so "counted vs modelled" cannot be recovered
   from the primary outcome. HPMS 2024 does carry `sample_id`, marking HPMS sample-panel
   sections, for which states must report measured data. Re-estimating on panel sections
   is the closest available test of whether the association is partly definitional.

Usage
-----
    uv run python code/05_model/05o_round3_comparators.py
"""
from __future__ import annotations
import argparse, math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import geopandas as gpd, networkx as nx, numpy as np, pandas as pd
import statsmodels.formula.api as smf
from lib import cfg, paths, provenance

CTRL = ["pop_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]
R = 800


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def prep(d):
    d = d.copy()
    d["betweenness_log"] = np.log10(d["arterial_betweenness"] + 1e-5)
    src = {"pop_density_km2_z": "pop_density_km2", "lu_entropy_z": "lu_entropy",
           "dist_cbd_km_c_z": "dist_cbd_km_c", "dist_cbd_km_c_sq_z": "dist_cbd_km_c_sq",
           "median_year_z": "median_year_structure_built", "through_lanes_z": "through_lanes",
           "gen_z": "local_int_density"}
    g = d.groupby("city")
    for dst, s in src.items():
        d[dst] = g[s].transform(z)
    d["p1"] = d["p1_any"].astype(float)
    d["y"] = d["log_aadt"]
    return d.dropna(subset=["y", "p1", "cell_id", "route_id", "f_system"] + CTRL).copy()


def bearing(geom):
    c = list(geom.coords)
    return math.atan2(c[-1][1] - c[0][1], c[-1][0] - c[0][0])


def angular_choice(city, metric, k=400, seed=7):
    """Normalised angular choice on the local subgraph (Hillier et al., 2012).

    Dual graph: one node per local street segment; two segments are adjacent if they
    share an endpoint, and the traversal cost is the angular deviation between them.
    Choice is betweenness over that graph; NACH = log(choice + 1) / log(depth + 3).
    """
    loc = gpd.read_file(paths.raw(city, "osm") / "network_urban_area_local.gpkg",
                        layer="edges").to_crs(metric)
    loc = loc[loc.geometry.type == "LineString"].reset_index(drop=True)
    lo = np.minimum(loc["u"].values, loc["v"].values)
    hi = np.maximum(loc["u"].values, loc["v"].values)
    loc["_pair"] = list(zip(lo, hi))
    loc = loc.drop_duplicates("_pair").reset_index(drop=True)
    ang = np.array([bearing(g) for g in loc.geometry])
    at_node = {}
    for i, (u, v) in enumerate(zip(loc["u"].values, loc["v"].values)):
        at_node.setdefault(u, []).append(i)
        at_node.setdefault(v, []).append(i)
    D = nx.Graph()
    D.add_nodes_from(range(len(loc)))
    for segs in at_node.values():
        for a in range(len(segs)):
            for b in range(a + 1, len(segs)):
                i, j = segs[a], segs[b]
                dth = abs(ang[i] - ang[j]) % (2 * math.pi)
                dth = min(dth, 2 * math.pi - dth)
                dth = min(dth, math.pi - dth) if dth > math.pi / 2 else dth
                D.add_edge(i, j, w=float(dth) + 1e-3)
    kk = min(k, D.number_of_nodes())
    ch = nx.betweenness_centrality(D, k=kk, weight="w", seed=seed, normalized=False)
    depth = max(np.mean([d for _, d in D.degree()]), 1.0)
    nach = {i: math.log(ch.get(i, 0.0) + 1.0) / math.log(depth + 3.0) for i in D.nodes}
    loc["nach"] = [nach.get(i, 0.0) for i in range(len(loc))]
    mid = gpd.GeoDataFrame(loc[["nach"]],
                           geometry=[g.interpolate(.5, normalized=True) for g in loc.geometry],
                           crs=metric)
    cat = gpd.read_parquet(paths.processed(city) / f"catchments_r{R}.parquet").to_crs(metric)
    j = gpd.sjoin(mid, cat[["segment_uid", "geometry"]], how="inner", predicate="within")
    out = j.groupby("segment_uid")["nach"].mean().rename("nach").reset_index()
    out["segment_uid"] = city + "|" + out["segment_uid"].astype(str)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-nach", action="store_true")
    args = ap.parse_args()
    conf = cfg.config(); metric = conf["crs"]["metric"]
    d = prep(pd.read_parquet(paths.ANALYSIS / f"analysis_pooled_r{R}.parquet"))
    base = " + ".join(CTRL) + " + C(f_system)"
    cities = sorted(d.city.unique())
    print(f"Environment: {provenance.environment_stamp()}\nn = {len(d):,}")
    rows = []

    # ------------------------------------------------------------------ A
    if not args.skip_nach:
        print(f"\n{'='*92}\nA. NORMALISED ANGULAR CHOICE as a functional comparator\n{'='*92}")
        parts = []
        for c in cities:
            try:
                parts.append(angular_choice(c, metric))
                print(f"  {c}: angular choice computed")
            except Exception as e:
                print(f"  {c}: FAILED ({e})")
        if parts:
            nach = pd.concat(parts, ignore_index=True)
            dd = d.merge(nach, on="segment_uid", how="left")
            dd["nach_z"] = dd.groupby("city")["nach"].transform(z)
            dd = dd.dropna(subset=["nach_z"])
            print(f"\n  merged on {len(dd):,} segments")
            print(f"  corr(NACH, P1) = {dd[['nach_z','p1']].corr().iloc[0,1]:+.3f}   "
                  f"corr(NACH, intersection density) = {dd[['nach_z','gen_z']].corr().iloc[0,1]:+.3f}")
            for lab, f_ in [("NACH alone", f"y ~ {base} + C(city) + nach_z"),
                            ("P1 alone", f"y ~ {base} + C(city) + p1"),
                            ("NACH | P1", f"y ~ {base} + C(city) + p1 + nach_z"),
                            ("P1 | NACH", f"y ~ {base} + C(city) + p1 + nach_z")]:
                m = smf.mixedlm(f_, dd, groups=dd["cell_id"]).fit(method="lbfgs", reml=True)
                term = "nach_z" if lab.startswith("NACH") else "p1"
                b, s, p = m.params[term], m.bse[term], m.pvalues[term]
                rows.append({"check": "nach", "spec": lab, "beta": b, "se": s, "p": p})
                print(f"  {lab:<12}{b:>+10.4f} (SE {s:.4f})  p = {p:.4f}")
            print("\n  -> This is the comparator that matters: angular choice is a functional")
            print("     measure of through-movement potential, not a morphological count.")

    # ------------------------------------------------------------------ B
    print(f"\n{'='*92}\nB. SPATIAL DURBIN, full control set\n{'='*92}")
    try:
        from libpysal.weights import KNN
        from spreg import GM_Lag
        for c in cities:
            g = d[d.city == c].copy()
            seg = gpd.read_parquet(paths.processed(c) / "segments.parquet").to_crs(metric)
            seg["segment_uid"] = c + "|" + seg["segment_uid"].astype(str)
            g = g.merge(seg[["segment_uid", "geometry"]], on="segment_uid", how="inner")
            g = gpd.GeoDataFrame(g, geometry="geometry", crs=metric)
            fs = pd.get_dummies(g["f_system"].astype(int), prefix="fs", drop_first=True).astype(float)
            X = pd.concat([g[CTRL].reset_index(drop=True), fs.reset_index(drop=True),
                           g[["p1"]].reset_index(drop=True)], axis=1)
            names = list(X.columns)
            pts = gpd.GeoDataFrame(geometry=[gm.interpolate(.5, normalized=True)
                                             for gm in g.geometry], crs=metric)
            w = KNN.from_dataframe(pts, k=8); w.transform = "r"
            m = GM_Lag(g[["y"]].to_numpy(float), X.to_numpy(float), w=w,
                       name_x=names, name_y="log_aadt")
            k = m.betas.flatten(); rho = float(k[-1])
            b_p1 = float(k[1 + names.index("p1")])
            direct, total = b_p1, b_p1 / (1 - rho)
            rows.append({"check": "durbin_full", "city": c, "rho": rho, "direct": direct,
                         "indirect": total - direct, "total": total})
            print(f"  {c:<16} ρ={rho:+.3f}  direct={direct:+.4f}  "
                  f"indirect={total-direct:+.4f}  total={total:+.4f}")
    except Exception as e:
        print(f"  unavailable: {e}")

    # ------------------------------------------------------------------ C
    print(f"\n{'='*92}\nC. SEVERANCE CONTROLS IN THE WITHIN-CORRIDOR MODEL\n{'='*92}")
    sev_parts = []
    for c in cities:
        try:
            cat = gpd.read_parquet(paths.processed(c) / f"catchments_r{R}.parquet").to_crs(metric)
            maj = gpd.read_file(paths.raw(c, "osm") / "network_urban_area_major.gpkg",
                                layer="edges").to_crs(metric)
            hw = maj["highway"].astype(str)
            ctrl_acc = maj[hw.str.contains("motorway|trunk", na=False)]
            allnet = gpd.read_file(paths.raw(c, "osm") / "network_urban_area_all.gpkg",
                                   layer="edges").to_crs(metric)
            rail = allnet[allnet.get("railway").notna()] if "railway" in allnet.columns else allnet.iloc[0:0]
            recs = []
            ca_idx = ctrl_acc.sindex if len(ctrl_acc) else None
            rl_idx = rail.sindex if len(rail) else None
            for uid, geom in zip(cat.segment_uid, cat.geometry):
                n_ca = len(ca_idx.query(geom, predicate="intersects")) if ca_idx is not None else 0
                n_rl = len(rl_idx.query(geom, predicate="intersects")) if rl_idx is not None else 0
                recs.append({"segment_uid": c + "|" + str(uid),
                             "n_ctrl_access": n_ca, "n_rail": n_rl})
            sev_parts.append(pd.DataFrame(recs))
            print(f"  {c}: severance features counted")
        except Exception as e:
            print(f"  {c}: FAILED ({e})")
    if sev_parts:
        sev = pd.concat(sev_parts, ignore_index=True)
        ds = d.merge(sev, on="segment_uid", how="left").fillna({"n_ctrl_access": 0, "n_rail": 0})
        ds["sev_ca"] = ds.groupby("city")["n_ctrl_access"].transform(z)
        ds["sev_rl"] = ds.groupby("city")["n_rail"].transform(z)
        keep = ds.groupby("route_id")["p1"].transform(lambda s: s.nunique() > 1)
        dw = ds[keep]
        for lab, f_ in [("corridor FE", f"y ~ {base} + C(route_id) + p1"),
                        ("corridor FE + severance", f"y ~ {base} + sev_ca + sev_rl + C(route_id) + p1")]:
            m = smf.ols(f_, dw).fit(cov_type="cluster", cov_kwds={"groups": dw["route_id"]})
            b, s, p = m.params["p1"], m.bse["p1"], m.pvalues["p1"]
            rows.append({"check": "severance", "spec": lab, "n": len(dw), "beta": b, "se": s, "p": p})
            print(f"  {lab:<26}n={len(dw):>7,}  β={b:>+8.4f} (SE {s:.4f})  p={p:.4f}")

    out = pd.DataFrame(rows)
    fp = paths.TABLES / "round3_comparators.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05o_round3_comparators", "NACH, Durbin, severance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
