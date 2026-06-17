"""Quick entry point for running the processor pipeline or API."""

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


def run_pipeline(source_path: str):
    """Run the pipeline on a single file and print results."""
    graph = CourseProcessorGraph(config=DEFAULT_CONFIG, debug=True)
    result = graph.process(source_path)

    print(f"\n--- Results ---")
    print(f"Chunks:    {len(result.get('knowledge_map', []))}")
    print(f"Questions: {len(result.get('question_bank', []))}")
    print(f"Audit:     {result.get('review_status')}")
    if result.get("audit_flags"):
        for flag in result["audit_flags"]:
            print(f"  ⚠ [{flag['issue']}] {flag['detail']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        run_api()
    elif len(sys.argv) > 1:
        run_pipeline(sys.argv[1])
    else:
        print("Usage:")
        print("  python main.py api              # Start the FastAPI server")
        print("  python main.py <file.pdf|txt>   # Process a single file")
