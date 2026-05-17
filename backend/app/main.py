from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import init_db, close_db
from app.observability.tracing import setup_tracing
from app.observability.logging import logger
from app.middleware.interceptor import RequestInterceptor
from app.api import gateway, security, policies, admin, audit, threats, providers, metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    setup_tracing()
    await init_db()
    logger.info("Database initialized")
    yield
    await close_db()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Enterprise-grade AI security and governance platform for LLM applications",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

if settings.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(RequestInterceptor)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", "unknown")
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"trace_id": trace_id, "path": str(request.url)},
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "trace_id": trace_id,
        },
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "version": settings.version, "service": settings.app_name}


app.include_router(gateway.router)
app.include_router(security.router)
app.include_router(policies.router)
app.include_router(admin.router)
app.include_router(audit.router)
app.include_router(threats.router)
app.include_router(providers.router)
app.include_router(metrics.router)
