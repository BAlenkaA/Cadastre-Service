from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    title: str
    db_user: str
    db_password: str
    db_name: str
    db_port: int
    db_host: str

    @property
    def DATABASE_URL(self):
        return (f'postgresql+asyncpg://{settings.db_user}:'
                f'{settings.db_password}@{settings.db_host}:'
                f'{settings.db_port}/{settings.db_name}')

    model_config = ConfigDict(
        env_file='.env'
    )

settings = Settings()
