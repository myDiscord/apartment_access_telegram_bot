from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr

    # Nested class with additional instructions for settings
    class Config:
        # The name of the file where the data will be read from
        # (relative to current working directory)
        env_file = '.env'
        # Readable file encoding
        env_file_encoding = 'utf-8'


config = Settings()
