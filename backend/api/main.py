"""
Main FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import structlog

from core.config import get_settings
from core.logging import setup_logging, get_logger
from core.cache import cache
from core.exceptions import NexusException
from anti_bot.proxy_manager import proxy_manager
from anti_bot.health_checker import health_checker
from filters.content_filter import content_filter

settings = get_settings()
logger = None  # Will be initialized after logging setup


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global logger
    
    # Startup
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info("Starting NEXUS Search", version="1.0.0")
    
    # Initialize cache
    await cache.connect()
    
    # Initialize proxy manager
    if settings.PROXY_ROTATION_ENABLED:
        await proxy_manager.initialize()
    
    # Start health checker
    await health_checker.start()
    
    # Initialize content filter
    content_filter.initialize()
    
    logger.info("Startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    
    await health_checker.stop()
    await cache.disconnect()
    await proxy_manager.disconnect()
    
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="Decentralized Privacy-First Search Engine with Web3",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2)
        )
        
        return response
    
    # Include routers
    from api.search import router as search_router
    from api.auth import router as auth_router
    from api.ipfs import router as ipfs_router
    from api.health import router as health_router
    
    app.include_router(search_router, prefix=settings.API_PREFIX)
    app.include_router(auth_router, prefix=settings.API_PREFIX)
    app.include_router(ipfs_router, prefix=settings.API_PREFIX)
    app.include_router(health_router, prefix=settings.API_PREFIX)
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": "1.0.0",
            "description": "Decentralized Privacy-First Search Engine with Web3",
            "docs": "/docs",
            "health": "/health"
        }
    
    # Exception handler
    @app.exception_handler(NexusException)
    async def nexus_exception_handler(request: Request, exc: NexusException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception", error=str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "status_code": 500
            }
        )
    
    return app


app = create_app()
