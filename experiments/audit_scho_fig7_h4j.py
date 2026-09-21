"""H4j: audit completed H4i Fig.7 controlled reproduction. No optimizer runs."""
from __future__ import annotations
import csv
from pathlib import Path
import numpy as np

RAW=Path("results/raw/scho_fig7_h4i_variant_runs.csv")
SUM=Path("results/processed/scho_fig7_h4i_variant_summary.csv")
PF=Path("results/processed/scho_fig7_h4i_pairwise_by_function.csv")
PC=Path("results/processed/scho_fig7_h4i_pairwise_counts.csv")
OUT=Path("results/processed/scho_fig7_h4j_diagnostic.csv")
NOTE=Path("report/notes/H4j_scho_fig7_diagnostic_freeze.md")
FIGS=[Path(f"report/figures/scho_fig7{x}_h4i_controlled.png") for x in "abcd"]
V=[f"V{i}" for i in range(1,12)]
F=[f"F{i}" for i in range(1,24)]

PAPER={"V1":(18,15),"V2":(20,13),"V3":(17,15),"V4":(17,14),
"V5":(17,16),"V6":(18,14),"V7":(20,13),"V8":(20,11),
"V9":(18,9),"V10":(20,13),"V11":(18,15)}
EXPECTED={"V1":(14,17,8),"V2":(20,14,11),"V3":(17,17,11),
"V4":(14,16,7),"V5":(19,16,12),"V6":(15,15,7),
"V7":(17,15,9),"V8":(16,17,10),"V9":(16,14,7),
"V10":(18,17,12),"V11":(19,20,16)}

def read(p):
    if not p.exists(): raise FileNotFoundError(f"Missing H4i evidence: {p}")
    with p.open("r",newline="",encoding="utf-8-sig") as f: return list(csv.DictReader(f))

def direction(a,b):
    return "SCHO" if a>b else ("VARIANT" if a<b else "TIE")

