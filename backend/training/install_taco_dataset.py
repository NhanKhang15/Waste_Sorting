from __future__ import annotations

import argparse
import json
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT_DIR / "datasets" / "taco"
OFFICIAL_ANNOTATIONS_URL = "https://raw.githubusercontent.com/pedropro/TACO/master/data/annotations.json"
UNOFFICIAL_ANNOTATIONS_URL = "https://raw.githubusercontent.com/pedropro/TACO/master/data/annotations_unofficial.json"
ALL_IMAGE_URLS = "https://raw.githubusercontent.com/pedropro/TACO/master/data/all_image_urls.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install the TACO dataset into this project.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--limit", type=int, default=None, help="Only download the first N labeled images.")
    parser.add_argument(
        "--include-unofficial-metadata",
        action="store_true",
        help="Also download annotations_unofficial.json metadata file.",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Download annotations files only, skip image downloads.",
    )
    return parser.parse_args()


def download_bytes(session: requests.Session, url: str, timeout: int) -> bytes:
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    return response.content


def save_remote_file(session: requests.Session, url: str, destination: Path, timeout: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(download_bytes(session, url, timeout))


def load_annotations(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_image(content: bytes, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(BytesIO(content))
    if image.mode not in ("RGB", "RGBA", "L"):
        image = image.convert("RGB")

    save_kwargs = {}
    if "exif" in image.info:
        save_kwargs["exif"] = image.info["exif"]
    image.save(destination, **save_kwargs)


def install_taco(args: argparse.Namespace) -> dict:
    output_dir = args.output.resolve()
    metadata_dir = output_dir / "metadata"
    images_dir = output_dir / "images"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "testYolo-TACO-installer/1.0"})

    official_annotations_path = metadata_dir / "annotations.json"
    all_urls_path = metadata_dir / "all_image_urls.csv"

    print(f"Downloading official metadata to {metadata_dir}")
    save_remote_file(session, OFFICIAL_ANNOTATIONS_URL, official_annotations_path, args.timeout)
    save_remote_file(session, ALL_IMAGE_URLS, all_urls_path, args.timeout)

    unofficial_annotations_path = metadata_dir / "annotations_unofficial.json"
    if args.include_unofficial_metadata:
        save_remote_file(session, UNOFFICIAL_ANNOTATIONS_URL, unofficial_annotations_path, args.timeout)

    annotations = load_annotations(official_annotations_path)
    images = annotations.get("images", [])
    if args.limit is not None:
        images = images[: args.limit]

    report = {
        "annotations_file": str(official_annotations_path),
        "image_count_in_manifest": len(images),
        "downloaded": 0,
        "skipped_existing": 0,
        "failed": [],
    }

    if args.metadata_only:
        return report

    total = len(images)
    for index, image_meta in enumerate(images, start=1):
        relative_name = str(image_meta["file_name"]).replace("\\", "/")
        destination = images_dir / relative_name
        if destination.exists():
            report["skipped_existing"] += 1
            if index % 50 == 0 or index == total:
                print(f"Progress {index}/{total}: downloaded={report['downloaded']} skipped={report['skipped_existing']} failed={len(report['failed'])}")
            continue

        source_urls = [image_meta.get("flickr_url", ""), image_meta.get("flickr_640_url", "")]
        source_urls = [url for url in source_urls if url]
        last_error = ""

        for url in source_urls:
            try:
                content = download_bytes(session, url, args.timeout)
                save_image(content, destination)
                report["downloaded"] += 1
                last_error = ""
                break
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)

        if last_error:
            report["failed"].append({"file_name": relative_name, "error": last_error})

        if index % 50 == 0 or index == total:
            print(f"Progress {index}/{total}: downloaded={report['downloaded']} skipped={report['skipped_existing']} failed={len(report['failed'])}")

    return report


def main() -> None:
    args = parse_args()
    report = install_taco(args)

    report_path = args.output.resolve() / "install_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Install report saved to {report_path}")
    print(
        "Summary:",
        {
            "manifest_images": report["image_count_in_manifest"],
            "downloaded": report["downloaded"],
            "skipped_existing": report["skipped_existing"],
            "failed": len(report["failed"]),
        },
    )


if __name__ == "__main__":
    main()
