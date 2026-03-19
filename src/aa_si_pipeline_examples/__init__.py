# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: NOAA Fisheries
"""
aa_si_pipeline_examples - Example pipelines for NOAA Fisheries AA-SI active acoustics data processing.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("aa-si-pipeline-examples")
except PackageNotFoundError:
    # Package is not installed (e.g., running from source without install)
    __version__ = "0.0.0.dev"

__all__ = ["__version__"]
