import importlib.metadata as im, json, os, subprocess
from urllib.parse import urlparse
for dist in sorted(im.distributions(), key=lambda d: (d.metadata['Name'] or '').lower()):
    name = dist.metadata['Name'] or '?'
    raw = dist.read_text('direct_url.json')
    if not raw:
        continue                      # from PyPI/wheel — no VCS info
    du = json.loads(raw)
    if 'vcs_info' in du:              # installed from git
        print(f"{name:26} git   {du['vcs_info'].get('commit_id')}  {du.get('url')}")
    else:                            # installed from a local directory
        path = urlparse(du.get('url','')).path
        if os.name == 'nt' and path.startswith('/'): path = path[1:]
        editable = du.get('dir_info', {}).get('editable', False)
        try:
            head = subprocess.check_output(['git','-C',path,'rev-parse','--short','HEAD'], text=True).strip()
        except Exception:
            head = '??'
        print(f"{name:26} dir   {head}  editable={editable}  {path}")


# NOTE: if any commits are stale, run ./update_aa_deps.sh (--clean wipes poetry.lock and the caches first)