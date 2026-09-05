import json
import os
import random
import string
from datetime import datetime
from pathlib import Path
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

fake = Faker()

def generate_alphanumeric(length: int = 14) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SYNTHETIC_DOCS_DIR = DATA_DIR / "synthetic_docs"
TEST_CASES_FILE = DATA_DIR / "test_cases.json"

REASON_CODES = [
    {"code": "10.4", "network": "Visa", "description": "Other Fraud - Card-Absent Environment"},
    {"code": "4837", "network": "Mastercard", "description": "No Cardholder Authorization"},
    {"code": "4853", "network": "Mastercard", "description": "Defective/Not as Described"},
    {"code": "13.1", "network": "Visa", "description": "Merchandise/Services Not Received"}
]

def generate_pdf_invoice(filepath: Path, transaction_id: str, customer_name: str, amount: float, item_name: str):
    """Generates a synthetic PDF invoice with RPay branding."""
    c = canvas.Canvas(str(filepath), pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "RPAY MERCHANT INVOICE")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, 730, f"Transaction ID: {transaction_id}")
    c.drawString(50, 715, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, 700, f"Customer Name: {customer_name}")
    
    c.line(50, 685, 550, 685)
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 665, "Description")
    c.drawString(450, 665, "Amount (INR)")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, 645, item_name)
    c.drawString(450, 645, f"INR {amount:,.2f}")
    
    c.line(50, 630, 550, 630)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(350, 610, "Total Paid:")
    c.drawString(450, 610, f"INR {amount:,.2f}")
    
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 550, "AVS Match: Y | 3DS Authenticated: True | IP: 192.168.1.45")
    c.save()

def generate_synthetic_dataset(num_cases: int = 5):
    """Generates dispute payloads and synthetic PDF evidence."""
    SYNTHETIC_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    disputes = []

    print(f"[*] Generating {num_cases} synthetic dispute cases...")

    for i in range(1, num_cases + 1):
        txn_id = f"pay_{generate_alphanumeric(14)}"
        dispute_id = f"disp_{generate_alphanumeric(14)}"
        cust_name = fake.name()
        cust_email = fake.email()
        amount = round(random.uniform(500.0, 45000.0), 2)
        reason = random.choice(REASON_CODES)
        item_name = fake.bs().title()
        
        pdf_filename = f"invoice_{txn_id}.pdf"
        pdf_path = SYNTHETIC_DOCS_DIR / pdf_filename
        
        generate_pdf_invoice(pdf_path, txn_id, cust_name, amount, item_name)
        
        dispute_case = {
            "dispute_id": dispute_id,
            "transaction_id": txn_id,
            "amount": amount,
            "currency": "INR",
            "reason_code": reason["code"],
            "network": reason["network"],
            "reason_description": reason["description"],
            "customer": {
                "name": cust_name,
                "email": cust_email,
                "ip_address": fake.ipv4(),
                "shipping_address": fake.address().replace("\n", ", ")
            },
            "telemetry": {
                "avs_match": "Y",
                "three_ds_version": "2.2.0",
                "three_ds_status": "Y",
                "device_fingerprint": fake.sha256()
            },
            "evidence_files": [
                str(pdf_path.relative_to(BASE_DIR))
            ]
        }
        disputes.append(dispute_case)

    with open(TEST_CASES_FILE, "w", encoding="utf-8") as f:
        json.dump(disputes, f, indent=2)

    print(f"[✓] Generated {num_cases} dispute payloads saved to: {TEST_CASES_FILE}")
    print(f"[✓] Generated synthetic PDF invoices in: {SYNTHETIC_DOCS_DIR}")

if __name__ == "__main__":
    generate_synthetic_dataset()