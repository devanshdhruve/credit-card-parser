import pdfplumber
import re
from pathlib import Path

DATE_RE = r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}"
AMOUNT_RE = r"₹?\s*[\d,]+\.\d{2}|\d{1,3}(?:,\d{3})*(?:\.\d{2})?"

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def identify_bank(text):
    """Simple bank identifier based on keywords"""
    t = text.lower()
    if "hdfc" in t or "hdfcbank" in t:
        return "HDFC"
    if "icici" in t or "icicibank" in t:
        return "ICICI"
    if "idfc" in t or "idfc first" in t:
        return "IDFC"
    if "citi" in t:
        return "CITI"
    if "visa" in t and ("card" in t or "statement" in t):
        return "VISA"
    return "UNKNOWN"

def find_last4(text):
    m = re.search(r"card\s*(?:no|number|ending)[:\s]*([0-9Xx\-\s]{4,})", text, re.IGNORECASE)
    if m:
        s = re.sub(r"[^0-9]", "", m.group(1))
        return s[-4:] if len(s) >= 4 else None
    m2 = re.search(r"([0-9]{4})\b(?!\d)", text)
    return m2.group(1) if m2 else None

def find_total_balance(text):
    # try multiple label variations seen in statements
    keys = [
        r"total\s*(?:amount\s*)?due[:\s]*(" + AMOUNT_RE + ")",
        r"total\s*outstanding\s*[:\s]*(" + AMOUNT_RE + ")",
        r"new\s*balance[:\s]*(" + AMOUNT_RE + ")",
        r"total\s*due[:\s]*(" + AMOUNT_RE + ")",
    ]
    for k in keys:
        m = re.search(k, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None

def find_payment_due_date(text):
    m = re.search(r"(?:payment\s*due\s*date|due\s*date)[:\s]*(" + DATE_RE + ")", text, re.IGNORECASE)
    if m:
        return m.group(1)
    m2 = re.search(r"(?:payment\s*due\s*date|due\s*date)[:\s]*([A-Za-z]{3,}\s+\d{1,2},?\s*\d{4})", text, re.IGNORECASE)
    if m2:
        return m2.group(1)
    return None

def find_billing_cycle(text):
    # sample patterns: 'Statement period : 24 Sep 2025 to 23 Oct 2025'
    m = re.search(r"(statement\s*period|billing\s*cycle)[:\s]*([A-Za-z0-9,\-\s\/]+to\s+[A-Za-z0-9,\-\s\/]+)", text, re.IGNORECASE)
    if m:
        return m.group(2).strip()
    # fallback: capture 'Statement Date: dd-mm-yyyy' etc.
    m2 = re.search(r"statement\s*date[:\s]*(" + DATE_RE + ")", text, re.IGNORECASE)
    if m2:
        return m2.group(1)
    return None

def extract_transactions_from_text(text, max_rows=50):
    """
    Best-effort extraction: finds lines that look like 'DD-MM-YYYY  Description  amount'
    Returns list of dicts: {date, description, amount}
    """
    transactions = []
    lines = text.splitlines()
    for line in lines:
        # attempt to find a date at line start
        m = re.search(r"^\s*(" + DATE_RE + r")\s+(.+?)\s+(" + AMOUNT_RE + r")\s*$", line)
        if m:
            date = m.group(1)
            desc = m.group(2).strip()
            amt = m.group(3).strip()
            transactions.append({"date": date, "description": desc, "amount": amt})
            if len(transactions) >= max_rows:
                break
    return transactions


    