import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# --- Import parsing engine ---
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

# --- Flask setup ---
app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# --- Bank parser map ---
PARSERS = {
    "HDFC": parse_hdfc,
    "ICICI": parse_icici,
    "IDFC": parse_idfc,
    "CITI": parse_citi,
    "VISA": parse_visa,
    "UNKNOWN": None,
}


# Serve frontend files
@app.route("/")
def serve_index():
    return send_from_directory("frontend", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("frontend", path)


@app.route("/upload", methods=["POST"])
def upload_pdf():
    print("📩 Received upload request")

    if "pdf" not in request.files:
        print("❌ Missing file field 'pdf'")
        return jsonify({"error": "Missing file field 'pdf'"}), 400

    file = request.files["pdf"]
    if file.filename == "":
        print("❌ No file selected")
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith(".pdf"):
        print("❌ Invalid file type")
        return jsonify({"error": "Invalid file type (only .pdf allowed)"}), 400

    temp_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(temp_path)
    print(f"📂 Saved file to {temp_path}")

    try:
        text = extract_text_from_pdf(temp_path)
        bank = identify_bank(text)
        print(f"🏦 Detected Bank: {bank}")

        parser = PARSERS.get(bank)
        if parser:
            parsed_data = parser(text, temp_path)
        else:
            parsed_data = {
                "last_4_digits": find_last4(text),
                "total_balance": find_total_balance(text),
                "payment_due_date": find_payment_due_date(text),
                "billing_cycle": find_billing_cycle(text),
                "transactions": extract_transactions_from_text(text),
            }

        response = {
            "filename": file.filename,
            "detected_bank": bank,
            "extracted_data": parsed_data,
        }

        print("✅ Successfully parsed PDF")
        return jsonify(response), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": f"Server error: {str(e)}"}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print("🧹 Cleaned up uploaded file")


# Railway Deployment Entry Point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  
    print(f"🚀 Running on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
