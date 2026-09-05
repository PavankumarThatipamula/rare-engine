# RPay Auto Representment Engine (RARE)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> An automated dispute representment and defense packet generation engine tailored for modern payment gateways.

RARE (**RPay Auto Representment Engine**) automates the process of analyzing payment disputes, extracting transaction evidence, matching evidence against card network dispute rules, and generating structured defense packets for representment workflows.

---

## Table of Contents

- [Overview](#overview)
- [Core Features](#core-features)
- [Requirements & Installation](#requirements--installation)
- [Quickstart & Usage](#quickstart--usage)
  - [CLI Pipeline](#cli-pipeline)
  - [Webhook & REST API](#webhook--rest-api)
- [Technical Architecture](#technical-architecture)
- [Project Structure](#project-structure)
- [Configuration & Output](#configuration--output)
- [Supported Networks](#supported-networks)
- [Security & Production Integration](#security--production-integration)
- [Testing & Benchmarks](#testing--benchmarks)
- [Roadmap & Contributing](#roadmap--contributing)
- [Frequently Asked Questions FAQs](#frequently-asked-questions-faq)
- [License & Disclaimer](#license--disclaimer)

---

## Overview

Payment disputes and chargebacks require merchants and payment processors to collect, validate, and present transaction evidence within strict card network rules.

RARE provides an automated pipeline for this workflow by combining:

- Synthetic dispute and transaction generation
- Multi Agent document extraction
- Pydantic based data validation
- 3DS authentication & AVS verification analysis
- Card network rule retrieval (RAG)
- Evidence to rule matching & defense argument generation
- PDF representment packet generation
- FastAPI webhook ingestion

---

## Core Features

### 1. Synthetic Dispute Generation
Generate realistic dispute cases for development, testing, and benchmarking across Visa (`10.4`, `13.1`) and Mastercard (`4837`, `4853`).

### 2. Multi Agent Document Extraction
Extract structured evidence from raw transaction metadata, customer profiles, device fingerprints, and invoice PDFs using validated Pydantic schemas.

### 3. Card Network RAG Rules Engine
Dynamically retrieve card network dispute requirements and compare them against extracted evidence to evaluate liability shift and defense strength.

### 4. PDF Defense Packet Generation
Compile verified evidence, transaction telemetry, and argument narratives into exportable PDF defense packets.

### 5. FastAPI Webhook Integration
Expose REST endpoints (`POST /disputes/represent`) to seamlessly ingest live dispute webhooks from payment gateways.

---

## Requirements & Installation

### Requirements
- Python 3.10+
- pip & virtualenv

### Installation

1. **Clone the repository:**
```bash
   git clone <YOUR_REPOSITORY_URL>
   cd rare-engine
```

2. **Set up virtual environment:**
```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

```


3. **Install dependencies:**
```bash
python -m pip install --upgrade pip # Ignore if newest vesrion is Installed
python -m pip install -r requirements.txt

```



---

## Quickstart & Usage

### CLI Pipeline

Run the pipeline directly from the command line to generate synthetic disputes and build defense packets:

```bash
# Generate and process 5 dispute cases
python -m src.main --mode cli --cases 5 # Case n, where 'n' denotes the size

# Process a larger batch
python -m src.main --mode cli --cases 50

```

### Webhook & REST API

Start the FastAPI ingestion server:

```bash
python -m src.main --mode api

```

* **Interactive API Docs:** `http://127.0.0.1:8000/docs`
* **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`

#### Request Example (`POST /disputes/represent`)

```bash
curl -X POST "[http://127.0.0.1:8000/disputes/represent](http://127.0.0.1:8000/disputes/represent)" \
  -H "Content-Type: application/json" \
  -d '{
    "dispute_id": "disp_LIVE_TEST_01",
    "transaction_id": "pay_LIVE_TEST_01",
    "amount": 15499.00,
    "currency": "INR",
    "reason_code": "10.4",
    "network": "Visa",
    "reason_description": "Other Fraud - Card-Absent Environment",
    "customer": {
      "name": "Pavan Kumar",
      "email": "pavan@example.com",
      "ip_address": "103.21.124.5",
      "shipping_address": "Bengaluru, Karnataka, India"
    },
    "telemetry": {
      "avs_match": "Y",
      "three_ds_version": "2.2.0",
      "three_ds_status": "Y",
      "device_fingerprint": "9f8e7d6c5b4a3210"
    },
    "evidence_files": [
      "data/synthetic_docs/invoice_pay_EXAMPLE.pdf"
    ]
  }'

```

> **Note on `evidence_files`:** In local/testing mode, file paths can be passed directly. For production deployments, pass secure HTTPS presigned object storage URLs (e.g., AWS S3, Google Cloud Storage) or base64-encoded strings.

---

## Technical Architecture

```text
Incoming Dispute Webhook
          |
          v
Validate Webhook & Payload
          |
          v
Extract & Normalize Evidence
          |
   +------+------+
   |      |      |
  AVS    3DS  Invoice
   |      |      |
   +------+------+
          |
          v
Identify Reason Code & Retrieve Network Rules (RAG)
          |
          v
Match Evidence Against Requirements
          |
          v
Generate Defense Argument & Compile PDF Packet

```

---

## Project Structure

```text
rare-engine/
├── data/
│   ├── synthetic_docs/    # Generated evidence PDFs
│   ├── rebuttals/         # Output defense packets (.pdf & .txt)
│   └── test_cases.json    # Dispute datasets
├── src/
│   ├── __init__.py
│   ├── config.py          # System environment & paths
│   ├── document_agent.py  # Evidence extraction & Pydantic validation
│   ├── exporter.py        # PDF defense packet generator
│   ├── main.py            # CLI orchestrator & FastAPI server
│   ├── rag_engine.py      # Network rules retrieval & argument synthesis
│   └── synthetic_generator.py
├── tests/
│   └── test_harness.py    # Test harness & benchmark suite
├── .env
├── .gitignore
├── README.md
└── requirements.txt

```

---

## Configuration & Output

### Environment Variables (`.env`)

```env
APP_ENV=development
LOG_LEVEL=INFO

# File Directories
DATA_DIR=data
SYNTHETIC_DOCS_DIR=data/synthetic_docs
REBUTTALS_DIR=data/rebuttals

# Server Settings
API_HOST=127.0.0.1
API_PORT=8000

# RAG & LLM Settings
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE_PATH=data/vector_db

```

---

## Supported Networks

| Network | Reason Code | Description | Status |
| --- | --- | --- | --- |
| **Visa** | `10.4` | Other Fraud  Card Absent Environment | Supported |
| **Visa** | `13.1` | Merchandise/Services Not Received | Supported |
| **Mastercard** | `4837` | No Cardholder Authorization | Supported |
| **Mastercard** | `4853` | Goods or Services Not Provided | Supported |

---

## Security & Production Integration

When deploying RARE to production environments:

* Enable **HTTPS/TLS** termination and secret management.
* Implement **Webhook Signature Verification** (e.g., HMAC-SHA256) and replay protection.
* Ensure **PII minimization** and compliance with PCI-DSS guidelines (never store raw PANs, CVVs, or sensitive credentials).

---

## Testing & Benchmarks

### Test Execution Hierarchy

```text
Unit Tests -> Component Tests -> Integration Tests -> End-to-End Benchmarks

```

Execute the full automated test harness:

```bash
python -m tests.test_harness

```

Run benchmarking suite over 100 cases:

```bash
python -m src.main --mode cli --cases 100

```

---

## Roadmap & Contributing

* [ ] Support for American Express & Discover networks
* [ ] Async background task processing (Redis / Celery)
* [ ] Interactive merchant UI for human in the loop packet review
* [ ] Real time acquirer webhook integrations

Contributions are welcome! Please open an issue or pull request following our standard feature-branch workflow.

---

## Frequently Asked Questions (FAQ)

### Q.1 How does RARE differ from basic LLM document generation agents?
Standard AI agents act primarily as text summaries or document compilers they attach an invoice to an email without evaluating network rule compliance. RARE is a specialized **RAG powered legal defense engine**. It queries vectorized card network rulebooks (Visa and Mastercard) to evaluate transaction telemetry (such as 3DS 2.2.0 ECI flags and AVS match states), directly citing mandatory network clauses to prove liability shift to the card issuer.

### Q.2. What happens if a merchant submits incomplete evidence?
Submitting weak disputes costs merchants non refundable acquirer fees (ranging from ₹1,600 to ₹8,500 / $20–$100 per dispute notice). RARE executes a **Pydantic Pre Flight Evidence Check** prior to representment generation. If critical evidence (such as delivery tracking for merchandise disputes) is missing, RARE flags the status as `insufficient_evidence`, halts the submission, and generates an exact missing evidence checklist for the merchant.

### Q.3 How does RARE handle sensitive payment data and PCI-DSS compliance?
RARE adheres to strict data minimization principles:
- **Zero Sensitive Card Storage:** RARE never processes, transmits, or stores raw Primary Account Numbers (PANs), CVVs, or magnetic stripe data.
- **Telemetry Only:** The engine evaluates non sensitive transaction metadata, including 3DS ECI authentication tokens, AVS match flags (`Y`/`N`), anonymized IP addresses, and hashed device fingerprints.
- **Local RAG & Storage:** Local vector stores (ChromaDB) allow evidence processing entirely within the merchant's private VPC or air gapped environment.

### Q.4 Can RARE operate without third party paid LLM API keys?
Yes. RARE features a **Pluggable AI Architecture**. While it natively supports enterprise LLM providers (e.g., OpenAI `gpt-4o`, Gemini `Flash-Lite/Flash/Pro`, Anthropic `Sonnet/Opus`), it is designed to run locally using open source embeddings, **ChromaDB** vector databases, and deterministic rule matching logic. This guarantees zero runtime API dependency, low latency, and zero data leakage during development or online deployment.

### Q.5 How easily does RARE integrate with existing Risk Engines & Gateways?
RARE exposes a lightweight **FastAPI REST API** (`POST /disputes/represent`) and supports asynchronous webhook ingestion. Gateways can stream dispute notifications and risk engine outputs directly to RARE. The engine processes the payload and returns structured JSON responses along with compiled PDF defense artifacts ready for acquirer API submission.

### Q.6 What card networks and reason codes are currently supported?
RARE supports high volume fraud and non receipt dispute flows for major card networks:
- **Visa:** `10.4` (Other Fraud  Card Absent Environment) & `13.1` (Merchandise/Services Not Received)
- **Mastercard:** `4837` (No Cardholder Authorization) & `4853` (Goods or Services Not Provided)

>The modular rule retriever architecture allows new reason codes and networks (e.g., American Express, Discover) to be added simply by indexing updated network rule documents into the RAG vector store.

---

## License & Disclaimer

### Disclaimer

RARE is an automated decision support system. Generated representment defense packets should be reviewed against current card network rules and acquirer guidelines. RARE does not guarantee liability shift or chargeback reversal.

### License

This project is licensed under the **MIT License**.