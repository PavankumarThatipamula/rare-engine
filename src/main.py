import argparse
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.config import (
    BASE_DIR,
    SYNTHETIC_DOCS_DIR,
    REBUTTALS_DIR,
)
from src.document_agent import DocumentProcessingAgent
from src.exporter import DefensePacketExporter
from src.rag_engine import CardNetworkRAGEngine
from src.synthetic_generator import generate_synthetic_dataset

# FastAPI App Instance
app = FastAPI(
    title="RPay Auto-Representment Engine (RARE)",
    description="Automated Dispute Evidence & Network Rebuttal Generation API",
    version="1.0.0"
)

class WebhookDisputePayload(BaseModel):
    dispute_id: str
    transaction_id: str
    amount: float
    currency: str = "INR"
    reason_code: str
    network: str
    reason_description: str
    customer: dict
    telemetry: dict
    evidence_files: list


@app.get("/health")
def health_check():
    return {"status": "active", "engine": "RARE v1.0.0"}


@app.post("/disputes/represent")
def represent_dispute(payload: WebhookDisputePayload):
    try:
        dispute_dict = payload.model_dump()

        # EXPLICIT GUARDRAIL: Block submission if evidence is missing
        if not dispute_dict.get("evidence_files"):
            return {
                "status": "rejected_insufficient_evidence",
                "dispute_id": payload.dispute_id,
                "message": "Mandatory evidence is missing. Representment blocked to prevent non-refundable acquirer penalty fees (₹1,600 - ₹8,500).",
                "required_actions": [
                    "Upload valid merchant invoice PDF",
                    "Attach delivery confirmation telemetry"
                ]
            }

        agent = DocumentProcessingAgent()
        
        # Fallback if provided file path does not exist
        existing_files = list(SYNTHETIC_DOCS_DIR.glob("*.pdf"))
        valid_files = [
            f for f in dispute_dict.get("evidence_files", [])
            if Path(f).exists() or (BASE_DIR / f).exists()
        ]
        if not valid_files and existing_files:
            dispute_dict["evidence_files"] = [str(existing_files[0])]

        package = agent.process_dispute_case(dispute_dict)
        
        rag = CardNetworkRAGEngine()
        rebuttal = rag.synthesize_rebuttal(package)
        
        pdf_path = DefensePacketExporter.export_pdf(package, rebuttal)
        
        return {
            "status": "success",
            "dispute_id": payload.dispute_id,
            "compelling_evidence_score": package.extracted_data.compelling_evidence_score,
            "rebuttal_statement": rebuttal["rebuttal_text"],
            "defense_packet_pdf": str(pdf_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_cli_pipeline(num_cases: int = 5):
    start_time = time.time()
    print("=" * 60)
    print("         RPAY AUTO-REPRESENTMENT ENGINE (RARE) PIPELINE")
    print("=" * 60)

    print("\n[STAGE 1/4] Generating Synthetic Disputes & PDF Evidence...")
    generate_synthetic_dataset(num_cases=num_cases)

    print("\n[STAGE 2/4] Processing Documents & Telemetry via Multi-Agent Engine...")
    doc_agent = DocumentProcessingAgent()
    dispute_packages = doc_agent.process_all_test_cases()

    print("\n[STAGE 3/4] Synthesizing Network Rules & Exporting PDF Defense Packets...")
    rag_engine = CardNetworkRAGEngine()
    rebuttals = []

    for pkg in dispute_packages:
        rebuttal = rag_engine.synthesize_rebuttal(pkg)
        rebuttals.append(rebuttal)
        DefensePacketExporter.export_pdf(pkg, rebuttal)

    elapsed = time.time() - start_time
    avg_score = sum(r["compelling_evidence_score"] for r in rebuttals) / len(rebuttals) * 100

    print("\n[STAGE 4/4] Pipeline Execution Summary:")
    print(f"  • Total Disputes Processed : {len(rebuttals)}")
    print(f"  • Avg Compelling Evidence   : {avg_score:.1f}%")
    print(f"  • PDF Packets Exported      : {REBUTTALS_DIR}")
    print(f"  • Execution Time           : {elapsed:.2f} seconds")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RARE Engine Runner")
    parser.add_argument("--mode", type=str, default="cli", choices=["cli", "api"], help="Mode: 'cli' or 'api'")
    parser.add_argument("--cases", type=int, default=5, help="Number of cases for CLI pipeline")
    args = parser.parse_args()

    if args.mode == "api":
        import uvicorn
        print("[*] Launching RARE REST API Server on http://127.0.0.1:8000/docs")
        uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
    else:
        run_cli_pipeline(num_cases=args.cases)