from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from scalar_fastapi import get_scalar_api_reference
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware

from src.api.v1 import routers
from src.core.config import APP_DIR, TEMPLATE_DIR, security_settings
from src.database import redis as redis_helper
from src.exceptions import DomainError
from src.frontend_routers import router as web_router
from src.logs import logger
from src.middleware import SecurityHeaderMiddleware
from src.rate_limiting import limiter
from src.tags import APITags

description = """
Clean Arch Todo App

### Todo
- Create todo
- Track todo with status 

### User
- Register and Login Securely
- Email link Verification
- Users dashboard
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan hook.
    - Runs once when the app starts.
    - Guarantees that ``close_redis`` is awaited when the process stops.
    """
    try:
        # Force creation of the Redis client early so connection errors surface
        redis_helper.get_redis_client()
        logger.info("Application startup – Redis client ready")
        yield
    finally:
        # This block runs on shutdown
        await redis_helper.close_redis()
        logger.info("Application shutdown – Redis connections closed")


app = FastAPI(
    title="Todos API",
    description=description,
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    terms_of_service="https://todos.com/terms/",
    contact={
        "name": "Todo support",
        "url": "https://todos.com/support",
        "email": "support@todos.com",
    },
    openapi_tags=[
        {"name": APITags.AUTH, "description": "Operation related to authentication."},
        {"name": APITags.TODOS, "description": "Operation related to todos."},
        {"name": APITags.USERS, "description": "Operation related to users."},
    ],
)


@app.get("/api/v1")
async def home(request: Request):
    templates = Jinja2Templates(directory=TEMPLATE_DIR)
    return templates.TemplateResponse({"request": request}, name="login.html")


@app.get("/health")
async def health():
    # Try Redis ping if available (safe check)
    try:
        r = redis_helper.get_redis_client()
        await r.ping()  # async ping in your redis lib, adjust if sync
    except Exception:
        return JSONResponse(status_code=503, content={"detail": "Redis not available"})

    return JSONResponse(status_code=200, content={"detail": "OK"})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeaderMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=security_settings.SESSION_MIDDLEWARE_SECRET_KEY,
    https_only=True,
    same_site="lax",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Mount Static Files for CSS/JS
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with meaningful messages"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:])
        msg = error["msg"]
        errors.append({"field": field, "message": msg, "type": error["type"]})

    return JSONResponse(
        status_code=422, content={"detail": "Validation Error", "errors": errors}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please try again later."
        },
    )


app.include_router(web_router)
routers.register_routes(app)


@app.get("/docs", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Todo API",
    )
