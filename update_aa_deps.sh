#!/usr/bin/env bash
# Pull this repo and reinstall the AA-SI dependencies at the latest commit on
# their default branches.
#
# Usage:
#   ./update_aa_deps.sh            # pull, re-resolve the AA-SI git deps, install
#   ./update_aa_deps.sh --clean    # also wipe poetry.lock, the poetry caches, and the venv
#   ./update_aa_deps.sh --no-pull  # leave this repo's checkout alone

set -euo pipefail

cd "$(dirname "$0")"

clean=0
pull=1
for arg in "$@"; do
    case "$arg" in
        --clean) clean=1 ;;
        --no-pull) pull=0 ;;
        -h|--help) sed -n '2,8p' "$0" | sed 's/^# \?//'; exit 0 ;;
        *) echo "unknown option: $arg" >&2; exit 2 ;;
    esac
done

# The AA-SI packages are the pyproject dependencies pinned to a git URL, so
# reading them back out keeps this script in sync with pyproject.toml.
mapfile -t packages < <(sed -n 's/^\(aa-[a-z0-9-]*\) *=.*git *=.*/\1/p' pyproject.toml)
if [ "${#packages[@]}" -eq 0 ]; then
    echo "no AA-SI git dependencies found in pyproject.toml" >&2
    exit 1
fi

if [ "$pull" -eq 1 ]; then
    echo "== pulling AA-SI_Full_Pipeline_Example"
    git pull --ff-only || echo "warning: git pull failed, continuing with the current checkout" >&2
fi

if [ "$clean" -eq 1 ]; then
    echo "== clearing the poetry caches"
    rm -f poetry.lock
    while read -r cache; do
        [ -n "$cache" ] && poetry cache clear --all --no-interaction "$cache"
    done < <(poetry cache list --no-ansi)
    # Poetry keeps its clones of the git dependencies here.
    rm -rf "$(poetry config cache-dir)/src"

    echo "== recreating the virtualenv"
    poetry env remove --all || true

    echo "== installing everything"
    poetry install
else
    echo "== updating ${packages[*]}"
    poetry update "${packages[@]}"
fi

echo "== installed commits"
poetry run python show_dep_commits.py
