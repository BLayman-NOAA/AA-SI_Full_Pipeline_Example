"""Check a generated flow folder against echodataflow's deployment contract.

Runs in an environment with echodataflow installed. The generated module is
registered in memory, as echodataflow's own registry tests do, so nothing is
copied into the echodataflow checkout. The check runs echodataflow's deploy
config validation, flow coverage check, registry resolution and deployment spec
build, and stops short of creating deployments on a Prefect server.

    python check_deploy.py run/gen
"""

import argparse
import importlib.util
import re
import sys
from pathlib import Path

import yaml


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder")
    args = parser.parse_args()
    folder = Path(args.folder).resolve()

    from echodataflow.deployment import deployment_engine as engine
    from echodataflow.deployment.flow_registry import FLOW_REGISTRY, FlowRegistration

    entry = (folder / "flow_registry_entry.txt").read_text(encoding="utf-8")
    slug = re.search(r'^\s+"(\w+)": FlowRegistration\(', entry, re.M).group(1)
    entrypoint = re.search(r'entrypoint="([^"]+)"', entry).group(1)
    module_path = folder / Path(entrypoint.partition(":")[0]).name

    module_name = entrypoint.partition(":")[0].removesuffix(".py").replace("/", ".")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    FLOW_REGISTRY[slug] = FlowRegistration(entrypoint=entrypoint)

    params = yaml.safe_load((folder / f"params.{slug}.yaml").read_text())
    deploy = yaml.safe_load((folder / f"deploy.{slug}.yaml").read_text())
    engine.validate_deploy_config(deploy)
    engine.validate_flow_coverage(params, deploy)
    resolved = engine.resolve_registered_flows(deploy)
    specs = engine.build_deploy_specs(
        param_cfg=params, deploy_cfg=deploy, resolved_flows=resolved
    )

    for spec_ in specs:
        unknown = [
            name for name in spec_.parameters
            if not engine._flow_accepts_parameter(spec_.flow_obj, name)
        ]
        print(f"flow key: {spec_.flow_key}")
        print(f"deployment: {spec_.deployment_name}")
        print(f"entrypoint: {spec_.entrypoint}")
        print(f"flow object: {type(spec_.flow_obj).__name__} {spec_.flow_obj.name!r}")
        print(f"parameters: {sorted(spec_.parameters)}")
        print(f"schedule: cron={spec_.cron} triggers={spec_.triggers}")
        if unknown:
            print(f"parameters the flow does not accept: {unknown}")
            sys.exit(1)
    print("Deployment contract checks passed.")


if __name__ == "__main__":
    main()
