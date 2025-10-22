# backend/parser_engine/icici_parser.py
import re
import pdfplumber
from .base_parser import (
    find_last4,
    find_total_balance,
    find_payment_due_date,
    find_billing_cycle,
)

def parse_icici(text, pdf_path=None):
    """
    ICICI Bank parser – handles multiline date formats like:
        15 Sep
        2025
        Amazon India 2,499.00 Purchase
    and merges them into a single transaction entry.
    """

    data = {}

    # --- 1️⃣ Basic meta extraction ---
    data["last_4_digits"] = find_last4(text)
    data["total_balance"] = find_total_balance(text)

    # Payment Due Date
    due_match = re.search(
        r"Payment\s*Due\s*Date[:\s]+([0-9]{1,2}\s+[A-Za-z]{3,}\s+\d{4})",
        text,
        re.IGNORECASE,
    )
    data["payment_due_date"] = due_match.group(1).strip() if due_match else None

    # Billing / Statement Date
    cycle_match = re.search(
        r"Statement\s*Date[:\s]+([0-9]{1,2}\s+[A-Za-z]{3,}\s+\d{4})",
        text,
        re.IGNORECASE,
    )
    data["billing_cycle"] = cycle_match.group(1).strip() if cycle_match else None

    # --- 2️⃣ Isolate TRANSACTION DETAILS section ---
    section_match = re.search(
        r"TRANSACTION DETAILS(.*?)REWARDS SUMMARY",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    section_text = section_match.group(1) if section_match else ""
    lines = [l.strip() for l in section_text.splitlines() if l.strip()]

    # --- 3️⃣ Merge lines into structured blocks ---
    transactions = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Look for line that matches "15 Sep" or "01 Oct" etc.
        if re.match(r"^\d{1,2}\s+[A-Za-z]{3}$", line) and i + 1 < len(lines):
            next_line = lines[i + 1]
            # if next line is year (e.g., 2025)
            if re.match(r"^\d{4}$", next_line) and i + 2 < len(lines):
                date = f"{line} {next_line}"
                details = lines[i + 2]

                # Now match description, amount, and type in the next line
                m = re.search(
                    r"(.+?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2}))\s+(Purchase|Cash\s*Advance|Finance\s*Charge)",
                    details,
                    re.IGNORECASE,
                )
                if m:
                    transactions.append({
                        "date": date.strip(),
                        "description": m.group(1).strip(),
                        "amount": m.group(2).replace(",", "").strip(),
                        "type": m.group(3).strip(),
                    })
                i += 3
                continue

        # Handle single-line date format (like "01 Oct 2025 ...")
        m2 = re.match(
            r"(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})\s+(.+?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2}))\s+(Purchase|Cash\s*Advance|Finance\s*Charge)",
            line,
            re.IGNORECASE,
        )
        if m2:
            transactions.append({
                "date": m2.group(1).strip(),
                "description": m2.group(2).strip(),
                "amount": m2.group(3).replace(",", "").strip(),
                "type": m2.group(4).strip(),
            })
        i += 1

    data["transactions"] = transactions
    return data
