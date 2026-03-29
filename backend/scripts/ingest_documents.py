#!/usr/bin/env python3
"""
Ingestion script — runs the full pipeline for CV or job-description files.

Usage examples:
  # Ingest a single CV
  python ingest_documents.py --file ../../data_hellio_hr/cvs/cv_001.pdf --type cv

  # Ingest all CVs in a directory
  python ingest_documents.py --dir ../../data_hellio_hr/cvs --type cv

  # Ingest all job descriptions
  python ingest_documents.py --dir ../../data_hellio_hr/jobs --type job

  # Ingest everything from default data dirs
  python ingest_documents.py --all

  # Use Anthropic instead of Bedrock
  python ingest_documents.py --file cv_001.pdf --type cv --provider anthropic

Run from backend/ directory or ensure PYTHONPATH includes the backend root.
"""
import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.document_ingestion import IngestionStatus
from app.services.ingestion.pipeline import run_ingestion
from app.services.ingestion.providers import build_provider

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ingest")

# Default data directories relative to the repo root
_REPO_ROOT = Path(__file__).parent.parent.parent.parent
_DEFAULT_CV_DIR = _REPO_ROOT / "data_hellio_hr" / "cvs"
_DEFAULT_JOB_DIR = _REPO_ROOT / "data_hellio_hr" / "jobs"

_CV_EXTENSIONS = {".pdf", ".docx", ".doc"}
_JOB_EXTENSIONS = {".txt", ".text", ""}


def _collect_files(directory: Path, doc_type: str) -> list[Path]:
    extensions = _CV_EXTENSIONS if doc_type == "cv" else _JOB_EXTENSIONS
    files = sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in extensions
    )
    return files


async def ingest_files(
    files: list[tuple[Path, str]],  # (path, document_type)
    provider_name: str,
    model: str,
) -> None:
    provider = build_provider(
        provider_name=provider_name,
        model=model,
        region=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        aws_bearer_token=settings.AWS_BEARER_TOKEN_BEDROCK,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
    )

    results: list[dict] = []

    for path, doc_type in files:
        print(f"\n{'─' * 60}")
        print(f"  File : {path.name}")
        print(f"  Type : {doc_type}")
        print(f"  Model: {provider.provider_name} / {provider.model_name}")

        async with AsyncSessionLocal() as session:
            ingestion = await run_ingestion(
                session=session,
                path=path,
                provider=provider,
                document_type=doc_type,
            )

        status_icon = "✓" if ingestion.status == IngestionStatus.COMPLETED else "✗"
        print(f"  {status_icon} Status : {ingestion.status.value}")
        if ingestion.candidate_id:
            print(f"  → Candidate ID : {ingestion.candidate_id}")
        if ingestion.position_id:
            print(f"  → Position  ID : {ingestion.position_id}")
        if ingestion.error_message:
            print(f"  ERROR: {ingestion.error_message}")

        results.append({
            "file": path.name,
            "status": ingestion.status.value,
            "error": ingestion.error_message,
        })

    # Summary
    print(f"\n{'=' * 60}")
    completed = sum(1 for r in results if r["status"] == "completed")
    failed = sum(1 for r in results if r["status"] == "failed")
    print(f"  Total : {len(results)}  |  Completed : {completed}  |  Failed : {failed}")
    if failed:
        print("\n  Failed files:")
        for r in results:
            if r["status"] == "failed":
                print(f"    {r['file']}: {r['error']}")
    print(f"{'=' * 60}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest CV and job-description files into the Hellio HR database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", type=Path, metavar="PATH", help="Single file to ingest")
    source.add_argument("--dir", type=Path, metavar="DIR", help="Directory of files to ingest")
    source.add_argument("--all", action="store_true", help="Ingest all default data directories")

    parser.add_argument(
        "--type",
        choices=["cv", "job"],
        help="Document type (required unless --all)",
    )
    parser.add_argument(
        "--provider",
        default=None,
        help=f"LLM provider (default: {settings.INGESTION_PROVIDER})",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=f"LLM model name (default: {settings.INGESTION_MODEL})",
    )

    args = parser.parse_args()

    provider_name = args.provider or settings.INGESTION_PROVIDER
    model = args.model or settings.INGESTION_MODEL

    files: list[tuple[Path, str]] = []

    if args.all:
        for cv_path in _collect_files(_DEFAULT_CV_DIR, "cv"):
            files.append((cv_path, "cv"))
        for job_path in _collect_files(_DEFAULT_JOB_DIR, "job"):
            files.append((job_path, "job_description"))
    elif args.dir:
        if not args.type:
            parser.error("--type is required when using --dir")
        doc_type = "job_description" if args.type == "job" else "cv"
        for p in _collect_files(args.dir, args.type):
            files.append((p, doc_type))
    else:  # --file
        if not args.type:
            parser.error("--type is required when using --file")
        doc_type = "job_description" if args.type == "job" else "cv"
        if not args.file.exists():
            print(f"ERROR: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        files.append((args.file, doc_type))

    if not files:
        print("No files found to ingest.")
        sys.exit(0)

    print(f"\nHellio HR — Document Ingestion")
    print(f"Provider : {provider_name} / {model}")
    print(f"Files    : {len(files)}")

    asyncio.run(ingest_files(files, provider_name, model))


if __name__ == "__main__":
    main()
