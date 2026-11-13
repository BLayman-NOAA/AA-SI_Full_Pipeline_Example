"""Compare the Sv and MVBS stores of two runs and print a markdown table.

Each run is a folder in one of three layouts, recognised from its contents:

    original   Sv/{stem}_Sv.zarr      MVBS/MVBS_{label}.zarr    (echodataflow flows)
    recipe     sv/{stem}.zarr         mvbs/{label}.zarr         (run_recipe.py)
    compiled   add_location/{stem}.zarr  window_mvbs/{label}.zarr  (generated flow)

    python compare.py run/original run/recipe --atol 1e-4

Stores are paired by name. For each pair the shared data variables are compared
with NaN equal to NaN, and the coordinates the two share are checked exactly.
Variables present on one side only are listed, not counted as differences.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import xarray as xr

_LAYOUTS = {
    "original": {"sv": ("Sv", "_Sv"), "mvbs": ("MVBS", None)},
    "recipe": {"sv": ("sv", ""), "mvbs": ("mvbs", "")},
    "compiled": {"sv": ("add_location", ""), "mvbs": ("window_mvbs", "")},
}


def _layout(run):
    if (run / "Sv").is_dir() or (run / "MVBS").is_dir():
        return "original"
    if (run / "add_location").is_dir():
        return "compiled"
    return "recipe"


def _stores(run, kind):
    folder, suffix = _LAYOUTS[_layout(run)][kind]
    found = {}
    for path in sorted((run / folder).glob("*.zarr")):
        name = path.name[: -len(".zarr")]
        if kind == "mvbs" and name.startswith("MVBS_"):
            name = name[len("MVBS_"):]
        elif suffix and name.endswith(suffix):
            name = name[: -len(suffix)]
        found[name] = path
    return found


def _max_abs_diff(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.shape != b.shape:
        return None
    nan_a, nan_b = np.isnan(a), np.isnan(b)
    if (nan_a != nan_b).any():
        return float("inf")
    both = ~nan_a
    return float(np.max(np.abs(a[both] - b[both]))) if both.any() else 0.0


def compare_pair(left, right, atol):
    """Return rows of (variable, result, ok) for one pair of stores."""
    a = xr.open_dataset(left, engine="zarr", chunks=None)
    b = xr.open_dataset(right, engine="zarr", chunks=None)
    rows = []
    for coord in sorted(set(a.coords) & set(b.coords)):
        if coord in a.dims and coord in b.dims:
            same = a[coord].shape == b[coord].shape and bool(
                (a[coord].values == b[coord].values).all()
            )
            rows.append((f"coord {coord}", "equal" if same else "DIFFERS", same))
    for name in sorted(set(a.data_vars) & set(b.data_vars)):
        if a[name].dtype.kind not in "fiu" or b[name].dtype.kind not in "fiu":
            continue
        a_var, b_var = xr.align(a[name], b[name], join="outer")
        diff = _max_abs_diff(a_var.transpose(*a[name].dims).values,
                             b_var.transpose(*a[name].dims).values)
        if diff is None:
            rows.append((name, f"shape {a[name].shape} vs {b[name].shape}", False))
        else:
            rows.append((name, f"max abs diff {diff:.3g}", diff <= atol))
    only_a = sorted(set(a.data_vars) - set(b.data_vars))
    only_b = sorted(set(b.data_vars) - set(a.data_vars))
    if only_a:
        rows.append(("only in left", ", ".join(only_a), True))
    if only_b:
        rows.append(("only in right", ", ".join(only_b), True))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("left")
    parser.add_argument("right")
    parser.add_argument("--atol", type=float, default=1e-4)
    args = parser.parse_args()
    left, right = Path(args.left), Path(args.right)

    print(f"Comparing {left} ({_layout(left)}) with {right} ({_layout(right)}), "
          f"atol {args.atol}\n")
    print("| kind | store | check | result |")
    print("|---|---|---|---|")
    failures = 0
    for kind in ("sv", "mvbs"):
        a, b = _stores(left, kind), _stores(right, kind)
        for name in sorted(set(a) | set(b)):
            if name not in a or name not in b:
                side = "left" if name in a else "right"
                print(f"| {kind} | {name} | present | only in {side} |")
                failures += 1
                continue
            for check, result, ok in compare_pair(a[name], b[name], args.atol):
                print(f"| {kind} | {name} | {check} | {result}{'' if ok else ' FAIL'} |")
                failures += not ok
    print(f"\n{failures} failing check(s).")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
