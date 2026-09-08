# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: NOAA Fisheries
"""Tests for the two-phase RL2307 calibration recipes.

The split into calibration_standardize.yaml and calibration_mapping.yaml only
pays for itself if the stages they share address the same cache entries, and
nothing in the recipe format enforces that: the symptom of drift is a slow run,
not an error. The two files carry those four steps as duplicate text, so these
tests are the only thing keeping the copies honest.

Run tests with: pytest
"""

from pathlib import Path

import pytest

RL2307 = Path(__file__).parent.parent / "example_recipes" / "RL2307"
PHASE1 = RL2307 / "calibration_standardize.yaml"
PHASE2 = RL2307 / "calibration_mapping.yaml"
STAGED = RL2307 / "calibration_pipeline_staged.yaml"

#: The stages both phase recipes declare. scan_raw_config is the expensive one:
#: thousands of raw files, one cache entry each.
SHARED_STEPS = (
    "initial_setup",
    "scan_raw_config",
    "record_raw_configs",
    "standardize_cal",
)


def _step_hashes(recipe, tmp_path, **extra_inputs):
    """Per-step cache hashes for *recipe*, against local placeholder folders."""
    from aa_recipe_manager import api
    from aa_recipe_manager.executor.checkpoint import compute_step_hashes

    raw = tmp_path / "raw"
    cal = tmp_path / "cal"
    raw.mkdir(exist_ok=True)
    cal.mkdir(exist_ok=True)

    inputs = {"raw_input_folder": str(raw), "cal_input_folder": str(cal)}
    inputs.update(extra_inputs)
    dag = api._load_dag(recipe, input_values=inputs)
    return compute_step_hashes(dag, inputs)


pytestmark = pytest.mark.skipif(
    not PHASE1.exists() or not PHASE2.exists(),
    reason="RL2307 phase recipes not present",
)


def test_both_phase_recipes_are_valid():
    """Each recipe builds a DAG, and only phase 2 has the mapping step."""
    from aa_recipe_manager import api

    phase1 = api.load(PHASE1)
    phase2 = api.load(PHASE2)

    assert "build_cal_mapping" not in phase1.nodes
    assert "build_cal_mapping" in phase2.nodes
    for step in SHARED_STEPS:
        assert step in phase1.nodes
        assert step in phase2.nodes


def test_shared_stages_hash_identically_across_phases(tmp_path):
    """The whole point of the split: phase 2 reuses phase 1's cached work."""
    phase1 = _step_hashes(PHASE1, tmp_path)
    phase2 = _step_hashes(PHASE2, tmp_path)

    for step in SHARED_STEPS:
        assert phase1[step] == phase2[step], (
            f"{step} hashes differ between the phase recipes, so its cache "
            f"entry would not be reused. The copy of this step in "
            f"{PHASE1.name} and the one in {PHASE2.name} have drifted; make "
            f"them identical again."
        )


def test_overrides_divert_only_the_standardize_step(tmp_path):
    """Supplied edits rewrite the folder without re-running the raw scan."""
    plain = _step_hashes(PHASE2, tmp_path)
    edited = _step_hashes(
        PHASE2, tmp_path, override_channels={"channels": [{"channel": "x"}]}
    )

    assert plain["standardize_cal"] != edited["standardize_cal"]
    for step in ("initial_setup", "scan_raw_config", "record_raw_configs"):
        assert plain[step] == edited[step]


def test_conflict_inputs_do_not_disturb_the_shared_stages(tmp_path):
    """Inputs only the mapping step reads must not invalidate anything else."""
    plain = _step_hashes(PHASE2, tmp_path)
    with_choices = _step_hashes(
        PHASE2,
        tmp_path,
        conflict_resolution="interactive",
        calibration_choices={"conflict-abc": "some-key"},
    )

    for step in SHARED_STEPS:
        assert plain[step] == with_choices[step]


@pytest.mark.skipif(not STAGED.exists(), reason="staged recipe not present")
def test_the_staged_recipe_still_shares_the_raw_scan(tmp_path):
    """The single-command recipe keeps reusing the expensive stages.

    standardize_cal is deliberately excluded: the staged recipe does not
    declare override_channels, so it addresses a different entry for that one
    cheap step.
    """
    staged = _step_hashes(STAGED, tmp_path)
    phase1 = _step_hashes(PHASE1, tmp_path)

    for step in ("initial_setup", "scan_raw_config", "record_raw_configs"):
        assert staged[step] == phase1[step]
