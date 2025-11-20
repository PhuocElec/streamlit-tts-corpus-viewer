from pathlib import Path
from typing import Optional

from settings import settings


def get_audio_bytes_local(filename: str) -> Optional[bytes]:
    filename = filename.strip()

    base_dir: Path = settings.AUDIO_BASE_DIR
    file_path = base_dir / filename

    if not file_path.exists():
        return None

    with open(file_path, "rb") as f:
        return f.read()


def get_audio_url(filename: str) -> str:
    filename = filename.strip()
    base = settings.AUDIO_BASE_URL.rstrip("/")
    return f"{base}/{filename.lstrip('/')}"
