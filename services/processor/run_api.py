"""Entrypoint for running the processor API with uvicorn."""

import uvicorn

from processor.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "processor.api:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
