import os
from pydantic import BaseSettings



class Settings(BaseSettings):
    bscscan_api_key: str
    p2eguildadm_api_host: str
    p2eguildadm_api_port: str

    class Config:
        env_file = ".env"


settings = Settings()