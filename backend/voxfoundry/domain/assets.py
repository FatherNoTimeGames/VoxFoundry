import re
from pathlib import PureWindowsPath

from voxfoundry.domain.errors import DomainError

MAX_ASSET_BYTES = 25 * 1024 * 1024


def validate_filename(name: str) -> str:
    """Reject platform-ambiguous names; names never become object-store paths."""
    reserved = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    if (
        not name
        or len(name) > 180
        or name in (".", "..")
        or name[-1:] in (" ", ".")
        or re.search(r'[<>:"/\\|?*\x00-\x1f\x7f]', name)
        or PureWindowsPath(name).is_reserved()
        or name.split(".")[0].upper() in reserved
    ):
        raise DomainError("Use a plain filename without paths or reserved Windows characters")
    return name
