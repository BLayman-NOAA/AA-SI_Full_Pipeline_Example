"""Run a generated echodataflow flow module.

Runs in an environment with echodataflow installed. The module is imported from
its file, so it need not be copied into echodataflow first.

    python run_compiled.py MODULE.py --out run/compiled --raw-dir RAW --files A.raw B.raw
    python run_compiled.py MODULE.py --out run/h --raw-input-folder gs://... \
        --file-time-start 2024-11-06T09:02:05

--raw-dir and --files fill the reference recipe's path_raw and raw_file_names.
Every other option is passed to the flow as a parameter, so --slice-mins 10
becomes slice_mins=10. Values are read as Python literals where they parse.
"""

import argparse
import ast
import importlib.util
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("module")
    parser.add_argument("--out", required=True)
    parser.add_argument("--raw-dir")
    parser.add_argument("--files", nargs="+")
    args, extra = parser.parse_known_args()

    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("PREFECT_HOME", str(out / ".prefect"))

    params = {}
    for flag, value in zip(extra[::2], extra[1::2]):
        name = flag.lstrip("-").replace("-", "_")
        try:
            params[name] = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            params[name] = value
    if args.raw_dir:
        params["path_raw"] = str(Path(args.raw_dir).resolve())
    if args.files:
        params["raw_file_names"] = sorted(args.files)

    path = Path(args.module).resolve()
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    flow = next(getattr(module, n) for n in dir(module) if n.startswith("flow_"))
    flow(output_dir=str(out), **params)


if __name__ == "__main__":
    main()
