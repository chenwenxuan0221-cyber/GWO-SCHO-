import csv
from pathlib import Path

PAPER_GWO_MEAN = {
    "F1": 6.59e-28, "F2": 7.18e-17, "F3": 3.29e-06, "F4": 5.61e-07,
    "F5": 26.81258, "F6": 0.816579, "F7": 0.002213,
    "F8": -6123.1, "F9": 0.310521, "F10": 1.06e-13, "F11": 0.004485,
    "F12": 0.053438, "F13": 0.654464,
    "F14": 4.042493, "F15": 0.000337, "F16": -1.03163, "F17": 0.397889,
    "F18": 3.000028, "F19": -3.86263, "F20": -3.28654, "F21": -10.1514,
    "F22": -10.4015, "F23": -10.5343,
}

# IMPORTANT:
# These are copied exactly from the GWO paper's printed "Std" column.
# The paper itself contains internally inconsistent entries:
# - F8 is printed with a negative Std.
# - Table 7 entries from F16 onward appear inconsistent with a standard deviation.
# Therefore they are preserved as source data, not silently corrected.
PAPER_GWO_STD_AS_PRINTED = {
    "F1": 6.34e-05, "F2": 0.029014, "F3": 79.14958, "F4": 1.315088,
    "F5": 69.90499, "F6": 0.000126, "F7": 0.100286,
    "F8": -4087.44, "F9": 47.35612, "F10": 0.077835, "F11": 0.006659,
    "F12": 0.020734, "F13": 0.004474,
    "F14": 4.252799, "F15": 0.000625, "F16": -1.03163, "F17": 0.397887,
    "F18": 3.0, "F19": -3.86278, "F20": -3.25056, "F21": -9.14015,
    "F22": -8.58441, "F23": -8.55899,
}

def paper_table(function_name):
    n = int(function_name[1:])
    if n <= 7:
        return "Table 5"
    if n <= 13:
        return "Table 6"
    return "Table 7"

def paper_std_status(function_name):
    n = int(function_name[1:])
    if function_name == "F8":
        return "Paper prints a negative Std; retain raw value, do not use for Std error"
    if n >= 16:
        return "Table 7 GWO Std entry appears inconsistent; retain raw printed value"
    return "OK as printed"

def build_comparison(
    input_csv="results/processed/gwo_classic23_results.csv",
    output_csv="results/processed/gwo_classic23_comparison.csv",
):
    input_csv = Path(input_csv)
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with input_csv.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    comparison = []
    for r in rows:
        fn = r["Function"]
        our_mean = float(r["Mean"])
        our_std = float(r["Std"])
        paper_mean = PAPER_GWO_MEAN[fn]
        paper_std = PAPER_GWO_STD_AS_PRINTED[fn]

        mean_diff = our_mean - paper_mean
        abs_mean_diff = abs(mean_diff)
        rel_pct = abs_mean_diff / abs(paper_mean) * 100 if paper_mean != 0 else None

        status = paper_std_status(fn)
        std_diff = our_std - paper_std if status == "OK as printed" else None

        comparison.append({
            "Function": fn,
            "Our_Mean": our_mean,
            "Paper_Mean": paper_mean,
            "Mean_Difference": mean_diff,
            "Abs_Mean_Difference": abs_mean_diff,
            "Mean_Relative_Error_pct": rel_pct,
            "Our_Std": our_std,
            "Paper_Std_As_Printed": paper_std,
            "Std_Difference": std_diff,
            "Abs_Std_Difference": abs(std_diff) if std_diff is not None else None,
            "Best": float(r["Best"]),
            "Worst": float(r["Worst"]),
            "Theoretical_Optimum": float(r["Theoretical_Optimum"]),
            "Paper_Table": paper_table(fn),
            "Paper_Std_Status": status,
        })

    fieldnames = list(comparison[0].keys())
    with output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(comparison)

    print(f"Comparison table saved to: {output_csv}")
    return comparison

if __name__ == "__main__":
    build_comparison()
