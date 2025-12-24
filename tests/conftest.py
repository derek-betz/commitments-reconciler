from __future__ import annotations

from pathlib import Path

import pytest

from commitments_reconciler.factories import (
    create_sample_commitments_workbook,
    create_sample_environment_doc,
)


@pytest.fixture()
def commitments_workbook(tmp_path: Path) -> Path:
    destination = tmp_path / "sample_commitments.xlsx"
    return create_sample_commitments_workbook(destination)


@pytest.fixture()
def environment_doc(tmp_path: Path) -> Path:
    destination = tmp_path / "sample_env_doc.docx"
    return create_sample_environment_doc(destination)
