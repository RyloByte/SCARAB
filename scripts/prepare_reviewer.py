#!/usr/bin/env python3
"""Download, verify, and extract the public SCARAB demo (56 MiB)."""
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import urllib.request
import zipfile

URL = 'https://drive.usercontent.google.com/download?id=1yUoPpoNRl6-CZHkRoUYDbikBJk4yC-3V&export=download&confirm=t'
SHA256 = '1339ebbce24aef8633e4163174337d53b6e202d22e1e1bd5eb74abc300027175'


def prepare(output, archive=None):
    output = output.expanduser().resolve()
    if (output/'demo').exists():
        raise ValueError(f'{output}/demo already exists; choose a fresh destination')
    output.mkdir(parents=True, exist_ok=True)
    if archive is None:
        archive = output/'demo.zip'
        partial = output/'demo.zip.part'
        print('Downloading the public SCARAB demo...', flush=True)
        with urllib.request.urlopen(URL, timeout=120) as response, partial.open('wb') as handle:
            shutil.copyfileobj(response, handle)
        partial.replace(archive)
    with archive.open('rb') as handle:
        checksum = hashlib.file_digest(handle, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(handle.read()).hexdigest()
    if checksum != SHA256:
        raise ValueError(f'Demo checksum mismatch ({checksum}); archive was not extracted. Check the download link.')
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            path = PurePosixPath(member.filename)
            if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] != 'demo':
                raise ValueError(f'Unsafe archive member: {path}')
            if (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError(f'Archive symlink is not allowed: {path}')
        bundle.extractall(output)
    print(f'Verified and extracted: {output}/demo')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--archive', type=Path, help='Use an already downloaded demo.zip')
    args = parser.parse_args()
    prepare(args.output, args.archive)
