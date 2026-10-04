import json
from pathlib import Path
from typing import Any, Dict, Optional

from rare.config.settings import settings


class CardNetworkRAGEngine:
    """Rule-Augmented Generation Engine for chargeback rebuttal generation."""

    def __init__(
        self,
        rulebook_dir: Optional[Path] = None,
        rebuttals_dir: Optional[Path] = None,
    ):
        self.rulebook_dir = rulebook_dir or settings.RULEBOOK_DIR
        self.rebuttals_dir = rebuttals_dir or settings.REBUTTALS_DIR
        self.rulebook_dir.mkdir(parents=True, exist_ok=True)
        self.rebuttals_dir.mkdir(parents=True, exist_ok=True)
        self.rules_cache = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        rules_file = self.rulebook_dir / "rules.json"
        if not rules_file.exists():
            return {}
        with open(rules_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def lookup_rule(self, network: str, reason_code: str) -> Dict[str, Any]:
        key = f"{network.upper()}_{reason_code}"
        if key in self.rules_cache:
            return self.rules_cache[key]

        return {
            "network": network,
            "reason_code": reason_code,
            "title": "Unspecified Dispute",
            "governing_clause": "Standard Acquiring Network Guidelines",
            "compelling_evidence_required": [
                "Valid merchant transaction receipt and customer logs."
            ],
        }

    def generate_rebuttal(self, evidence: Any) -> Dict[str, Any]:
        rule_data = self.lookup_rule(evidence.network, evidence.reason_code)

        lines = [
            "REPRESENTMENT REBUTTAL STATEMENT",
            f"Transaction ID: {evidence.transaction_id} | Dispute ID: {evidence.dispute_id}",
            (
                f"Network & Reason Code: {evidence.network} "
                f"{evidence.reason_code} - {rule_data['title']}"
            ),
            f"Governing Standard: {rule_data['governing_clause']}",
            "",
            "EVIDENCE SUMMARY:",
        ]

        if evidence.telemetry.three_ds_status == "Y":
            lines.append(
                f"- [LIABILITY SHIFT]: Transaction was authenticated via "
                f"3D Secure (v{evidence.telemetry.three_ds_version}). Under "
                f"{evidence.network} rules, fraud liability shifts to issuer."
            )

        if evidence.telemetry.avs_match in ["Y", "X", "Z"]:
            lines.append(
                f"- [AVS MATCH]: Address Verification Service returned match code "
                f"'{evidence.telemetry.avs_match}', confirming cardholder billing identity."
            )

        lines.append(
            f"- [DEVICE TELEMETRY]: IP Address {evidence.customer.ip_address} "
            f"and Device Fingerprint ({evidence.telemetry.device_fingerprint[:12]}...) "
            "recorded at checkout."
        )

        lines.append("\nCONCLUSION:")
        lines.append(
            f"Based on compliance with {rule_data['governing_clause']}, merchant requests "
            f"immediate reversal of dispute {evidence.dispute_id} in the amount of "
            f"{evidence.currency} {evidence.amount:,.2f}."
        )

        statement = "\n".join(lines)
        return {
            "governing_clause": rule_data["governing_clause"],
            "rebuttal_statement": statement,
            "rebuttal_text": statement,
        }

    def synthesize_rebuttal(self, pkg: Any) -> Dict[str, Any]:
        evidence = getattr(pkg, "extracted_data", pkg)
        return self.generate_rebuttal(evidence)


# Alias for backward compatibility across other modules
RAGEngine = CardNetworkRAGEngine