def main():
    print("="*118)
    print("H4j - SCHO Fig.7 paper-agreement diagnostic + controlled freeze")
    print("="*118)
    print("No optimizer will be executed.")
    raw,summ,pf,pc=read(RAW),read(SUM),read(PF),read(PC)
    assert len(raw)==7590, f"raw rows {len(raw)} != 7590"
    assert len(summ)==253, f"summary rows {len(summ)} != 253"
    assert len(pf)==253, f"pairwise-function rows {len(pf)} != 253"
    assert len(pc)==11, f"pairwise-count rows {len(pc)} != 11"
    keys={(r["Variant"],r["Function"],int(r["Run"])) for r in raw}
    exp={(v,f,n) for v in V for f in F for n in range(1,31)}
    assert keys==exp, "raw protocol keys mismatch"
    assert {(r["Variant"],r["Function"]) for r in summ}=={(v,f) for v in V for f in F}
    assert {(r["Variant"],r["Function"]) for r in pf}=={(v,f) for v in V for f in F}
    for p in FIGS: assert p.exists(), f"missing figure: {p}"
    m={r["Variant"]:r for r in pc}
    assert set(m)==set(V), "variant set mismatch"

    rows=[]
    for v in V:
        r=m[v]
        rs=int(r["SCHO_OptimalAverageCount"]); rv=int(r["Variant_OptimalAverageCount"]); t=int(r["Ties"])
        ps,pv=PAPER[v]
        assert (rs,rv,t)==EXPECTED[v], f"{v}: H4i counts changed"
        assert (int(r["Paper_SCHO_Count"]),int(r["Paper_Variant_Count"]))==(ps,pv), f"{v}: paper anchors changed"
        rd,pd=direction(rs,rv),direction(ps,pv)
        status="SAME_DIRECTION" if rd==pd else ("REPRO_TIE" if rd=="TIE" else "REVERSED")
        rows.append(dict(Variant=v,ReproSCHO=rs,ReproVariant=rv,ReproTies=t,
                         PaperSCHO=ps,PaperVariant=pv,SCHO_Delta=rs-ps,Variant_Delta=rv-pv,
                         AbsSCHO_Delta=abs(rs-ps),AbsVariant_Delta=abs(rv-pv),
                         ReproDirection=rd,PaperDirection=pd,DirectionStatus=status,
                         PaperImpliedOverlapIfDualCredit=ps+pv-23))

    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0].keys())
    with OUT.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

    same=sum(r["DirectionStatus"]=="SAME_DIRECTION" for r in rows)
    tie=sum(r["DirectionStatus"]=="REPRO_TIE" for r in rows)
    rev=sum(r["DirectionStatus"]=="REVERSED" for r in rows)
    exs=sum(r["AbsSCHO_Delta"]==0 for r in rows)
    exv=sum(r["AbsVariant_Delta"]==0 for r in rows)
    expair=sum(r["AbsSCHO_Delta"]==0 and r["AbsVariant_Delta"]==0 for r in rows)
    w2=sum(r["AbsSCHO_Delta"]<=2 and r["AbsVariant_Delta"]<=2 for r in rows)
    w3=sum(r["AbsSCHO_Delta"]<=3 and r["AbsVariant_Delta"]<=3 for r in rows)
    mae_s=float(np.mean([r["AbsSCHO_Delta"] for r in rows]))
    mae_v=float(np.mean([r["AbsVariant_Delta"] for r in rows]))
    mae=float(np.mean([x for r in rows for x in (r["AbsSCHO_Delta"],r["AbsVariant_Delta"])]))
    rt=sum(r["ReproTies"] for r in rows)
    pi=sum(r["PaperImpliedOverlapIfDualCredit"] for r in rows)

    lines=["# H4j — SCHO Fig.7 paper-agreement diagnostic + controlled freeze","",
    "## Freeze conclusion","",
    "**SCHO FIG.7 CONTROLLED REPRODUCTION COMPLETE; PARTIAL BAR-LEVEL AGREEMENT; NO TUNING.**","",
    "`SCHO_FIG7_CONTROLLED_COMPLETE__PARTIAL_BAR_LEVEL_AGREEMENT__NO_TUNING`","",
    "The eleven variants remain `CONTROLLED-INTERPRETATION`, not recovered author-source implementations.","",
    "## Pairwise comparison","",
    "| Variant | Repro SCHO/Variant | Paper SCHO/Variant | Delta | Direction |",
    "|---|---:|---:|---:|---|"]
    for r in rows:
        lines.append(f"| {r['Variant']} | {r['ReproSCHO']}/{r['ReproVariant']} | {r['PaperSCHO']}/{r['PaperVariant']} | {r['SCHO_Delta']:+d}/{r['Variant_Delta']:+d} | {r['DirectionStatus']} |")
    lines += ["","## Aggregate diagnostic","",
    f"- Same paper direction: **{same}/11**",
    f"- Reproduced tie: **{tie}/11**",
    f"- Reversed direction: **{rev}/11**",
    f"- Exact SCHO bar: **{exs}/11**",
    f"- Exact variant bar: **{exv}/11**",
    f"- Exact pair: **{expair}/11**",
    f"- Both bars within ±2: **{w2}/11**",
    f"- Both bars within ±3: **{w3}/11**",
    f"- Mean absolute SCHO-count difference: **{mae_s:.3f}**",
    f"- Mean absolute variant-count difference: **{mae_v:.3f}**",
    f"- Overall bar-count MAE: **{mae:.3f}**","",
    "Same-direction cases: V2, V5, V7, V9, V10. Reproduced ties: V3, V6. Reversals: V1, V4, V8, V11.","",
    "## Tie/overlap diagnostic","",
    f"H4i records **{rt}** pairwise ties. If the paper bars are interpreted using the same dual-credit convention, their aggregate implied overlap is **{pi}**. This is diagnostic only because the paper does not publish a machine-readable tie-counting rule.","",
    "## Interpretation and freeze rule","",
    "The disagreement is preserved. Do not change H4h equations, H4i tie tolerance, seeds, or protocol to move the bars toward the paper. A future change requires new primary-source evidence for the author variants and a new version.","",
    "With H4c (Fig.8), H4f (Table 5), and H4j (Fig.7), the planned Section 3.1.1–3.1.2 scope is complete with explicit exactness boundaries.","",
    "**H4 — COMPLETE WITH CONTROLLED-INTERPRETATION BOUNDARY FOR FIG.7.**"]
    NOTE.parent.mkdir(parents=True,exist_ok=True); NOTE.write_text("\n".join(lines),encoding="utf-8")

    print("H4i evidence audit: PASS")
    print("Raw 7590/7590 | Summary 253/253 | Pairwise-function 253/253 | Pairwise 11/11 | Figures 4/4")
    print("-"*118)
    for r in rows:
        print(f"{r['Variant']:<3} repro={r['ReproSCHO']:>2}/{r['ReproVariant']:<2} paper={r['PaperSCHO']:>2}/{r['PaperVariant']:<2} delta={r['SCHO_Delta']:+d}/{r['Variant_Delta']:+d} {r['DirectionStatus']}")
    print("-"*118)
    print(f"Direction: same={same}/11, repro_tie={tie}/11, reversed={rev}/11")
    print(f"Exact bars: SCHO={exs}/11, variant={exv}/11, exact_pair={expair}/11")
    print(f"Both bars within +/-2: {w2}/11 | within +/-3: {w3}/11")
    print(f"Bar-count MAE: SCHO={mae_s:.3f}, variant={mae_v:.3f}, overall={mae:.3f}")
    print(f"Tie/overlap diagnostic: reproduced={rt}, paper-implied={pi}")
    print("-"*118)
    print("H4j RESULT: PASS")
    print("Freeze: SCHO_FIG7_CONTROLLED_COMPLETE__PARTIAL_BAR_LEVEL_AGREEMENT__NO_TUNING")
    print(f"Saved diagnostic: {OUT}")
    print(f"Saved freeze note: {NOTE}")
    print("H4 STATUS: COMPLETE WITH CONTROLLED-INTERPRETATION BOUNDARY FOR FIG.7")
    print("="*118)

if __name__=="__main__": main()
