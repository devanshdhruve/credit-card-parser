import re
from .base_parser import find_last4, find_total_balance, find_payment_due_date, find_billing_cycle, extract_transactions_from_text

def parse_hdfc(text):
    data = {}
    # HDFC often uses 'Card No:' or 'Card No' label
    data['last_4_digits'] = find_last4(text)
    data['total_balance'] = find_total_balance(text)
    data['payment_due_date'] = find_payment_due_date(text)
    data['billing_cycle'] = find_billing_cycle(text)

    # HDFC lists transactions under 'Domestic Transactions' etc.
    txs = extract_transactions_from_text(text)
    data['transactions'] = txs
    return data
