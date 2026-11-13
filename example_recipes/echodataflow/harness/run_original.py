"""Run echodataflow's raw to Sv and MVBS postprocessing flows on local files.

Runs in an environment with echodataflow installed. The flows start Prefect's
temporary local server; PREFECT_HOME is pointed at the output folder so the run
leaves nothing in the user's Prefect home.

    python run_original.py --raw-dir RAW --files A.raw B.raw C.raw --out run/original

Writes Sv stores to OUT/Sv/{stem}_Sv.zarr and MVBS stores to
OUT/MVBS/MVBS_{start}.zarr, as the flows name them.
"""

import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--files", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--sonar-model", default="EK80")
    parser.add_argument("--depth-offset", type=float, default=9.5)
    parser.add_argument("--slice-mins", type=int, default=20)
    parser.add_argument("--no-data-gap-hours", type=float, default=3.0)
    parser.add_argument("--range-bin", default="1m")
    parser.add_argument("--ping-time-bin", default="5s")
    args = parser.parse_args()

    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("PREFECT_HOME", str(out / ".prefect"))

    import pandas as pd

    from echodataflow.flows.flows_acoustics import (
        flow_create_MVBS_postprocessing,
        flow_raw2Sv_postprocessing,
    )

    raw_list = out / "raw_files.csv"
    pd.DataFrame({"s3_path": sorted(args.files)}).to_csv(raw_list, index=False)

    flow_raw2Sv_postprocessing(
        path_raw_list=str(raw_list),
        path_raw=str(Path(args.raw_dir).resolve()),
        path_main=str(out),
        sonar_model=args.sonar_model,
        depth_offset=args.depth_offset,
        waveform_mode="CW",
        encode_mode="power",
    )
    flow_create_MVBS_postprocessing(
        path_main=str(out),
        slice_mins=args.slice_mins,
        no_data_gap_hours=args.no_data_gap_hours,
        range_bin=args.range_bin,
        ping_time_bin=args.ping_time_bin,
        remove_completed_Sv_files=False,
    )
    print(f"Sv stores: {sorted(p.name for p in (out / 'Sv').glob('*.zarr'))}")
    print(f"MVBS stores: {sorted(p.name for p in (out / 'MVBS').glob('*.zarr'))}")


if __name__ == "__main__":
    main()
