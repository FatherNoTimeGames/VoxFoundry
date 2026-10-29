import json
import os
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_config_path, user_data_path


@dataclass(frozen=True)
class Settings:
    library: Path
    port: int = 8765
    frontend: Path = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def load_settings(library: str | None = None, port: int = 8765) -> Settings:
    config = user_config_path("VoxFoundry", appauthor=False) / "config.json"
    configured = None
    if config.exists():
        data = json.loads(config.read_text(encoding="utf-8"))
        configured = data.get("library")
        if configured is not None and not isinstance(configured, str):
            raise ValueError("config.json library must be an absolute path")
    selected = library or os.environ.get("VOXFOUNDRY_LIBRARY") or configured
    path = (
        Path(selected).expanduser()
        if selected
        else user_data_path("VoxFoundry", appauthor=False) / "Library"
    )
    if not path.is_absolute():
        raise ValueError("Library path must be absolute")
    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535")
    checkout = Path(__file__).resolve().parents[2]
    resolved = path.resolve()
    if resolved == checkout or checkout in resolved.parents:
        raise ValueError("Keep the library outside the application installation/checkout")
    return Settings(resolved, port)
