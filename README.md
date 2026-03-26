<!-- markdownlint-disable MD033 MD041 -->

<div align="center">

# AA-SI Full Pipeline Examples

**Example Jupyter notebooks demonstrating end-to-end active acoustics data processing for NOAA Fisheries AA-SI**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Getting Started](#getting-started) •
[Example Notebooks](#example-notebooks) •
[Project Structure](#project-structure)

</div>

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/) for dependency management

### Installation

```bash
# Clone the repository
git clone https://github.com/BLayman-NOAA/AA-SI_Full_Pipeline_Example.git
cd AA-SI_Full_Pipeline_Example

# Install dependencies with Poetry
poetry install

# Set up pre-commit hooks (optional)
poetry run pre-commit install
```

### Running the Notebooks

After installation, open any notebook in `example_notebooks/` with JupyterLab or VS Code:

```bash
poetry run jupyter lab
```

Select the Poetry environment as your Jupyter kernel.

---

## Example Notebooks

| Notebook | Description |
|----------|-------------|
| [NEFSC Use Case 1](example_notebooks/NEFSC_use_case_example_1/) | End-to-end pipeline with EK60 data: raw conversion, calibration comparison, Sv computation, and visualization |
| [NEFSC Use Case 2](example_notebooks/NEFSC_use_case_example_2/) | Extended pipeline with multi-file combination, ML clustering (HDBSCAN), and 3D PyVista export |
| [NEFSC Use Case 2 (Refactored)](example_notebooks/NEFSC_use_case_example_2_refactored/) | Refactored version of Use Case 2 |
| [Zooplankton Example](example_notebooks/zooplankton_example/) | Zooplankton-focused processing pipeline |

### AA-SI Packages Used

These notebooks demonstrate the following AA-SI packages working together:

- **[aa-si-calibration](https://github.com/BLayman-NOAA/AA-SI_calibration)** — Calibration parameter extraction, standardized file I/O, and calibration comparison
- **[aa-si-ml](https://github.com/BLayman-NOAA/AA-SI_ML)** — ML-based data preprocessing and HDBSCAN clustering
- **[aa-si-utils](https://github.com/BLayman-NOAA/AA-SI_Utils)** — Masking, seafloor removal, and general utilities
- **[aa-si-visualization](https://github.com/BLayman-NOAA/AA-SI_Visualization)** — Echogram plotting and Sv difference visualization

---

## Project Structure

```
├── pyproject.toml              # Dependency management (Poetry)
├── README.md
├── CHANGELOG.md
├── LICENSE
├── NOTICE
├── example_notebooks/
│   ├── calibration_files/      # Shared calibration data
│   ├── line_files/             # Shared line/overlay data
│   ├── NEFSC_use_case_example_1/
│   │   ├── NEFSC_use_case_example_1.ipynb
│   │   ├── NEFSC_use_case_1_raw_files/
│   │   ├── NetCDF-files/
│   │   ├── Sv-files/
│   │   ├── Output-Logs/
│   │   └── standardized_cal_files/
│   ├── NEFSC_use_case_example_2/
│   │   └── ...
│   ├── NEFSC_use_case_example_2_refactored/
│   │   └── ...
│   └── zooplankton_example/
│       └── ...
└── tests/
```

---

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

---

## Disclaimer

This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration, or the United States Department of Commerce. All NOAA GitHub project code is provided on an ‘as is’ basis and the user assumes responsibility for its use. Any claims against the Department of Commerce or Department of Commerce bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.
