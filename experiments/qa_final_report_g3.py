"""G3 v3 - Final report consistency and formatting QA.

Fixes the overly brittle engineering-total text check from v1/v2.
No scientific result or report content is changed.
"""

from __future__ import annotations
import csv
import shutil
from pathlib import Path

DRAFT = Path("report/final_reproduction_report_draft.md")
CLAIMS = Path("report/tables/stage_g2_claims_matrix.csv")
G1_OVERVIEW = Path("report/tables/stage_g1_overview.csv")
G1_CLASSIC = Path("report/tables/stage_g1_classic_family_summary.csv")
G1_ENGINEERING = Path("report/tables/stage_g1_engineering_summary.csv")

FINAL = Path("report/final_reproduction_report.md")
QA_REPORT = Path("report/stage_g3_qa_report.md")
QA_CSV = Path("report/tables/stage_g3_qa_checks.csv")


def require(path):
    if not path.exists():
        raise FileNotFoundError(f"Required G3 input missing: {path}")


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def add(checks, category, name, passed, detail):
    checks.append({
        "category": category,
        "check": name,
        "passed": bool(passed),
        "detail": detail,
    })


def main():
    print("=" * 118)
    print("G3 v3 - Final report consistency / formatting QA")
    print("=" * 118)
    print("No optimizer will be executed.")
    print("=" * 118)

    for p in [DRAFT, CLAIMS, G1_OVERVIEW, G1_CLASSIC, G1_ENGINEERING]:
        require(p)

    draft = DRAFT.read_text(encoding="utf-8")
    claims = read_csv(CLAIMS)
    overview = read_csv(G1_OVERVIEW)
    classic = read_csv(G1_CLASSIC)
    engineering = read_csv(G1_ENGINEERING)

    checks = []

    required_sections = [
        "## 摘要",
        "## 1. 研究目标与复现原则",
        "## 2. 算法实现",
        "## 3. 经典 F1–F23",
        "## 4. CEC2014",
        "## 5. 工程设计",
        "## 6. Source anomalies",
        "## 7. 综合讨论",
        "## 8. 局限性",
        "## 9. 可复现性",
        "## 10. 结论",
        "## Appendix A",
        "## Appendix B",
        "## Appendix C",
        "## Appendix D",
    ]
    missing = [s for s in required_sections if s not in draft]
    add(checks, "structure", "required_sections", not missing,
        "all present" if not missing else "missing: " + "; ".join(missing))

    add(checks, "structure", "claims_matrix_rows", len(claims) == 10, f"{len(claims)} rows")
    add(checks, "structure", "g1_overview_rows", len(overview) == 3, f"{len(overview)} rows")
    add(checks, "structure", "g1_classic_family_rows", len(classic) == 3, f"{len(classic)} rows")
    add(checks, "structure", "g1_engineering_rows", len(engineering) == 12, f"{len(engineering)} rows")

    frozen = [
        ("classic headline", ["GWO lower mean 8", "SCHO 12", "Tie 3"]),
        ("classic family F1-F7", ["F1–F7", "1/4/2"]),
        ("classic family F8-F13", ["F8–F13", "2/3/1"]),
        ("classic family F14-F23", ["F14–F23", "5/5/0"]),
        ("CEC paper-scale agreement", ["22/30", "14/30", "26/30"]),
        ("CEC pairwise comparison", ["GWO 22", "SCHO 8", "9 个 pairwise flip"]),
        ("speed reducer feasibility", ["GWO 仅 1/30", "SCHO 为 14/30"]),
        ("welded beam feasibility", ["GWO 18/30", "SCHO 19/30"]),
        ("spring anomaly", ["+0.9999994", "-6.0e-7"]),
        ("cantilever anomaly", ["0.6224*sum(x)", "13.0326", "1.3033", "0.06224*sum(x)"]),
        ("freeze tags", ["scho-source-faithful-v1", "stage-e-cec2014-v1", "stage-f-engineering-v1"]),
    ]
    for name, fragments in frozen:
        ok = all(x in draft for x in fragments)
        add(checks, "frozen_claim", name, ok,
            "found" if ok else "missing one or more required fragments")

    # Semantic engineering-total check: accept the actual G2 wording.
    eng_row = next((r for r in overview if r.get("domain") == "Engineering design"), None)
    draft_ok = (
        "288 次 feasible" in draft
        and "72 次 `NO_FEASIBLE_FOUND`" in draft
        and (
            "0 structural failures" in draft
            or "结构性失败为 0" in draft
            or "结构性失败 0" in draft
        )
    )
    overview_ok = bool(
        eng_row
        and "Feasible runs: 288/360" in eng_row.get("headline_1", "")
        and "NO_FEASIBLE_FOUND: 72/360" in eng_row.get("headline_2", "")
        and "Structural failures: 0" in eng_row.get("headline_3", "")
    )
    add(
        checks, "frozen_claim", "engineering totals",
        draft_ok and overview_ok,
        f"draft_ok={draft_ok}; overview_ok={overview_ok}"
    )

    expected_ids = {f"C{i:02d}" for i in range(1, 11)}
    actual_ids = {r.get("claim_id", "") for r in claims}
    add(checks, "claims", "claim_ids_C01_C10", actual_ids == expected_ids,
        f"ids={sorted(actual_ids)}")

    non_frozen = [r.get("claim_id", "") for r in claims
                  if r.get("status", "").strip().lower() != "frozen"]
    add(checks, "claims", "all_claims_frozen", not non_frozen,
        "all frozen" if not non_frozen else "non-frozen: " + ", ".join(non_frozen))

    bad_phrases = [
        "bitwise identical to MATLAB",
        "exactly reproduces MATLAB random numbers",
        "SCHO is universally superior",
        "GWO is universally superior",
        "proves SCHO is better",
        "proves GWO is better",
        "0.06224 is the correct paper formula",
    ]
    found_bad = [p for p in bad_phrases if p.lower() in draft.lower()]
    add(checks, "wording", "no_overclaim_phrases", not found_bad,
        "none found" if not found_bad else "found: " + "; ".join(found_bad))

    required_caveats = [
        "NumPy RNG",
        "不主张 MATLAB bitwise reproduction",
        "project reproduction convention",
        "NO_FEASIBLE_FOUND",
        "table-consistent diagnostic",
        "不为了贴近论文而事后调参",
    ]
    missing_caveats = [c for c in required_caveats if c not in draft]
    add(checks, "wording", "required_caveats_present", not missing_caveats,
        "all present" if not missing_caveats else "missing: " + "; ".join(missing_caveats))

    no_placeholder = "TODO" not in draft and "TBD" not in draft
    add(checks, "format", "no_TODO_placeholder", no_placeholder,
        "none found" if no_placeholder else "placeholder found")
    add(checks, "format", "nontrivial_report_length", len(draft) >= 8000,
        f"{len(draft)} characters")

    failed = [c for c in checks if not c["passed"]]

    QA_CSV.parent.mkdir(parents=True, exist_ok=True)
    with QA_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "check", "passed", "detail"])
        writer.writeheader()
        writer.writerows(checks)

    lines = [
        "# Stage G3 — Final Report QA",
        "",
        f"- Total checks: **{len(checks)}**",
        f"- Passed: **{len(checks)-len(failed)}**",
        f"- Failed: **{len(failed)}**",
        "",
        "| Category | Check | Result | Detail |",
        "|---|---|---|---|",
    ]
    for c in checks:
        detail = str(c["detail"]).replace("|", "\\|")
        lines.append(
            f"| {c['category']} | {c['check']} | "
            f"{'PASS' if c['passed'] else 'FAIL'} | {detail} |"
        )

    lines += ["", "## Decision", ""]
    if failed:
        lines += ["**G3 RESULT: FAIL**", "",
                  "The G2 draft was not promoted to the final Markdown candidate."]
    else:
        FINAL.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(DRAFT, FINAL)
        lines += [
            "**G3 RESULT: PASS**",
            "",
            "The audited G2 draft was promoted byte-for-byte to "
            "`report/final_reproduction_report.md`."
        ]

    QA_REPORT.parent.mkdir(parents=True, exist_ok=True)
    QA_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\nQA summary")
    print("-" * 118)
    print(f"Checks : {len(checks)}")
    print(f"Passed : {len(checks)-len(failed)}")
    print(f"Failed : {len(failed)}")

    if failed:
        print("\nFailed checks")
        print("-" * 118)
        for c in failed:
            print(f"{c['category']} / {c['check']}: {c['detail']}")

    print("\nOutputs")
    print("-" * 118)
    print(f"QA report : {QA_REPORT}")
    print(f"QA CSV    : {QA_CSV}")
    if not failed:
        print(f"Final MD  : {FINAL}")

    if failed:
        print("\nG3 RESULT: FAIL")
        raise SystemExit(1)

    print("\nG3 RESULT: PASS")
    print("Final Markdown candidate created.")
    print("No optimizer was rerun.")
    print("No frozen numerical conclusion was changed.")
    print("Stage G is ready for G4 final freeze.")


if __name__ == "__main__":
    main()
