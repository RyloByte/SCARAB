#!/usr/bin/env python3
"""Check built Python archives without importing scientific dependencies."""
import argparse
from pathlib import Path
import re
import tarfile
import zipfile


def check(directory):
    root = Path(__file__).resolve().parents[1]
    version = re.search(r'^version = "([^"]+)"', (root/'src/scarab/__init__.py').read_text(), re.M)[1]
    configs = {p.name for p in (root/'src/scarab/configs').glob('*.tsv')}
    wheels = list(directory.glob(f'scarab-{version}-*.whl'))
    sdists = list(directory.glob(f'scarab-{version}.tar.gz'))
    assert len(wheels) == len(sdists) == 1, 'Expected exactly one wheel and source archive for this version'
    for artifact in wheels + sdists:
        if artifact.suffix == '.whl':
            with zipfile.ZipFile(artifact) as archive:
                names = archive.namelist()
                entry = next(n for n in names if n.endswith('.dist-info/entry_points.txt'))
                assert 'scarab = scarab.__main__:main' in archive.read(entry).decode()
                metadata = next(n for n in names if n.endswith('.dist-info/METADATA'))
                assert f'Version: {version}\n' in archive.read(metadata).decode()
        else:
            with tarfile.open(artifact) as archive:
                names = archive.getnames()
        for name in names:
            assert not {'dev_utils', 'docs', 'tests', '__pycache__'} & set(Path(name).parts), name
            assert not name.lower().endswith(('.docx', '.pdf', '.svg', '.png', '.pyc')), name
        packaged = {Path(n).name for n in names if 'scarab/configs/' in n and n.endswith('.tsv')}
        assert packaged == configs and configs, 'Runtime parameter tables are incomplete'
        print(f'Validated {artifact.name}: {len(configs)} runtime parameter tables; no research directories')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    check(parser.parse_args().directory)
