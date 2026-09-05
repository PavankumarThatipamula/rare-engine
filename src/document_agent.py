import json
import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

# Base Directory Setup
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Pydantic Data Models ---

class TelemetryData(BaseModel):
    avs_match: str
    three_ds_version: str
    three_ds_status: str
    device_fingerprint: str

class CustomerInfo(BaseModel):
    name: str
    email: str
    ip_address: str
    shipping_address: str

class ExtractedEvidence(BaseModel):
    transaction_id: str
    dispute_id: str
    amount: float
    currency: str
    reason_code: str
    network: str
    reason_description: str
    customer: CustomerInfo
    telemetry: TelemetryData
    invoice_path: str
    is_3ds_authenticated: bool = False
    avs_verified: bool = False
    compelling_evidence_score: float = 0.0

class DisputePackage(BaseModel):
    extracted_data: ExtractedEvidence
    summary_notes: List[str]

# --- Processing Agent ---

class DocumentProcessingAgent:
    """Multi-Agent Document Processing Engine for Dispute Telemetry & Invoices."""

    def __init__(self):
        pass

    def parse_invoice_metadata(self, invoice_relative_path: str) -> dict:
        """Parses evidence PDF file path and checks existence."""
        full_path = BASE_DIR / invoice_relative_path
        exists = full_path.exists()
        return {
            "path": str(full_path),
            "exists": exists
        }

    def process_dispute_case(self, case_raw: dict) -> DisputePackage:
        """Ingests raw case payload, validates telemetry, and constructs evidence package."""
        
        # Parse nested models using Pydantic validation
        customer = CustomerInfo(**case_raw["customer"])
        telemetry = TelemetryData(**case_raw["telemetry"])
        
        invoice_info = self.parse_invoice_metadata(case_raw["evidence_files"][0])
        
        # Rule-based validation rules
        is_3ds = telemetry.three_ds_status == "Y" and telemetry.three_ds_version.startswith("2.")
        is_avs = telemetry.avs_match in ["Y", "Z", "X"]
        
        # Calculate initial compelling evidence score (0.0 to 1.0)
        score = 0.0
        if is_3ds:
            score += 0.5  # Strong liability shift for 3DS v2+
        if is_avs:
            score += 0.3  # Billing verification match
        if invoice_info["exists"]:
            score += 0.2  # Proof of purchase attached
            
        summary = []
        if is_3ds:
            summary.append(f"3DS v{telemetry.three_ds_version} authenticated successfully (Liability shift eligible).")
        else:
            summary.append("Warning: 3DS authentication unverified.")

        if is_avs:
            summary.append(f"AVS match confirmed (Code: {telemetry.avs_match}).")
            
        if invoice_info["exists"]:
            summary.append("Itemized merchant invoice verified & attached.")

        extracted = ExtractedEvidence(
            transaction_id=case_raw["transaction_id"],
            dispute_id=case_raw["dispute_id"],
            amount=case_raw["amount"],
            currency=case_raw["currency"],
            reason_code=case_raw["reason_code"],
            network=case_raw["network"],
            reason_description=case_raw["reason_description"],
            customer=customer,
            telemetry=telemetry,
            invoice_path=invoice_info["path"],
            is_3ds_authenticated=is_3ds,
            avs_verified=is_avs,
            compelling_evidence_score=round(score, 2)
        )

        return DisputePackage(extracted_data=extracted, summary_notes=summary)

    def process_all_test_cases(self, test_cases_path: Path = BASE_DIR / "data" / "test_cases.json") -> List[DisputePackage]:
        """Loads data/test_cases.json and parses all disputes."""
        if not test_cases_path.exists():
            raise FileNotFoundError(f"Test cases file not found at {test_cases_path}")

        with open(test_cases_path, "r", encoding="utf-8") as f:
            cases = json.load(f)

        packages = []
        for case in cases:
            package = self.process_dispute_case(case)
            packages.append(package)

        return packages

if __name__ == "__main__":
    agent = DocumentProcessingAgent()
    results = agent.process_all_test_cases()
    print(f"[✓] Multi-Agent Extracted {len(results)} Dispute Evidence Packages.")
    for idx, pkg in enumerate(results, 1):
        ext = pkg.extracted_data
        print(f"  [{idx}] Dispute: {ext.dispute_id} | Network: {ext.network} ({ext.reason_code}) | Score: {ext.compelling_evidence_score * 100}%")