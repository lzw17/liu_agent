"""Main application entry point for LiuAgent."""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.core import get_config, logger
from app.api import router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    config = get_config()
    
    app = FastAPI(
        title="LiuAgent - AI Competition Agent",
        description="智能AI助手，支持PDF知识库、聊天问答和网络搜索功能",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.server.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(router, prefix="/api")
    
    # Serve static files
    static_path = Path("static")
    if static_path.exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Serve frontend
    frontend_path = Path("frontend/dist")
    if frontend_path.exists():
        # Serve static assets
        app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
        
        # Serve other static files
        @app.get("/logo.svg")
        async def logo():
            from fastapi.responses import FileResponse
            return FileResponse("frontend/dist/logo.svg")
        
        # SPA index for root and any subpath (support GET/HEAD)
        from fastapi.responses import FileResponse

        async def spa_index():
            return FileResponse("frontend/dist/index.html")

        app.add_api_route("/", spa_index, methods=["GET", "HEAD"], response_class=HTMLResponse)
        app.add_api_route("/{full_path:path}", spa_index, methods=["GET", "HEAD"], response_class=HTMLResponse)
    else:
        # Fallback HTML page if frontend not built
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>LiuAgent - AI Competition Agent</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #2c3e50; text-align: center; }
                    .logo { text-align: center; margin: 20px 0; }
                    .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
                    .feature { padding: 20px; background: #ecf0f1; border-radius: 8px; text-align: center; }
                    .api-link { text-align: center; margin: 30px 0; }
                    .api-link a { background: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; }
                    .api-link a:hover { background: #2980b9; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="logo">
                        <h1>🎓 LiuAgent</h1>
                        <p>武昌工学院 AI 竞赛项目</p>
                    </div>
                    
                    <h2>功能特性</h2>
                    <div class="features">
                        <div class="feature">
                            <h3>📚 PDF知识库</h3>
                            <p>上传PDF文档，自动生成可搜索的知识库</p>
                        </div>
                        <div class="feature">
                            <h3>💬 智能聊天</h3>
                            <p>基于知识库内容的智能问答对话</p>
                        </div>
                        <div class="feature">
                            <h3>🔍 网络搜索</h3>
                            <p>实时网络搜索，获取最新信息</p>
                        </div>
                        <div class="feature">
                            <h3>🤖 多模型支持</h3>
                            <p>支持在线和本地大语言模型API</p>
                        </div>
                    </div>
                    
                    <div class="api-link">
                        <a href="/docs">查看 API 文档</a>
                        <a href="/redoc">API 参考</a>
                    </div>
                    
                    <h2>API 端点</h2>
                    <ul>
                        <li><strong>POST /api/chat</strong> - 聊天对话</li>
                        <li><strong>POST /api/upload-pdf</strong> - 上传PDF文档</li>
                        <li><strong>POST /api/search</strong> - 网络搜索</li>
                        <li><strong>GET /api/knowledge-base</strong> - 查看知识库</li>
                        <li><strong>GET /api/health</strong> - 健康检查</li>
                    </ul>
                    
                    <p style="text-align: center; margin-top: 40px; color: #7f8c8d;">
                        LiuAgent v1.0.0 - 为竞赛而生的智能AI助手
                    </p>
                </div>
            </body>
            </html>
            """
    
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return HTMLResponse(
            content="<h1>404 - Page Not Found</h1><p>The requested page was not found.</p>",
            status_code=404
        )
    
    return app


def main():
    """Main function to run the application."""
    try:
        config = get_config()
        
        logger.info("Starting LiuAgent server...")
        logger.info(f"Server will run on {config.server.host}:{config.server.port}")
        
        app = create_app()
        
        uvicorn.run(
            app,
            host=config.server.host,
            port=config.server.port,
            log_level="info" if not config.server.debug else "debug",
            reload=config.server.debug
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    main()
