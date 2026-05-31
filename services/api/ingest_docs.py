import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.dialog.vectorstore import ingest_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest documents (.pdf or .txt) into the vector store."
    )
    parser.add_argument("files", nargs="+", help="File paths to ingest")
    args = parser.parse_args()

    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"  skipping {file_path} — file not found", file=sys.stderr)
            continue
        print(f"  ingesting {path.name}...", end=" ", flush=True)
        try:
            n = ingest_file(str(path))
            print(f"done ({n} chunks)")
        except Exception as exc:
            print(f"failed: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
