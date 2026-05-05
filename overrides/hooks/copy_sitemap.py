"""Drop a copy of sitemap.xml/sitemap.xml.gz into every page directory.

Material's instant nav fetches `sitemap.xml` as a path relative to the
current page (e.g. `/sdk/sitemap.xml`), which 404s by default since the
sitemap is only generated at the site root. This hook copies the root
sitemap into every directory that contains an index.html so those
relative requests resolve.
"""

from __future__ import annotations

import os
import shutil


def on_post_build(config, **_) -> None:
    site_dir: str = config["site_dir"]
    sources = [
        os.path.join(site_dir, "sitemap.xml"),
        os.path.join(site_dir, "sitemap.xml.gz"),
    ]
    sources = [s for s in sources if os.path.exists(s)]
    if not sources:
        return

    for root, _dirs, files in os.walk(site_dir):
        if root == site_dir:
            continue
        if "index.html" not in files:
            continue
        for src in sources:
            dst = os.path.join(root, os.path.basename(src))
            if os.path.exists(dst):
                continue
            shutil.copy2(src, dst)
