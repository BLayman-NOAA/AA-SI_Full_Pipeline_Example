"""Run the reference recipe with the recipe manager and write its outputs.

Runs in an environment with the recipe manager installed.

    python run_recipe.py --raw-dir RAW --files A.raw B.raw C.raw --out run/recipe

Writes the per file Sv to OUT/sv/{stem}.zarr and each window's MVBS to
OUT/mvbs/{label}.zarr, the names compare.py expects. The recipe's own cache and
outputs go under OUT/_run.
"""

import argparse
from pathlib import Path

RECIPE = Path(__file__).resolve().parent.parent / "edf_raw2Sv_MVBS_postprocessing.yaml"


def _write(ds, path):
    """Write a dataset reloaded from a checkpoint to a fresh store.

    The checkpoint's encoding names zarr v2 codecs, which a store in another
    zarr format rejects, so it is dropped and the values are written as they are.
    """
    ds = ds.copy()
    for var in ds.variables.values():
        var.encoding = {}
    ds.to_zarr(path, mode="w")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--files", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--slice-mins", type=int, default=20)
    args = parser.parse_args()

    from aa_recipe_manager import api

    out = Path(args.out).resolve()
    run = out / "_run"
    result = api.execute(
        RECIPE,
        inputs={
            "path_raw": str(Path(args.raw_dir).resolve()),
            "raw_file_names": sorted(args.files),
            "slice_mins": args.slice_mins,
        },
        user_cache_dir=run / "user_cache",
        outputs_dir=run / "outputs",
        temp_dir=run / "exe_temp",
        force=True,
    )

    paths = result.outputs["initial_setup"]["raw_file_paths"]
    for path, ds in zip(paths, result.outputs["add_location"]["ds_Sv"]):
        _write(ds, out / "sv" / f"{Path(path).stem}.zarr")
    windows = result.outputs["plan_windows"]["windows"]
    for window, ds in zip(windows, result.outputs["window_mvbs"]["ds_MVBS"]):
        if ds is not None:
            _write(ds, out / "mvbs" / f"{window['label']}.zarr")
    print(f"Wrote {len(paths)} Sv and {len(windows)} window stores to {out}")


if __name__ == "__main__":
    main()
