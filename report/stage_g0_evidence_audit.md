# Stage G0 — Final Report Evidence Audit

## 1. 目的

Stage G0 不重新运行任何优化器。它只检查最终报告所需的主要证据是否已经存在，并冻结 Stage G 的报告结构。

## 2. Final report structure

最终报告建议按以下顺序组织：

1. Introduction and reproduction goals
2. Algorithms: GWO and source-faithful SCHO
3. Reproduction protocol and implementation principles
4. Classic 23 benchmark reproduction
5. GWO vs SCHO comparison on classic benchmarks
6. CEC2014 reproduction
7. Engineering-design reproduction
8. Source anomalies and implementation caveats
9. Overall findings and limitations
10. Reproducibility / Git freeze information

## 3. Evidence audit

| Group | Required | File | Exists |
|---|---|---|---|
| classic_gwo | yes | `results/processed/gwo_classic23_results.csv` | yes |
| classic_gwo | yes | `results/processed/gwo_stageB_summary.csv` | yes |
| classic_gwo | yes | `report/notes/gwo_stageB_report.md` | yes |
| classic_scho | yes | `results/processed/scho_classic23_summary.csv` | yes |
| classic_scho | yes | `report/notes/C13_SCHO_vs_Paper_Table7_report.md` | yes |
| classic_comparison | yes | `results/processed/D2_GWO_vs_SCHO_classic23.csv` | yes |
| classic_comparison | yes | `report/notes/D2_GWO_vs_SCHO_report.md` | yes |
| classic_comparison | yes | `report/notes/D3_StageD_final_report.md` | yes |
| cec2014 | yes | `results/raw/cec2014_e4_runs.csv` | yes |
| cec2014 | yes | `results/processed/cec2014_e4_summary.csv` | yes |
| engineering | yes | `results/raw/engineering_f4_runs.csv` | yes |
| engineering | yes | `results/processed/engineering_f4_summary.csv` | yes |
| engineering | yes | `results/processed/engineering_f5_paper_comparison.csv` | yes |
| engineering | yes | `results/processed/engineering_f5_seed_diagnostics.csv` | yes |
| engineering | yes | `report/stage_f_engineering_final.md` | yes |
| engineering | yes | `report/stage_f_manifest.csv` | yes |
| optional | no | `report/notes/F0_engineering_protocol_audit.md` | yes |
| optional | no | `report/engineering_f5_analysis.md` | yes |
| optional | no | `report/figures/D3_mean_error_to_optimum.png` | yes |
| optional | no | `report/figures/D3_mean_wins_by_family.png` | yes |
| optional | no | `report/figures/D3_std_comparison.png` | yes |

## 4. Git freeze references

| Tag | Found | Commit | Subject |
|---|---|---|---|
| `scho-source-faithful-v1` | yes | `tag scho-sou` | Freeze SCHO source-faithful baseline v1 after C9 F1 validation |
| `stage-e-cec2014-v1` | yes | `4c6ad0998705` | Freeze Stage E CEC2014 reproduction |
| `stage-f-engineering-v1` | yes | `23eab4b30f83` | Freeze Stage F engineering reproduction |

## 5. Frozen conclusions to preserve in Stage G

- Classic 23 functions: GWO and SCHO have already been reproduced and compared under the frozen project protocol; stochastic deviations should not be tuned away.
- SCHO implementation: keep the source-faithful behavior frozen, including its unusual boundary handling, dynamic bounded initialization behavior, leader/second-best behavior, and exact equation branching documented earlier.
- CEC2014: GWO broadly reproduced the paper scale; SCHO's relative advantage was not fully reproduced under the project protocol. The result must remain reported as evidence, not corrected by retuning.
- Engineering design: feasibility rate is a primary metric in addition to feasible-only objective quality. `NO_FEASIBLE_FOUND` runs must remain visible.
- Cantilever beam: keep the paper-printed 0.6224 formulation separate from the Table-20-consistent 0.06224 diagnostic; do not silently replace one with the other.
- Spring: keep the documented x3 bound correction and terminal `-1` in g2.

## 6. G0 decision

**G0 status: PASS**

All required evidence groups are present. Stage G can proceed to G1 (final tables + integrated numerical summary) without rerunning optimizers.
