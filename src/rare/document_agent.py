import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from rare.config.settings import settings


class CustomerInfo(BaseModel):
    name: str
    email: str
    ip_address: str
    shipping_address: str


class TelemetryInfo(BaseModel):
    avs_match: str
    three_ds_version: str
    three_ds_status: str
    device_fingerprint: str


class ExtractedDispute(BaseModel):
    dispute_id: str
    transaction_id: str
    amount: float
    currency: str
    reason_code: str
    network: str
    reason_description: str
    customer: CustomerInfo
    telemetry: TelemetryInfo
    evidence_files: List[str]
    compelling_evidence_score: float = 1.0


class DisputePackage(BaseModel):
    extracted_data: ExtractedDispute
    summary_notes: List[str]


class DocumentProcessingAgent:
    """Parses raw dispute cases and extracts structured telemetry data."""

    def process_case(self, raw_case: Dict[str, Any]) -> DisputePackage:
        case_data = dict(raw_case)
        if "compelling_evidence_score" not in case_data:
            score = 0.5
            telemetry = case_data.get("telemetry", {})
            if telemetry.get("three_ds_status") == "Y":
                score += 0.3
            if telemetry.get("avs_match") in ["Y", "X", "Z"]:
                score += 0.2
            case_data["compelling_evidence_score"] = min(1.0, score)

        extracted = ExtractedDispute(**case_data)
        summary = []

        telemetry = extracted.telemetry
        is_3ds = telemetry.three_ds_status == "Y"
        if is_3ds:
            summary.append(
                f"3DS v{telemetry.three_ds_version} authenticated successfully "
                "(Liability shift eligible)."
            )
        else:
            summary.append("Warning: 3DS authentication unverified.")

        if telemetry.avs_match in ["Y", "X", "Z"]:
            summary.append(f"AVS match successful (Code: {telemetry.avs_match}).")
        else:
            summary.append(f"AVS match warning (Code: {telemetry.avs_match}).")

        return DisputePackage(extracted_data=extracted, summary_notes=summary)

    def process_all_test_cases(
        self,
        test_cases_path: Optional[Path] = None,
    ) -> List[DisputePackage]:
        """Loads test cases file and parses all disputes."""
        target_path = test_cases_path or settings.TEST_CASES_FILE
        if not target_path.exists():
            return []

        with open(target_path, "r", encoding="utf-8") as f:
            cases_data = json.load(f)

        return [self.process_case(c) for c in cases_data]


# Alias for backward compatibility across modules
DocumentAgent = DocumentProcessingAgent
