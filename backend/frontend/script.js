const uploadBtn = document.getElementById("uploadBtn");
const pdfFile = document.getElementById("pdfFile");
const fileName = document.getElementById("fileName");
const resultDiv = document.getElementById("result");
const uploadBox = document.getElementById("uploadBox");
const btnText = document.getElementById("btnText");

// 🎨 Glow effect on drag
uploadBox.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadBox.classList.add("dragging");
});

uploadBox.addEventListener("dragleave", (e) => {
  e.preventDefault();
  uploadBox.classList.remove("dragging");
});

uploadBox.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadBox.classList.remove("dragging");

  const files = e.dataTransfer.files;
  if (files.length && files[0].type === "application/pdf") {
    pdfFile.files = files;
    fileName.textContent = `📎 ${files[0].name}`;
  } else {
    alert("Please upload a valid PDF file.");
  }
});

// 🧾 Display selected filename
pdfFile.addEventListener("change", () => {
  if (pdfFile.files.length) {
    fileName.textContent = `📎 ${pdfFile.files[0].name}`;
  }
});

// 🚀 Upload & Analyze
uploadBtn.addEventListener("click", async () => {
  if (!pdfFile.files.length) {
    alert("Please select or drop a PDF file first!");
    return;
  }

  const formData = new FormData();
  formData.append("pdf", pdfFile.files[0]);

  uploadBtn.disabled = true;
  btnText.innerHTML = '<span class="spinner"></span>Analyzing...';

  try {
    const response = await fetch("http://127.0.0.1:8080/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Failed to process PDF");
    const data = await response.json();
    displayResult(data);
  } catch (error) {
    alert("Error: " + error.message);
  } finally {
    uploadBtn.disabled = false;
    btnText.textContent = "Upload & Analyze";
  }
});

// 🧩 Render results
function displayResult(data) {
  resultDiv.classList.remove("hidden");

  const extractedData = data.extracted_data || {};
  const detectedBank = data.detected_bank || "Unknown";

  const summaryGrid = document.getElementById("summaryGrid");
  summaryGrid.innerHTML = `
    <div class="summary-item"><strong>Bank</strong><span>${detectedBank}</span></div>
    <div class="summary-item"><strong>Billing Cycle</strong><span>${extractedData.billing_cycle || "N/A"}</span></div>
    <div class="summary-item"><strong>Payment Due</strong><span>${extractedData.payment_due_date || "N/A"}</span></div>
    <div class="summary-item"><strong>Card Number</strong><span>•••• ${extractedData.last_4_digits || "N/A"}</span></div>
    <div class="summary-item"><strong>Total Balance</strong><span>₹${extractedData.total_balance || "N/A"}</span></div>
  `;

  const transactions = extractedData.transactions || [];
  const transactionsTable = document.getElementById("transactionsTable");
  transactionsTable.innerHTML = "";

  document.getElementById("transactionCount").textContent =
    `${transactions.length} transaction${transactions.length !== 1 ? "s" : ""}`;

  if (transactions.length > 0) {
    transactions.forEach((tx) => {
      const row = document.createElement("tr");
      const typeClass = tx.type?.toLowerCase()?.replace(/\s+/g, "-") || "unknown";
      row.innerHTML = `
        <td>${tx.date || "N/A"}</td>
        <td>${tx.description || "N/A"}</td>
        <td class="amount">₹${tx.amount || "N/A"}</td>
        <td><span class="type-badge type-${typeClass}">${tx.type || "N/A"}</span></td>
      `;
      transactionsTable.appendChild(row);
    });
  } else {
    transactionsTable.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:20px;">No transactions found</td></tr>`;
  }

  resultDiv.scrollIntoView({ behavior: "smooth", block: "start" });
}
