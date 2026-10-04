import json
import random
from pathlib import Path
from typing import Optional

from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from rare.config.settings import settings

fake = Faker()

REASON_CODES = [
    {
        "code": "10.4",
        "network": "Visa",
        "description": "Other Fraud - Card-Absent Environment",
    },
    {
        "code": "4837",
        "network": "Mastercard",
        "description": "No Cardholder Authorization",
    },
]


def generate_pdf_invoice(
    filepath: Path,
    transaction_id: str,
    customer_name: str,
    amount: float,
    item_name: str,
):
    """Generates a synthetic PDF invoice with RPay branding."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(filepath), pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "RPay Transaction Invoice")

    c.setFont("Helvetica", 10)
    c.drawString(50, 720, f"Transaction ID: {transaction_id}")
    c.drawString(50, 705, f"Customer: {customer_name}")
    c.drawString(50, 690, f"Item Description: {item_name}")
    c.drawString(50, 675, f"Amount Paid: INR {amount:,.2f}")
    c.drawString(50, 660, f"Date: {fake.date_this_year()}")

    c.save()


def generate_synthetic_dataset(
    count: int = 5,
    num_cases: Optional[int] = None,
):
    settings.SYNTHETIC_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

    total_cases = num_cases if num_cases is not None else count
    test_cases = []

    for i in range(1, total_cases + 1):
        dispute_id = f"DISP-{1000 + i}"
        txn_id = f"TXN-{random.randint(100000, 999999)}"
        amount = round(random.uniform(500.0, 50000.0), 2)
        reason = random.choice(REASON_CODES)
        cust_name = fake.name()
        cust_email = fake.email()

        pdf_filename = f"{dispute_id}_invoice.pdf"
        pdf_path = settings.SYNTHETIC_DOCS_DIR / pdf_filename

        generate_pdf_invoice(
            filepath=pdf_path,
            transaction_id=txn_id,
            customer_name=cust_name,
            amount=amount,
            item_name=fake.catch_phrase(),
        )

        relative_evidence_path = str(
            pdf_path.resolve().relative_to(settings.PROJECT_ROOT.resolve())
        )

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
                "shipping_address": fake.address().replace("\n", ", "),
            },
            "telemetry": {
                "avs_match": "Y",
                "three_ds_version": "2.2.0",
                "three_ds_status": "Y",
                "device_fingerprint": fake.sha256(),
            },
            "evidence_files": [relative_evidence_path],
        }

        test_cases.append(dispute_case)

    with open(settings.TEST_CASES_FILE, "w", encoding="utf-8") as f:
        json.dump(test_cases, f, indent=2)


if __name__ == "__main__":
    generate_synthetic_dataset()
