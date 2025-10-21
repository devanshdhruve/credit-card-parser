from .base_parser import find_last4, find_total_balance, find_payment_due_date, find_billing_cycle, extract_transactions_from_text

def parse_visa(text):
    data = {}
    # Visa statements often show the card network logo but the content is similar to bank statements.
    data['last_4_digits'] = find_last4(text)
    data['total_balance'] = find_total_balance(text)
    data['payment_due_date'] = find_payment_due_date(text)
    data['billing_cycle'] = find_billing_cycle(text)
    data['transactions'] = extract_transactions_from_text(text)
    return data