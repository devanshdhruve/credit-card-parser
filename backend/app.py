import os
from flask import Flask, request, jsonify
from waitress import serve

# --- Import our parsing engine ---
from parser_engine.base_parser import (
    extract_text_from_pdf,
    identify_bank,
    find_last4,
    find_total_balance,
    find_payment_due_date,
    find_billing_cycle,
    extract_transactions_from_text,
)
from parser_engine.hdfc_parser import parse_hdfc
from parser_engine.icici_parser import parse_icici
from parser_engine.idfc_parser import parse_idfc
from parser_engine.citi_parser import parse_citi
from parser_engine.visa_parser import parse_visa


# --- Flask app setup ---
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# --- Bank parsers mapping ---
PARSERS = {
    "HDFC": parse_hdfc,
    "ICICI": parse_icici,
    "IDFC": parse_idfc,
    "CITI": parse_citi,
    "VISA": parse_visa,
    "UNKNOWN": None,
}


@app.route("/upload", methods=["POST"])
def upload_pdf():
    """
    Upload a credit card statement (PDF), auto-detect the bank,
    parse key details, and return structured data.
    """

    # 1️⃣ Validate the file
    if "pdf" not in request.files:
        return jsonify({"error": "Missing file field 'pdf'"}), 400

    file = request.files["pdf"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Invalid file type (only .pdf allowed)"}), 400

    # 2️⃣ Save temporarily
    temp_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(temp_path)

    try:
        # 3️⃣ Extract text & identify bank
        text = extract_text_from_pdf(temp_path)
        bank = identify_bank(text)

        # --- 4️⃣ Call bank-specific parser ---
        parser = PARSERS.get(bank)
        if parser:
            # Pass both text and file path for advanced parsers
            parsed_data = parser(text, temp_path)
        else:
            # Fallback generic parsing
            parsed_data = {
            "last_4_digits": find_last4(text),
            "total_balance": find_total_balance(text),
            "payment_due_date": find_payment_due_date(text),
            "billing_cycle": find_billing_cycle(text),
            "transactions": extract_transactions_from_text(text),
        }


        # 5️⃣ Prepare the response
        response = {
            "filename": file.filename,
            "detected_bank": bank,
            "extracted_data": parsed_data,
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred while processing the file: {str(e)}"}), 500

    finally:
        # 6️⃣ Always clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/", methods=["GET"])
def index():
    """Simple health-check route."""
    return jsonify({
        "message": "Credit Card Statement Parser API is running",
        "upload_endpoint": "/upload",
        "method": "POST",
        "field": "pdf",
    })


# --- Run the server ---
if __name__ == "__main__":
    print("🚀 Starting backend server on http://localhost:8080 ...")
    serve(app, host="0.0.0.0", port=8080)
