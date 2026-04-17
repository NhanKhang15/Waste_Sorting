from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.deps import get_detector, get_settings
from app.api.router import api_router
from app.core.errors import InferenceError, InvalidImageError, ModelNotConfiguredError


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    if settings.yolov26_preload_on_startup:
        detector = get_detector()
        detector.preload()
    yield



def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    if settings.cors_origin_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origin_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app



def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidImageError)
    async def handle_invalid_image(_: Request, exc: InvalidImageError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(ModelNotConfiguredError)
    async def handle_missing_model(_: Request, exc: ModelNotConfiguredError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(InferenceError)
    async def handle_inference_error(_: Request, exc: InferenceError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": str(exc)})


app = create_application()
