import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import engine, Base, SessionLocal, ACTIVE_DB_TYPE
from app.auth import seed_demo_user_if_needed
from app.routers import tasks, ai, auth

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed demo user
    logger.info(f"[Startup] Initializing database tables with {ACTIVE_DB_TYPE}...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_user_if_needed(db)
        logger.info("[Startup] Database ready. Default demo user: admin / admin123")
    finally:
        db.close()
    yield
    # Shutdown
    logger.info("[Shutdown] Application terminating.")


app = FastAPI(
    title="Task Management AI API",
    description=(
        "Enterprise Task Management Backend built with FastAPI, MySQL/SQLite, and LLM AI Task Extraction. "
        "Compliant with Stage 1 and Stage 2 assessment requirements."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Friendly Validation Error Formatter
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        msg = err.get("msg", "Invalid input")
        # Clean pydantic prefix if present
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
        errors.append({
            "field": field,
            "message": msg,
            "type": err.get("type", "validation_error")
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation Failed",
            "errors": errors,
            "message": "; ".join(f"{e['field']}: {e['message']}" for e in errors)
        }
    )


# Root endpoint
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "healthy",
        "service": "Task Management AI API",
        "version": settings.VERSION,
        "database_type": ACTIVE_DB_TYPE,
        "docs_url": "/docs"
    }


# Include Routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(ai.router)
