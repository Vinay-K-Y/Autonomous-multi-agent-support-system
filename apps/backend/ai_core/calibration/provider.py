from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.core.config import settings

from ai_core.calibration.models import CalibrationArtifact
from ai_core.calibration.store import load_calibration_artifact


class CalibratedThresholdProvider:
    """Supplies the escalation confidence threshold.

    Prefers a statistically calibrated value (see selective_risk.py) loaded
    from a calibration artifact on disk. Falls back to the static
    settings.ESCALATION_THRESHOLD when:
      - no artifact file exists (calibration has never been run), or
      - the artifact's own calibration run fell back (too little data, or
        no threshold satisfied the target risk bound)

    This means the app's behavior is unchanged from the pre-calibration
    baseline until someone deliberately runs the calibration pipeline
    against real labeled data and a valid artifact is produced.
    """

    def __init__(self, artifact_path: Optional[Path] = None):
        self._artifact_path = artifact_path
        self._artifact: Optional[CalibrationArtifact] = load_calibration_artifact(artifact_path)

    def reload(self) -> None:
        """Re-read the artifact from disk. Useful after running a new
        calibration pass without restarting the process."""
        self._artifact = load_calibration_artifact(self._artifact_path)

    def get_escalation_threshold(self) -> tuple[float, str]:
        artifact = self._artifact
        if artifact is not None and not artifact.fallback_used:
            source = (
                f"calibrated threshold (coverage={artifact.coverage:.2f}, "
                f"target_risk={artifact.target_risk:.2f}, "
                f"n={artifact.calibration_set_size}, "
                f"computed_at={artifact.computed_at})"
            )
            return artifact.threshold, source

        return settings.ESCALATION_THRESHOLD, "static config default (no valid calibration artifact)"


# Process-wide singleton, mirroring the WORKFLOW_RULES pattern already used
# in ai_core/workflow/rules.py. Tests should construct their own
# CalibratedThresholdProvider(artifact_path=...) rather than relying on
# this singleton, so they aren't affected by whatever artifact happens to
# be on disk.
calibrated_threshold_provider = CalibratedThresholdProvider()
