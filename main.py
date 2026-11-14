#!/usr/bin/env python3
"""Write the ai-happy-01 v3 entry image to /output/entry.png.

Deterministic: copies assets/entry.png byte-for-byte (atomically, with a
sha256 check before and after the replace), so every run produces the
same bytes. Stdlib only, no network.
"""

import hashlib
import os
import shutil
import sys
import tempfile

ASSET = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "assets", "entry.png")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv):
    out = argv[1] if len(argv) > 1 else "/output/entry.png"
    if not os.path.isfile(ASSET):
        print(f"error: asset missing: {ASSET}", file=sys.stderr)
        return 1
    expected = sha256_of(ASSET)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(out)),
                               prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as dst:
            with open(ASSET, "rb") as src:
                shutil.copyfileobj(src, dst)
            dst.flush()
            os.fsync(dst.fileno())
        if sha256_of(tmp) != expected:
            print("error: temp copy failed sha256 check", file=sys.stderr)
            return 1
        os.replace(tmp, out)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    if sha256_of(out) != expected:
        print("error: output failed sha256 check", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
