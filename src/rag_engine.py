import json
from pathlib import Path
from typing import Dict, Any, List
from src.document_agent import DisputePackage, ExtractedEvidence

BASE_DIR = Path(__file__).resolve().parent.parent

# Mock Knowledge Base of Card Network Rulebooks
CARD_NETWORK_RULEBOOK = {
    "10.4": {
        "network": "Visa",
        "title": "Other Fraud - Card-Absent Environment",
        "compelling_evidence_required": [
            "Proof of 3DS v2.x authentication yielding liability shift.",
            "AVS match response code (Y, Z, or X).",
            "IP address and device fingerprint matched to past legitimate transactions."
        ],
        "governing_clause": "Visa Core Rules & Visa Product and Service Rules (VCR Section 10.4)"
    },
    "13.1": {
        "network": "Visa",
        "title": "Merchandise/Services Not Received",
        "compelling_evidence_required": [
            "Itemized invoice with customer identifier.",
            "Proof of digital fulfillment or physical delivery confirmation."
        ],
        "governing_clause": "Visa Core Rules (VCR Section 13.1 - Compelling Evidence 3.0)"
    },
    "4837": {
        "network": "Mastercard",
        "title": "No Cardholder Authorization",
        "compelling_evidence_required": [
            "EMV 3-D Secure authentication data proving authorization.",
            "AVS verification payload match."
        ],
        "governing_clause": "Mastercard Chargeback Guide (Section 3.14 - Rule 4837)"
    },
    "4853": {
        "network": "Mastercard",
        "title": "Defective or Not as Described",
        "compelling_evidence_required": [
            "Merchant terms of service acceptance log.",
            "Itemized invoice detailing delivered specifications matching description."
        ],
        "governing_clause": "Mastercard Chargeback Guide (Section 3.18 - Rule 4853)"
    }
}


class CardNetworkRAGEngine:
    """RAG Core for Retrieving Card Rules & Synthesizing Legal Dispute Rebuttals."""

    def __init__(self):
        self.rules = CARD_NETWORK_RULEBOOK

    def retrieve_network_rules(self, reason_code: str) -> Dict[str, Any]:
        """Retrieves targeted network rules matching the specific dispute reason code."""
        return self.rules.get(
            reason_code,
            {
                "network": "Generic",
                "title": "Unspecified Dispute",
                "compelling_evidence_required": ["Valid merchant transaction receipt and customer logs."],
                "governing_clause": "Standard Acquiring Network Guidelines"
            }
        )

    def synthesize_rebuttal(self, dispute_package: DisputePackage) -> Dict[str, Any]:
        """Synthesizes formal Representment Argument based on rules + extracted evidence."""
        evidence: ExtractedEvidence = dispute_package.extracted_data
        rule_data = self.retrieve_network_rules(evidence.reason_code)

        # Generate automated legal rebuttal statement
        rebuttal_lines = [
            f"REPRESENTMENT REBUTTAL STATEMENT",
            f"Transaction ID: {evidence.transaction_id} | Dispute ID: {evidence.dispute_id}",
            f"Network & Reason Code: {evidence.network} {evidence.reason_code} - {rule_data['title']}",
            f"Governing Standard: {rule_data['governing_clause']}",
            "",
            "DEFENSE ARGUMENTS & COMPLIANCE PROOF:"
        ]

        if evidence.is_3ds_authenticated:
            rebuttal_lines.append(
                f"- [LIABILITY SHIFT]: Transaction was authenticated via 3D Secure (v{evidence.telemetry.three_ds_version}). "
                f"Under {evidence.network} rules, fraud liability shifts from merchant to issuer."
            )

        if evidence.avs_verified:
            rebuttal_lines.append(
                f"- [AVS MATCH]: Address Verification Service returned match code '{evidence.telemetry.avs_match}', "
                f"confirming cardholder billing identity."
            )

        rebuttal_lines.append(
            f"- [DEVICE TELEMETRY]: IP Address {evidence.customer.ip_address} and Device Fingerprint "
            f"({evidence.telemetry.device_fingerprint[:12]}...) recorded at checkout."
        )

        rebuttal_lines.append(
            f"- [DOCUMENTATION ATTACHED]: Itemized invoice verified at '{evidence.invoice_path}'."
        )

        rebuttal_lines.append("\nCONCLUSION:")
        rebuttal_lines.append(
            f"Based on compliance with {rule_data['governing_clause']}, merchant requests immediate reversal "
            f"of dispute {evidence.dispute_id} in the amount of {evidence.currency} {evidence.amount:,.2f}."
        )

        full_rebuttal = "\n".join(rebuttal_lines)

        return {
            "dispute_id": evidence.dispute_id,
            "governing_clause": rule_data["governing_clause"],
            "compelling_evidence_score": evidence.compelling_evidence_score,
            "rebuttal_text": full_rebuttal
        }


if __name__ == "__main__":
    from src.document_agent import DocumentProcessingAgent
    
    agent = DocumentProcessingAgent()
    rag = CardNetworkRAGEngine()
    
    packages = agent.process_all_test_cases()
    print(f"[*] Executing RAG Synthesizer for {len(packages)} packages...\n")
    
    for i, pkg in enumerate(packages[:2], 1):
        result = rag.synthesize_rebuttal(pkg)
        print(f"=== REBUTTAL PACKET #{i} ({result['dispute_id']}) ===")
        print(result["rebuttal_text"])
        print("=" * 55 + "\n")