from __future__ import annotations

from pathlib import Path
from typing import Optional

from ai_core.calibration.models import CalibrationArtifact, CalibrationExample

DATA_DIR = Path(__file__).parent / "data"

# Where a real calibration run writes its output. Intentionally NOT shipped
# with a file at this path by default — its absence means
# CalibratedThresholdProvider falls back to the static ESCALATION_THRESHOLD
# config value, so existing behavior is unchanged until someone actually
# runs the calibration pipeline against real labeled data.
DEFAULT_ARTIFACT_PATH = DATA_DIR / "calibrated_thresholds.json"

DEFAULT_EXAMPLES_PATH = DATA_DIR / "calibration_examples.jsonl"


def load_calibration_examples(path: Optional[Path] = None) -> list[CalibrationExample]:
    path = path or DEFAULT_EXAMPLES_PATH
    if not path.exists():
        return []

    examples: list[CalibrationExample] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            examples.append(CalibrationExample.model_validate_json(line))
    return examples


def save_calibration_examples(
    examples: list[CalibrationExample], path: Optional[Path] = None
) -> None:
    path = path or DEFAULT_EXAMPLES_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for example in examples:
            f.write(example.model_dump_json() + "\n")


def save_calibration_artifact(
    artifact: CalibrationArtifact, path: Optional[Path] = None
) -> None:
    path = path or DEFAULT_ARTIFACT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(artifact.model_dump_json(indent=2))


def load_calibration_artifact(path: Optional[Path] = None) -> Optional[CalibrationArtifact]:
    path = path or DEFAULT_ARTIFACT_PATH
    if not path.exists():
        return None
    try:
        return CalibrationArtifact.model_validate_json(path.read_text())
    except Exception:
        # A corrupt or partially-written artifact should never take down
        # the app — fail safe by acting as if no artifact exists, which
        # means DecisionEngine falls back to the static config threshold.
        return None
