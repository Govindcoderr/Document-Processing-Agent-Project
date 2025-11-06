# 🧾 Document Processing Agent

An **AI-powered invoice automation system** that extracts data from **PDFs and images**, validates the extracted fields, and automatically pushes them into your ERP (Odoo or ERPNext).

---

## 🚀 Features

✅ OCR-based text extraction from PDF, PNG, JPG, JPEG  
✅ AI (LLM) field extraction — invoice no, date, total, vendor name  
✅ Automatic data validation  
✅ ERP integration (Odoo XML-RPC or ERPNext REST API)  
✅ Streamlit or FastAPI-based UI for real-time uploads  
✅ Modular backend with clear folder structure  

---
### 🧩 Folder Structure
```
document_processing_agent/
│
├── backend/
│ ├── main.py # FastAPI entrypoint
│ ├── ocr_extractor.py # PDF/image OCR logic (Tesseract + Poppler + CV2)
│ ├── llm_extractor.py # LLM-powered data parsing
│ ├── data_validator.py # Field validation & cleanup
│ ├── db.py # SQLite or Postgres database operations
│ ├── erp_integration.py # Odoo or ERPNext connection logic
│ └── utils/ # helper utilities (logging, file utils)
│
├── frontend/
│ └── app.py # Streamlit UI (file upload + status display)
│
├── .env # credentials for ERP & APIs
├── requirements.txt
└── README.md
```

---

## 🛠️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/document-processing-agent.git
cd document-processing-agent
```
2️⃣ Create and activate a virtual environment
```
python -m venv .venv
.venv\Scripts\activate     # on Windows
source .venv/bin/activate  # on Linux/Mac
```
3️⃣ Install dependencies
```
pip install -r requirements.txt
```
4️⃣ Configure environment variables

# OCR
```
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
POPPLER_PATH=C:\poppler-25.07.0\Library\bin
```
# ERP (choose Odoo or ERPNext)
```
ODOO_URL=https://yourcompany.odoo.com/odoo
ODOO_DB=your_db
ODOO_USERNAME=your_email@example.com
ODOO_PASSWORD=your_password
```
# OR (ERPNext)
```
ERP_URL=https://yourcompany.erpnext.com
ERP_API_KEY=your_api_key
ERP_API_SECRET=your_api_secret
```
5️⃣ Run the backend (FastAPI)
```
uvicorn backend.main:app --reload
```
Backend runs on: http://127.0.0.1:8000/docs

6️⃣ (Optional) Run the Streamlit frontend
```
streamlit run frontend/app.py
```

🧠 How It Works
```
1️⃣ Upload an invoice (PDF/JPG/PNG)
2️⃣ OCR converts it to text (via Tesseract + Poppler)
3️⃣ LLM parses invoice fields (number, date, total, vendor)
4️⃣ Data validator checks required fields
5️⃣ Data is stored in local DB and pushed to ERP automatically
```
📸 Example Output
```
✅ Extracted text using OCR on image
🧾 Cleaned OCR Text: STRIPESSHOP INVOICE NUMBER 9000000001
🔍 Extracted fields: {'invoice_number': '9000000001', 'invoice_date': 'Dec 11, 2020', 'total': '162.37', 'vendor_name': 'StripesShop'}
✅ Invoice Processed Successfully!
```

⚙️ Tech Stack
```
ComponentTechnologyOCRTesseract + Poppler + OpenCVLLMGroq / OpenAI / Local LlamaBackendFastAPIFrontendStreamlitDatabaseSQLite / PostgreSQLERPOdoo / ERPNext
```
🤝 Contributing
```
Pull requests are welcome!
For major changes, please open an issue first to discuss what you’d like to change.
```
📜 License
```
This project is licensed under the MIT License.
```
💡 Created by Govind Rajpurohit
“Automating the way businesses read their documents.”

---


----
<img width="2870" height="1439" alt="Screenshot 2025-11-06 124804" src="https://github.com/user-attachments/assets/ed805bd7-b11e-4208-95e7-0784f473110c" />

-----
<img width="2869" height="1449" alt="Screenshot 2025-11-06 124828" src="https://github.com/user-attachments/assets/764f4612-ded2-4e9d-894c-efa1ea5a9848" />

----
<img width="2880" height="1620" alt="Screenshot 2025-11-06 124726" src="https://github.com/user-attachments/assets/481f59c2-9920-4f43-bbcb-97b05d3dec23" />
----
<img width="789" height="672" alt="Screenshot 2025-11-06 151108" src="https://github.com/user-attachments/assets/a40f4193-d503-4fea-a43e-b60d6ad689d0" />

----
<img width="2869" height="1461" alt="Screenshot 2025-11-06 182336" src="https://github.com/user-attachments/assets/691cb474-5f11-45f9-8b69-834de7e4e66c" />
---
<img width="2880" height="1620" alt="Screenshot 2025-11-06 182411" src="https://github.com/user-attachments/assets/a040d812-aad8-4102-8591-ee434645f1ed" />
----
