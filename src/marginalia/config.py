from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MARGINALIA_", env_file=".env", extra="ignore")

    # The POSTGRES_* names are shared with docker-compose, so the credentials live in one place
    # (.env). No defaults for them: a missing password should fail at startup.
    postgres_user: str = Field(validation_alias="POSTGRES_USER")
    postgres_password: SecretStr = Field(validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(validation_alias="POSTGRES_DB")
    db_host: str = "localhost"
    db_port: int = 5434  # host port from docker-compose (5432/5433 are often taken)

    # all-MiniLM-L6-v2 produces 384-dim vectors; changing model means a new migration
    embedding_dim: int = 384
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 800  # max characters per chunk
    chunk_overlap: int = 100  # characters shared between consecutive chunks of a page
    max_upload_bytes: int = 20 * 1024 * 1024

    @property
    def database_url(self) -> URL:
        # URL.create escapes special characters in the password
        return URL.create(
            "postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.postgres_db,
        )


settings = Settings()
