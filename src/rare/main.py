import argparse
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from rare.document_agent import DocumentAgent
from rare.exporter import DefensePacketExporter
from rare.rag_engine import RAGEngine
from rare.synthetic_generator import generate_synthetic_dataset

app = FastAPI(title="RARE Engine API")


class DisputePayload(BaseModel):
    dispute_id: str
    transaction_id: str
    amount: float
    currency: str = "INR"
    reason_code: str
    network: str
    reason_description: str
    customer: Dict[str, Any]
    telemetry: Dict[str, Any]
    evidence_files: list[str] = []


@app.post("/api/v1/representment")
def process_representment(payload: DisputePayload):
    try:
        agent = DocumentAgent()
        pkg = agent.process_case(payload.model_dump())

        if not payload.evidence_files:
            return {
                "status": "rejected_insufficient_evidence",
                "dispute_id": payload.dispute_id,
                "message": (
                    "Mandatory evidence missing. "
                    "Representment blocked to prevent acquirer penalty fees."
                ),
                "required_actions": [
                    "Upload valid merchant invoice PDF",
                    "Provide 3DS authentication logs",
                ],
            }

        rag = RAGEngine()
        rebuttal = rag.generate_rebuttal(pkg.extracted_data)

        return {
            "status": "success",
            "dispute_id": payload.dispute_id,
            "rebuttal": rebuttal,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


def run_cli_pipeline(case_count: int = 5):
    print(f"Generating {case_count} synthetic dispute cases...")
    generate_synthetic_dataset(count=case_count)

    agent = DocumentAgent()
    packages = agent.process_all_test_cases()
    rag = RAGEngine()

    print(f"Processing {len(packages)} dispute packages through RAG & Exporter...")
    for pkg in packages:
        rebuttal_data = rag.generate_rebuttal(pkg.extracted_data)
        out_path = DefensePacketExporter.generate_pdf(
            output_path=rag.rebuttals_dir / f"{pkg.extracted_data.dispute_id}_defense.pdf",
            evidence=pkg.extracted_data,
            rebuttal_data=rebuttal_data,
        )
        print(f"Generated Defense Packet: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RARE Engine Runner")
    parser.add_argument(
        "--mode",
        type=str,
        default="cli",
        choices=["cli", "api"],
        help="Mode: 'cli' or 'api'",
    )
    parser.add_argument(
        "--cases",
        type=int,
        default=5,
        help="Number of cases for CLI pipeline",
    )
    args = parser.parse_args()

    if args.mode == "cli":
        run_cli_pipeline(case_count=args.cases)
    else:
        import uvicorn

        uvicorn.run("rare.main:app", host="127.0.0.1", port=8000, reload=True)
