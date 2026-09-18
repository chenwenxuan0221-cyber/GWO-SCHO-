"""G0 - Final report evidence audit and structure freeze.

Purpose
-------
Stage G starts by checking that the major evidence from Stages A-F exists
before any final narrative is written. This script does NOT rerun optimizers
and does NOT modify frozen algorithm implementations.

It validates:
- classic-function evidence from Stages A-D
- CEC2014 evidence from Stage E
- engineering-design evidence from Stage F
- important Git freeze tags when available

Outputs
-------
report/stage_g0_evidence_audit.md
report/stage_g0_evidence_manifest.csv

This is a report-preparation audit, not a scientific re-analysis.
"""

from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path


OUT_REPORT = Path("report/stage_g0_evidence_audit.md")
OUT_MANIFEST = Path("report/stage_g0_evidence_manifest.csv")


# Required evidence that should exist for the final report.
# Some early-stage filenames reflect the existing project history.
EVIDENCE_GROUPS = {
    "classic_gwo": [
        Path("results/processed/gwo_classic23_results.csv"),
        Path("results/processed/gwo_stageB_summary.csv"),
        Path("report/notes/gwo_stageB_report.md"),
    ],
    "classic_scho": [
        Path("results/processed/scho_classic23_summary.csv"),
        Path("report/notes/C13_SCHO_vs_Paper_Table7_report.md"),
    ],
    "classic_comparison": [
        Path("results/processed/D2_GWO_vs_SCHO_classic23.csv"),
        Path("report/notes/D2_GWO_vs_SCHO_report.md"),
        Path("report/notes/D3_StageD_final_report.md"),
    ],
    "cec2014": [
        Path("results/raw/cec2014_e4_runs.csv"),
        Path("results/processed/cec2014_e4_summary.csv"),
    ],
    "engineering": [
        Path("results/raw/engineering_f4_runs.csv"),
        Path("results/processed/engineering_f4_summary.csv"),
        Path("results/processed/engineering_f5_paper_comparison.csv"),
        Path("results/processed/engineering_f5_seed_diagnostics.csv"),
        Path("report/stage_f_engineering_final.md"),
        Path("report/stage_f_manifest.csv"),
    ],
}

OPTIONAL_EVIDENCE = [
    Path("report/notes/F0_engineering_protocol_audit.md"),
    Path("report/engineering_f5_analysis.md"),
    Path("report/figures/D3_mean_error_to_optimum.png"),
    Path("report/figures/D3_mean_wins_by_family.png"),
    Path("report/figures/D3_std_comparison.png"),
]


