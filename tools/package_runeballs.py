"""Build and verify the standalone player package."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
addon = ROOT / 'RaynnaRuneballs'
toc = addon / 'RaynnaRuneballs.toc'
version = next(line.split(': ', 1)[1] for line in toc.read_text().splitlines() if line.startswith('## Version:'))
files = [toc, addon / 'README.md', addon / 'ART-CREDITS.txt']
files += [addon / line for line in toc.read_text().splitlines() if line and not line.startswith('#')]
files += sorted((addon / 'Media').rglob('*.tga'))
files += sorted((addon / 'Media/Fonts').glob('*'))
files += [addon / 'CURSEFORGE.txt']
output = ROOT / 'dist' / ('RaynnaRuneballs-' + version + '.zip')
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in files:
        archive.write(path, path.relative_to(ROOT))
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    for path in files:
        assert archive.read(path.relative_to(ROOT).as_posix()) == path.read_bytes()
print(f'{output}: {len(files)} verified files')
