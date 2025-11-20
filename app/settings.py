from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    CORPUS_CSV_PATH: Path = Field(
        default=Path("data/corpus_metadata.csv"),
        description="Path to corpus metadata CSV",
    )

    AUDIO_MODE: str = Field(
        default="local",  # local | url
        description="Audio loading mode: 'local' or 'url'",
    )

    AUDIO_BASE_DIR: Path = Field(
        default=Path("data/sample_audio"),
        description="Base directory for local audio files",
    )

    AUDIO_BASE_URL: str = Field(
        default="",
        description="Base URL for audio files when using URL mode",
    )

    ADMIN_USERNAME: str = Field(
        default="",
        description="Admin username for upload panel",
    )

    ADMIN_PASSWORD: str = Field(
        default="",
        description="Admin password for upload panel",
    )

    DEFAULT_MAX_ROWS: int = Field(
        default=100,
        description="Default max rows to display in viewer",
    )


settings = Settings()
