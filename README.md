# 💳 Credit Card Statement Parser

A web app that **extracts and analyzes credit card statement PDFs** to give you structured insights such as billing cycle, due date, balance, and transactions — beautifully visualized in a modern, responsive UI.

Built with:
- 🐍 **Flask (Python)** for backend parsing logic  
- 🧠 **Custom PDF parsing engine** for multiple banks (HDFC, ICICI, IDFC, CITI, VISA, etc.)  
- ⚡ **Vanilla JavaScript + HTML + CSS** frontend  
- ☁️ **Deployed on Railway** for seamless hosting  

---

## 🚀 Features

✅ Upload credit card statement PDF  
✅ Auto-detects issuing bank  
✅ Extracts:
- Billing cycle  
- Payment due date  
- Card last 4 digits  
- Total balance  
- Transaction list (date, description, amount, type)

✅ Clean, modern, dark-themed UI  
✅ Drag-and-drop file upload  
✅ Fully responsive (mobile/tablet/desktop)  
✅ Fast and lightweight — no heavy dependencies  

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | HTML, CSS, JavaScript (Vanilla) |
| **Backend** | Python (Flask) |
| **Parsing Engine** | PDF extraction using PyPDF2 / Regex |
| **Deployment** | Railway (Gunicorn + Flask) |
| **Version Control** | Git + GitHub |

---

## 🏗️ Project Structure

```

credit-card-parser/
│
├── app.py                   # Flask main app entry point
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway deployment config
│
├── frontend/                # Web UI
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── backend/                 # Parsing logic
│   ├── parser_engine/
│   │   ├── base_parser.py
│   │   ├── hdfc_parser.py
│   │   ├── icici_parser.py
│   │   ├── idfc_parser.py
│   │   ├── citi_parser.py
│   │   └── visa_parser.py
│
└── uploads/                 # Temporary uploaded PDFs

````

---

## ⚙️ Local Setup (Development)

### 1️⃣ Clone the repository
```bash
git clone https://github.com/devanshdhruve/credit-card-parser.git
cd credit-card-parser
````

### 2️⃣ Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Flask app

```bash
python app.py
```

### 5️⃣ Open in browser

Visit 👉 `http://127.0.0.1:8080`

---

## 🌐 Deployment (Railway)

### 1️⃣ Push your code to GitHub

Make sure your repo contains:

* `app.py`
* `Procfile`
* `requirements.txt`
* `frontend/` folder

### 2️⃣ Deploy to Railway

* Go to [https://railway.app](https://railway.app)
* Create a new project → “Deploy from GitHub”
* Select your repository
* Railway auto-detects Flask and builds the app

✅ Once deployed, you’ll get a public URL like:
`https://credit-card-parser-production.up.railway.app`

---

## 🧠 How It Works

1. User uploads a credit card statement (PDF)
2. Backend extracts text using pdfplumber
3. Bank is identified based on keywords in the text
4. Relevant parser (`hdfc_parser`, `icici_parser`, etc.) is executed
5. Data is cleaned and structured into JSON
6. Frontend displays the summary and transactions beautifully

---

## 🧾 Example Output

| Field             | Example     |
| ----------------- | ----------- |
| **Bank**          | IDFC        |
| **Billing Cycle** | 09 Oct 2025 |
| **Payment Due**   | 26 Oct 2025 |
| **Card Number**   | •••• 3344   |
| **Total Balance** | ₹6,590.00   |

**Transactions:**

| Date        | Description       | Amount   | Type     |
| ----------- | ----------------- | -------- | -------- |
| 12 Sep 2025 | Myntra            | ₹1100.00 | Purchase |
| 16 Sep 2025 | Shell Petrol Pump | ₹900.00  | Purchase |
| 23 Sep 2025 | Groceries Store   | ₹600.00  | Purchase |

---

## 🧰 Requirements

* Python 3.8+
* Flask
* Flask-CORS
* PyPDF2 / pdfminer.six
* Gunicorn (for production)

---

## 📦 Example `Procfile`

```
web: gunicorn app:app
```

This ensures Railway uses Gunicorn to serve Flask efficiently.

---

## 🤝 Contributing

Pull requests are welcome!
If you’d like to add a new bank parser (e.g., SBI or Axis Bank):

1. Create a new parser file in `backend/parser_engine/`
2. Implement a `parse_<bank>.py` function
3. Add it to the `PARSERS` dictionary in `app.py`

---

## 🧑‍💻 Author

**Devansh Dhruve**
💼 GitHub: [@devanshdhruve](https://github.com/devanshdhruve)
📧 Email: *[dhruvedevansh@gmail.com](mailto:dhruvedevansh@gmail.com)*

---




