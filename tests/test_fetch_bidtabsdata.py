import io
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.fetch_bidtabsdata as fetch


class DummyResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


def _make_zip_payload() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("BidTabsData-1.0.0/sample.txt", "hello")
    buffer.seek(0)
    return buffer.getvalue()


def test_main_downloads_and_marks(monkeypatch, tmp_path):
    payload = _make_zip_payload()

    def fake_urlopen(url: str):
        return DummyResponse(payload)

    out_dir = tmp_path / "BidTabsData"
    monkeypatch.setenv("BIDTABSDATA_VERSION", "v1.0.0")
    monkeypatch.setenv("BIDTABSDATA_OUT_DIR", str(out_dir))
    monkeypatch.setenv("BIDTABSDATA_REPO", "example/repo")
    monkeypatch.setattr(fetch, "urlopen", fake_urlopen)

    result = fetch.main()

    assert result == 0
    assert (out_dir / ".bidtabsdata_version").read_text(encoding="utf-8") == "v1.0.0"
    assert (out_dir / "sample.txt").read_text(encoding="utf-8") == "hello"

    # Idempotent when the version marker matches.
    second_result = fetch.main()
    assert second_result == 0
