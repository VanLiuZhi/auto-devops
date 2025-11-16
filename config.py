"""
应用配置文件
"""
import os
from typing import Optional


class Settings:
    """应用配置类"""

    # 应用基础配置
    APP_NAME: str = "Auto DevOps API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "自动化运维服务 - 故障诊断AI助手"

    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8002))

    # 开发环境配置
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"

    # API配置
    API_PREFIX: str = "/api"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

    # CORS配置
    CORS_ORIGINS: list = ["*"]  # 生产环境应该限制具体域名

    # 诊断服务配置
    DIAGNOSIS_VERBOSE: bool = False

    @property
    def app_config(self) -> dict:
        """获取FastAPI应用配置"""
        return {
            "title": self.APP_NAME,
            "description": self.APP_DESCRIPTION,
            "version": self.APP_VERSION,
            "docs_url": self.DOCS_URL,
            "redoc_url": self.REDOC_URL
        }

    @property
    def server_config(self) -> dict:
        """获取服务器启动配置"""
        return {
            "host": self.HOST,
            "port": self.PORT,
            "reload": self.RELOAD,
            "log_level": "info" if self.DEBUG else "warning"
        }


# 全局配置实例
settings = Settings()