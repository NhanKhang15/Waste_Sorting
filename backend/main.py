from app.main import app

__all__ = ["app"]


if __name__ == "__main__":
    import os

    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("WASTE_HOST", "127.0.0.1"),
        port=int(os.getenv("WASTE_PORT", "8000")),
        reload=os.getenv("WASTE_RELOAD", "false").lower() == "true",
    )
