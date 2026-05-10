"""PyPI version-check utilities.

Queries the PyPI JSON API (no third-party dependencies) and compares the
latest published version against the locally installed one.
"""

from __future__ import annotations

import importlib.metadata
import json
import urllib.error
import urllib.request
from typing import Optional

PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"
PACKAGE_NAME = "paint-tracker"


def _fetch_latest_pypi_version(package: str = PACKAGE_NAME) -> Optional[str]:
    """Return the latest version string from PyPI, or *None* on any error."""
    url = PYPI_JSON_URL.format(package=package)
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            return data["info"]["version"]
    except (urllib.error.URLError, KeyError, json.JSONDecodeError, OSError):
        return None


def _installed_version() -> str:
    try:
        return importlib.metadata.version(PACKAGE_NAME)
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"


def _version_tuple(ver: str) -> tuple[int, ...]:
    """Convert a version string like '1.2.3' to a comparable tuple."""
    try:
        return tuple(int(x) for x in ver.split(".")[:3])
    except ValueError:
        return (0, 0, 0)


def check_for_update() -> Optional[str]:
    """Return the newer version string if an update is available, else *None*.

    Returns *None* when offline or already up to date.
    """
    latest = _fetch_latest_pypi_version()
    if latest is None:
        return None
    current = _installed_version()
    if _version_tuple(latest) > _version_tuple(current):
        return latest
    return None
