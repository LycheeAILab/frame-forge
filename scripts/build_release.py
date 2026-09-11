"""Build a deterministic standalone skill archive from tracked files only."""
import hashlib
from pathlib import Path
import subprocess
import zipfile

root=Path(__file__).resolve().parents[1]
target=root/'dist';target.mkdir(exist_ok=True)
archive=target/'frame-forge-2.0.0.zip'
files=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as bundle:
    for name in sorted(filter(None,files)):
        if name.startswith(('.git','dist/')):continue
        info=zipfile.ZipInfo('frame-forge/'+name,(2026,9,11,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        bundle.writestr(info,(root/name).read_bytes())
(target/'SHA256SUMS').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n',encoding='utf-8')
print(archive)