FREEZE_TAGS = [
    "scho-source-faithful-v1",
    "stage-e-cec2014-v1",
    "stage-f-engineering-v1",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_tag_target(tag: str):
    try:
        result = subprocess.run(
            ["git", "show", "--no-patch", "--format=%H|%s", tag],
            check=True,
            text=True,
            capture_output=True,
        )
        text = result.stdout.strip()
        if "|" in text:
            commit, subject = text.split("|", 1)
        else:
            commit, subject = text, ""
        return True, commit, subject
    except Exception as exc:
        return False, "", str(exc)


def build_manifest():
    rows = []
    missing_required = []

    for group, paths in EVIDENCE_GROUPS.items():
        for path in paths:
            exists = path.exists()
            if not exists:
                missing_required.append((group, path))
            rows.append({
                "group": group,
                "required": True,
                "path": str(path).replace("\\", "/"),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else "",
                "sha256": sha256_file(path) if exists else "",
            })

    for path in OPTIONAL_EVIDENCE:
        exists = path.exists()
        rows.append({
            "group": "optional",
            "required": False,
            "path": str(path).replace("\\", "/"),
            "exists": exists,
            "size_bytes": path.stat().st_size if exists else "",
            "sha256": sha256_file(path) if exists else "",
        })

    return rows, missing_required


def write_manifest(rows):
    OUT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with OUT_MANIFEST.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "group",
                "required",
                "path",
                "exists",
                "size_bytes",
                "sha256",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def build_report(rows, missing_required, tag_info):
    lines = []
    lines.append("# Stage G0 — Final Report Evidence Audit")
    lines.append("")
    lines.append("## 1. 目的")
    lines.append("")
    lines.append(
        "Stage G0 不重新运行任何优化器。它只检查最终报告所需的主要证据是否已经存在，"
        "并冻结 Stage G 的报告结构。"
    )
    lines.append("")

    lines.append("## 2. Final report structure")
    lines.append("")
    lines.append("最终报告建议按以下顺序组织：")
    lines.append("")
    lines.append("1. Introduction and reproduction goals")
    lines.append("2. Algorithms: GWO and source-faithful SCHO")
    lines.append("3. Reproduction protocol and implementation principles")
    lines.append("4. Classic 23 benchmark reproduction")
    lines.append("5. GWO vs SCHO comparison on classic benchmarks")
    lines.append("6. CEC2014 reproduction")
    lines.append("7. Engineering-design reproduction")
    lines.append("8. Source anomalies and implementation caveats")
    lines.append("9. Overall findings and limitations")
    lines.append("10. Reproducibility / Git freeze information")
    lines.append("")

    lines.append("## 3. Evidence audit")
    lines.append("")
    lines.append("| Group | Required | File | Exists |")
    lines.append("|---|---|---|---|")
    for row in rows:
        lines.append(
            f"| {row['group']} | "
            f"{'yes' if row['required'] else 'no'} | "
            f"`{row['path']}` | "
            f"{'yes' if row['exists'] else 'NO'} |"
        )
    lines.append("")

    lines.append("## 4. Git freeze references")
    lines.append("")
    lines.append("| Tag | Found | Commit | Subject |")
    lines.append("|---|---|---|---|")
    for tag, info in tag_info.items():
        found, commit, subject = info
        lines.append(
            f"| `{tag}` | {'yes' if found else 'NO'} | "
            f"`{commit[:12] if commit else ''}` | {subject} |"
        )
    lines.append("")

    lines.append("## 5. Frozen conclusions to preserve in Stage G")
    lines.append("")
    lines.append(
        "- Classic 23 functions: GWO and SCHO have already been reproduced and "
        "compared under the frozen project protocol; stochastic deviations should "
        "not be tuned away."
    )
    lines.append(
        "- SCHO implementation: keep the source-faithful behavior frozen, including "
        "its unusual boundary handling, dynamic bounded initialization behavior, "
        "leader/second-best behavior, and exact equation branching documented earlier."
    )
    lines.append(
        "- CEC2014: GWO broadly reproduced the paper scale; SCHO's relative advantage "
        "was not fully reproduced under the project protocol. The result must remain "
        "reported as evidence, not corrected by retuning."
    )
    lines.append(
        "- Engineering design: feasibility rate is a primary metric in addition to "
        "feasible-only objective quality. `NO_FEASIBLE_FOUND` runs must remain visible."
    )
    lines.append(
        "- Cantilever beam: keep the paper-printed 0.6224 formulation separate from "
        "the Table-20-consistent 0.06224 diagnostic; do not silently replace one with the other."
    )
    lines.append(
        "- Spring: keep the documented x3 bound correction and terminal `-1` in g2."
    )
    lines.append("")

    lines.append("## 6. G0 decision")
    lines.append("")
    if missing_required:
        lines.append("**G0 status: INCOMPLETE**")
        lines.append("")
        lines.append("Missing required evidence:")
        lines.append("")
        for group, path in missing_required:
            lines.append(f"- `{group}`: `{path}`")
        lines.append("")
        lines.append(
            "Do not draft the final integrated report until these files are located "
            "or the report scope is explicitly adjusted."
        )
    else:
        lines.append("**G0 status: PASS**")
        lines.append("")
        lines.append(
            "All required evidence groups are present. Stage G can proceed to G1 "
            "(final tables + integrated numerical summary) without rerunning optimizers."
        )

    return "\n".join(lines) + "\n"


def main():
    print("=" * 116)
    print("G0 - Final report evidence audit")
    print("=" * 116)
    print("No optimizer will be executed.")
    print("Checking Stages A-F evidence and freeze tags...")
    print("=" * 116)

    rows, missing_required = build_manifest()
    write_manifest(rows)

    tag_info = {
        tag: git_tag_target(tag)
        for tag in FREEZE_TAGS
    }

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(
        build_report(rows, missing_required, tag_info),
        encoding="utf-8",
    )

    required_total = sum(
        1 for row in rows if row["required"]
    )
    required_found = sum(
        1 for row in rows if row["required"] and row["exists"]
    )

    print("\nEvidence")
    print("-" * 116)
    print(f"Required files found : {required_found}/{required_total}")
    print(f"Missing required     : {len(missing_required)}")

    print("\nFreeze tags")
    print("-" * 116)
    for tag, (found, commit, subject) in tag_info.items():
        if found:
            print(f"{tag:<28} {commit[:12]}  {subject}")
        else:
            print(f"{tag:<28} NOT FOUND")

    print("\nOutputs")
    print("-" * 116)
    print(f"Audit report : {OUT_REPORT}")
    print(f"Manifest     : {OUT_MANIFEST}")

    if missing_required:
        print("\nG0 RESULT: INCOMPLETE")
        for group, path in missing_required:
            print(f"  missing [{group}] {path}")
        raise SystemExit(1)

    print("\nG0 RESULT: PASS")
    print("All required evidence groups are present.")
    print("No optimizer was rerun.")
    print("Stage G is ready for G1 final tables and integrated numerical summary.")


if __name__ == "__main__":
    main()
