#!/usr/bin/env python3
"""Download BidTabsData releases into the local data-sample directory.

Environment variables:
    BIDTABSDATA_VERSION (required): Release tag to download.
    BIDTABSDATA_REPO (optional): GitHub repository owner/name.
        Defaults to "derek-betz/BidTabsData".
    BIDTABSDATA_OUT_DIR (optional): Target directory for extracted data.
        Defaults to "data-sample/BidTabsData" relative to the repo root.
"""

from __future__ import annotations

import os
import shutil
import stat
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

DEFAULT_REPO = "derek-betz/BidTabsData"
DEFAULT_OUT_DIR = "data-sample/BidTabsData"
ZIP_ASSET_NAME = "BidTabsData.zip"
REPO_ROOT = Path(__file__).resolve().parent.parent


def _require_version() -> str:
    version = os.getenv("BIDTABSDATA_VERSION")
    if not version:
        raise ValueError("BIDTABSDATA_VERSION environment variable is required.")
    return version


def _resolve_out_dir() -> Path:
    configured = os.getenv("BIDTABSDATA_OUT_DIR", DEFAULT_OUT_DIR)
    out_dir = Path(configured)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    return out_dir


def _download_zip(urls: list[str], destination: Path) -> str:
    last_error: Exception | None = None
    for url in urls:
        try:
            with urlopen(url) as response, open(destination, "wb") as target:
                shutil.copyfileobj(response, target)
            return url
        except (HTTPError, URLError) as exc:  # pragma: no cover - network dependent
            last_error = exc
    raise RuntimeError(
        f"Unable to download BidTabsData from {', '.join(urls)}; last error: {last_error}"
    )


def _safe_extract(zip_path: Path, destination: Path) -> None:
    destination = destination.resolve()
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            member_path = Path(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise ValueError(f"Unsafe path in zip file: {member.filename}")

            mode = member.external_attr >> 16
            if stat.S_IFMT(mode) == stat.S_IFLNK:
                raise ValueError(f"Symlinks are not allowed: {member.filename}")

            target_path = destination / member_path
            if member.is_dir():
                target_path.mkdir(parents=True, exist_ok=True)
                continue

            target_path.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as source, open(target_path, "wb") as target:
                shutil.copyfileobj(source, target)


def _locate_payload_root(extracted: Path) -> Path:
    entries = [path for path in extracted.iterdir() if path.name != "__MACOSX"]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return extracted


def main() -> int:
    try:
        version = _require_version()
        repo = os.getenv("BIDTABSDATA_REPO", DEFAULT_REPO)
        out_dir = _resolve_out_dir()
        marker_file = out_dir / ".bidtabsdata_version"

        if out_dir.exists() and marker_file.exists():
            try:
                current_version = marker_file.read_text(encoding="utf-8").strip()
            except OSError:
                current_version = None
            if current_version == version:
                print(f"BidTabsData version {version} already present at {out_dir}")
                return 0

        out_dir.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="bidtabsdata_", dir=out_dir.parent) as tmp:
            tmp_path = Path(tmp)
            download_target = tmp_path / "BidTabsData.zip"

            urls = [
                f"https://github.com/{repo}/releases/download/{version}/{ZIP_ASSET_NAME}",
                f"https://github.com/{repo}/archive/refs/tags/{version}.zip",
            ]
            source_url = _download_zip(urls, download_target)

            extracted_dir = tmp_path / "extracted"
            extracted_dir.mkdir()
            _safe_extract(download_target, extracted_dir)

            payload_root = _locate_payload_root(extracted_dir)
            ready_dir = tmp_path / "ready"
            shutil.copytree(payload_root, ready_dir)
            ready_marker = ready_dir / ".bidtabsdata_version"
            ready_marker.write_text(version, encoding="utf-8")

            backup_dir: Path | None = None
            try:
                if out_dir.exists():
                    backup_dir = out_dir.parent / f"{out_dir.name}.bak"
                    if backup_dir.exists():
                        shutil.rmtree(backup_dir)
                    os.replace(str(out_dir), str(backup_dir))
                os.replace(str(ready_dir), str(out_dir))
            except Exception:
                if backup_dir and backup_dir.exists():
                    if out_dir.exists():
                        shutil.rmtree(out_dir)
                    os.replace(str(backup_dir), str(out_dir))
                raise
            else:
                if backup_dir and backup_dir.exists():
                    shutil.rmtree(backup_dir)

        print(f"Fetched BidTabsData {version} from {source_url} into {out_dir}")
        return 0
    except Exception as exc:  # pragma: no cover - script entry point
        print(f"Failed to fetch BidTabsData: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    raise SystemExit(main())
