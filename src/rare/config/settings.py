from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field
    @property
    def DATA_DIR(self) -> Path:
        return self.PROJECT_ROOT / "data"

    @computed_field
    @property
    def RULEBOOK_DIR(self) -> Path:
        return self.DATA_DIR / "rulebook"

    @computed_field
    @property
    def REBUTTALS_DIR(self) -> Path:
        return self.DATA_DIR / "rebuttals"

    @computed_field
    @property
    def SYNTHETIC_DOCS_DIR(self) -> Path:
        return self.DATA_DIR / "synthetic_docs"

    @computed_field
    @property
    def TEST_CASES_FILE(self) -> Path:
        return self.DATA_DIR / "test_cases.json"


settings = Settings()
