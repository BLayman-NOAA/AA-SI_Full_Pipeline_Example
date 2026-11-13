"""Compare a recipe run's checkpoints with a compiled flow's stores, step by step.

    python compare_steps.py RECIPE_CACHE COMPILED_OUT merge_sv remove_noise compute_mvbs

RECIPE_CACHE is the recipe manager's user cache folder, holding
STEP/HASH/RUN/zarr/OUTPUT.zarr. COMPILED_OUT is the flow's output_dir, holding
STEP.zarr, STEP/OUTPUT.zarr, or STEP/ITEM.zarr for a mapped step. A mapped step's
stores are paired by their first ping_time. Prints a markdown table as
compare.py does, and exits non zero on any failing check.
"""

import argparse
import sys
from pathlib import Path

import xarray as xr

from compare import compare_pair


def _first_ping(path):
    ds = xr.open_dataset(path, engine="zarr", chunks=None)
    return str(ds["ping_time"].values[0]) if "ping_time" in ds.coords else path.name


def _pairs(cache, out, step):
    recipe = sorted((cache / step).glob("*/*/zarr/*.zarr"))
    single = out / f"{step}.zarr"
    compiled = [single] if single.is_dir() else sorted((out / step).glob("*.zarr"))
    if len(recipe) == 1 and len(compiled) == 1:
        return [(recipe[0].stem, recipe[0], compiled[0])], []
    left = {_first_ping(p): p for p in recipe}
    right = {_first_ping(p): p for p in compiled}
    pairs = [(key, left[key], right[key]) for key in sorted(set(left) & set(right))]
    missing = sorted(set(left) ^ set(right))
    return pairs, missing


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("recipe_cache")
    parser.add_argument("compiled_out")
    parser.add_argument("steps", nargs="+")
    parser.add_argument("--atol", type=float, default=1e-12)
    args = parser.parse_args()
    cache, out = Path(args.recipe_cache), Path(args.compiled_out)

    print("| step | store | check | result |")
    print("|---|---|---|---|")
    failures = 0
    for step in args.steps:
        pairs, missing = _pairs(cache, out, step)
        if not pairs:
            print(f"| {step} | | present | no stores to pair |")
            failures += 1
        for key in missing:
            print(f"| {step} | {key} | present | on one side only |")
            failures += 1
        for key, left, right in pairs:
            for check, result, ok in compare_pair(left, right, args.atol):
                print(f"| {step} | {key} | {check} | {result}{'' if ok else ' FAIL'} |")
                failures += not ok
    print(f"\n{failures} failing check(s).")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
