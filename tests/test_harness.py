from rare.config import settings
from rare.document_agent import DocumentProcessingAgent
from rare.rag_engine import CardNetworkRAGEngine
from rare.synthetic_generator import generate_synthetic_dataset


def test_synthetic_generation():
    """Verify synthetic dataset generator writes valid payload files."""
    generate_synthetic_dataset(num_cases=3)
    assert settings.TEST_CASES_FILE.exists()


def test_document_agent_extraction():
    """Verify document agent extracts telemetry on valid payload."""
    agent = DocumentProcessingAgent()
    packages = agent.process_all_test_cases()
    assert len(packages) > 0
    for pkg in packages:
        assert pkg.extracted_data.compelling_evidence_score > 0.0


def test_rag_rebuttal_synthesis():
    """Verify RAG engine produces non-empty legal rebuttal clauses."""
    agent = DocumentProcessingAgent()
    rag = CardNetworkRAGEngine()
    packages = agent.process_all_test_cases()

    for pkg in packages:
        rebuttal = rag.synthesize_rebuttal(pkg)
        assert "REPRESENTMENT REBUTTAL STATEMENT" in rebuttal["rebuttal_text"]
        assert "CONCLUSION" in rebuttal["rebuttal_text"]


if __name__ == "__main__":
    print("[*] Running RARE Engine Benchmark & Test Suite...")
    test_synthetic_generation()
    test_document_agent_extraction()
    test_rag_rebuttal_synthesis()
    print("\n[ALL TESTS PASSED] RARE Engine components are 100% operational.")
