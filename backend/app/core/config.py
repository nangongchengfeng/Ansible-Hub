from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    APP_NAME: str = "Ansible Job Platform"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "mysql+asyncmy://root:123456@127.0.0.1:3306/ansible_db"

    # Redis配置
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # JWT配置
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Fernet加密（用于加密敏感数据）
    # 使用: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    FERNET_KEY: str = "naEdG_qFeaI_WZQcPRTOPK_7Z-tvXnZleClUfjvpTmw="

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
