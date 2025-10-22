# backend/parser_engine/visa_parser.py
import re
import pdfplumber
from .base_parser import (
    find_total_balance,
    find_billing_cycle,
    find_payment_due_date,
)

def find_last4_custom(text):
    """Find 4 consecutive digits preceded by X or shown as masked card."""
    m = re.search(r"X{2,4}[-\s]*X{2,4}[-\s]*X{2,4}[-\s]*(\d{4})", text)
    if m:
        return m.group(1)
    return None

def parse_visa(text, pdf_path=None):
    """
    Parser for VISA card statement (full layout).
    Uses table parsing for transactions and regex for top-level fields.
    """
    data = {}

    # --- Core field extraction ---
    data["last_4_digits"] = find_last4_custom(text)
    data["total_balance"] = find_total_balance(text)

    # Payment Due Date
    due_match = re.search(
        r"Payment\s*Due\s*Date[:\s]+([0-9]{1,2}\s+[A-Za-z]{3,}\s+\d{4})",
        text, re.IGNORECASE)
    data["payment_due_date"] = due_match.group(1).strip() if due_match else None

    # Billing Cycle / Statement Date
    bill_match = re.search(
        r"Statement\s*Date[:\s]+([0-9]{1,2}\s+[A-Za-z]{3,}\s+\d{4})",
        text, re.IGNORECASE)
    data["billing_cycle"] = bill_match.group(1).strip() if bill_match else None

    # --- Extract transactions ---
    parsed_transactions = []
    if pdf_path:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text_page = page.extract_text() or ""
                if "TRANSACTION DETAILS" not in text_page:
                    continue

                tables = page.extract_tables(
                    table_settings={
                        "vertical_strategy": "lines",
                        "horizontal_strategy": "lines",
                        "snap_tolerance": 3,
                        "join_tolerance": 3,
                        "edge_min_length": 40,
                        "intersection_y_tolerance": 5,
                    }
                )

                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    headers = [h.strip().lower() if h else "" for h in table[0]]
                    if "date" in headers and "description" in headers:
                        for row in table[1:]:
                            if len(row) < 4:
                                continue
                            date, desc, amount, tx_type = row[:4]
                            if not re.search(r"\d", amount or ""):
                                continue
                            parsed_transactions.append({
                                "date": (date or "").strip(),
                                "description": re.sub(r"\s+", " ", (desc or "").strip()),
                                "amount": (amount or "").replace(",", "").strip(),
                                "type": (tx_type or "").strip()
                            })

    # --- Fallback regex extraction if no tables found ---
    if not parsed_transactions:
        lines = text.splitlines()
        for line in lines:
            m = re.search(
                r"(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})\s+(.+?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2}))\s+(Purchase|Finance\s*Charge|Cash\s*Advance)",
                line, re.IGNORECASE)
            if m:
                parsed_transactions.append({
                    "date": m.group(1).strip(),
                    "description": m.group(2).strip(),
                    "amount": m.group(3).replace(",", "").strip(),
                    "type": m.group(4).strip(),
                })

    data["transactions"] = parsed_transactions
    return data
