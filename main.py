"""Quick entry point for running the processor pipeline, API, or worker."""

import sys

from dialog.default_config import DEFAULT_CONFIG
from dialog.graph import CourseProcessorGraph


def run_api():
    """Start the FastAPI server."""
    import uvicorn

    uvicorn.run(
        "dialog.api:app",
        host=DEFAULT_CONFIG["api_host"],
        port=DEFAULT_CONFIG["api_port"],
        reload=True,
    )


def run_worker():
    """Start the background worker that processes jobs from Redis."""
    import logging
    import time

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("dialog.worker")
    logger.info("Worker started — waiting for jobs...")

    # Placeholder: poll Redis for jobs
    # Full implementation will come with the job queue integration
    try:
        while True:
            # TODO: pop job_id from Redis, load job from DB, run pipeline
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Worker shutting down.")


def run_gateway():
    """Start the LLM gateway proxy service."""
    import os
    import uvicorn

    port = int(os.environ.get("GATEWAY_PORT", "8100"))
    uvicorn.run(
        "dialog.gateway:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )


def run_pipeline(source_path: str):
    """Run the pipeline on a single file and print results."""
    graph = CourseProcessorGraph(config=DEFAULT_CONFIG, debug=True)
    result = graph.process(source_path)

    print(f"\n--- Results ---")
    print(f"Chunks: {len(result.get('knowledge_map', []))}")
    for chunk in result.get("knowledge_map", []):
        print(f"  [{chunk['chunk_id']}] {chunk['topic']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        run_api()
    elif len(sys.argv) > 1 and sys.argv[1] == "worker":
        run_worker()
    elif len(sys.argv) > 1 and sys.argv[1] == "gateway":
        run_gateway()
    elif len(sys.argv) > 1:
        run_pipeline(sys.argv[1])
    else:
        print("Usage:")
        print("  python main.py api              # Start the FastAPI server")
        print("  python main.py worker           # Start the background worker")
        print("  python main.py gateway           # Start the LLM gateway")
        print("  python main.py <file.pdf|txt>   # Process a single file")
