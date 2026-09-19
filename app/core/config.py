from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    DB_USER:str
    DB_NAME:str
    DB_PASSWORD:str
    DB_HOST:str
    DB_PORT:str
    REDIS_HOST:str
    REDIS_PORT:str
    REDIS_DB:str
    SECRET_KEY:str
    ALGORITHM:str='HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES:int=30
    REFRESH_TOKEN_EXPIRE_DAYS:int=7
    SMTP_HOST:str
    SMTP_PORT:int
    SMTP_USER:str|None=None
    SMTP_PASSWORD:str|None=None
    SMTP_FROM:str
    testing:bool=False

    @property
    def sync_database_url(self) -> str:
        return(
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file= ".env"


settings=Settings()