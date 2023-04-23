from pydantic import BaseSettings


class Config(BaseSettings):
    dbname: str
