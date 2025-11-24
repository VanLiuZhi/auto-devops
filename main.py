"""
Auto DevOps 应用启动入口
"""
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from config import settings
from src.demo.web_service import router as chat_router


def create_app() -> FastAPI:
    """
    创建FastAPI应用实例

    Returns:
        FastAPI: 配置好的应用实例
    """
    # 创建FastAPI应用
    app = FastAPI(**settings.app_config)

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 挂载静态文件
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # 注册路由
    app.include_router(chat_router)

    # 根路径返回前端页面
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def root():
        return FileResponse("static/index.html")

    return app


def main():
    """主函数：启动应用"""
    server_config = settings.server_config

    print("🚀 启动 Auto DevOps 服务...")
    print(f"📍 服务地址: http://{server_config['host']}:{server_config['port']}")
    print(f"🌐 前端页面: http://{server_config['host']}:{server_config['port']}/")
    print(f"📚 API文档: http://{server_config['host']}:{server_config['port']}{settings.DOCS_URL}")
    print(f"🏥 健康检查: http://{server_config['host']}:{server_config['port']}{settings.API_PREFIX}/health")

    if server_config.get("reload"):
        # 开发模式：使用import string方式启动以支持热重载
        uvicorn.run(
            "main:create_app",
            host=server_config["host"],
            port=server_config["port"],
            reload=True,
            log_level=server_config["log_level"],
            factory=True  # 指定使用工厂函数
        )
    else:
        # 生产模式：直接运行应用实例
        app = create_app()
        uvicorn.run(app, **{k: v for k, v in server_config.items() if k != "reload"})


if __name__ == "__main__":
    main()
