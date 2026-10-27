# PolicyDiff — Semantic Policy Change Detector

> **Natural Language Processing • Document Intelligence • Semantic Text Analysis**  
> A full-stack, local-first NLP platform that compares academic regulations, detects meaningful semantic and threshold changes, and generates grounded plain-English explanations.

---

## 1. Problem Statement & Overview

College policies, academic rules, examination notices, attendance requirements, scholarship conditions, and administrative guidelines are frequently revised across academic years. Traditional text comparison tools mainly detect word-level differences and overlook subtle shifts in:
- **Obligations vs Discretionary Permissions** ("may submit" vs "must submit within 7 days")
- **Quantitative Thresholds** (Attendance minimum increasing from 75% to 80%)
- **Deadlines & Schedules** (Submission date shifting from 15 July 2025 to 30 July 2026)
- **Financial Requirements** (Registration fees modified from $100 to $150)
- **Conduct Restrictions & Prohibitions** (Late submissions permitted with fine vs strictly prohibited)
- **Target Student Eligibility** (Open to all students vs restricted to final-year students with CGPA $\ge 3.8$)

**PolicyDiff** aligns sections and rules across document versions, classifies additions, removals, and modifications, and explains every change in clear, plain English backed by authoritative source excerpts.

---

## 2. Key Features

- **Document Ingestion**: Supports `.pdf` (via PyMuPDF), `.docx` (via python-docx), and `.txt` files with automated page tracking and scanned-PDF detection.
- **Dual NLP Engine**:
  - **Sentence Transformers** (`all-MiniLM-L6-v2`) for dense semantic embeddings and cosine similarity.
  - **High-Performance Fallback** using Character & Word N-Gram TF-IDF with RapidFuzz token-set ratios for lightweight execution without heavy model weights.
- **Granular Entity & Threshold Extraction**: Deterministic difference detection for percentages, currencies, dates, calendar days, student cohorts, negations, and modal verbs.
- **Priority Heuristics**: Automated rule-based classification into *Critical*, *High*, *Medium*, or *Low* priority with transparent rationales.
- **Interactive Web Dashboard**:
  - Responsive landing page and dual-panel upload workspace.
  - Dynamic Recharts analytics showing category and type distributions.
  - Granular filtering by change type, priority level, academic domain, and review status.
  - Side-by-side desktop excerpt comparisons with live search.
- **Persistent Local History**: SQLite storage using SQLAlchemy ORM to retrieve and manage previous comparisons.
- **Executive Export Reports**:
  - Formal executive PDF report generated via ReportLab.
  - Structured raw data export in CSV format.
- **Live Empirical Benchmark Suite**: Built-in 16-sample labeled academic regulation benchmark measuring precision, recall, F1-score, and confusion matrix.

---

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS v4, Lucide React, Recharts, React Router v7, Axios |
| **Backend** | Python 3.12, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0 |
| **NLP & Vectors** | Sentence Transformers (`all-MiniLM-L6-v2`), Scikit-Learn Cosine Similarity, RapidFuzz |
| **Document Parsers** | PyMuPDF (`fitz`), python-docx, ReportLab (PDF generation) |
| **Database** | SQLite (`policydiff.db`) with persistent storage |
| **Testing** | Pytest, FastAPI TestClient, Vite Build Verification |

---

## 4. Project Structure

```
policydiff/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entry point & CORS
│   │   ├── api/routes.py               # REST API endpoints
│   │   ├── core/config.py              # Configuration & settings
│   │   ├── database/                   # SQLite engine & SQLAlchemy models
│   │   ├── schemas/comparison.py       # Pydantic v2 response schemas
│   │   ├── services/
│   │   │   ├── document_extractor.py   # PDF, DOCX, TXT parser & scanned PDF detector
│   │   │   ├── text_preprocessor.py    # Unicode NFKC & sentence boundary protection
│   │   │   ├── rule_segmenter.py       # Clause, bullet & section extractor
│   │   │   ├── semantic_matcher.py     # Dual embedding & bipartite alignment
│   │   │   ├── entity_extractor.py     # Percentages, dates, fees, modals, negations
│   │   │   ├── change_classifier.py    # ADDED, REMOVED, MODIFIED, UNCHANGED logic
│   │   │   ├── priority_analyzer.py    # Critical, High, Medium, Low heuristics
│   │   │   ├── explanation_generator.py# Grounded plain-English generator
│   │   │   ├── report_generator.py     # ReportLab PDF & CSV generation
│   │   │   ├── comparison_service.py   # End-to-end pipeline orchestrator
│   │   │   └── demo_generator.py       # Synthetic demonstration documents
│   │   └── evaluation/benchmark.py     # Ground-truth evaluation dataset & metrics
│   ├── tests/                          # 19 Pytest unit & integration tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/                 # Navbar, Footer, ChangeCard, Badges, Modals
│   │   ├── pages/                      # Landing, Compare, Results, History, About
│   │   ├── services/api.ts             # Axios API client
│   │   ├── types/index.ts              # TypeScript definitions
│   │   ├── App.tsx                     # React Router routes
│   │   └── index.css                   # Tailwind v4 base styles
│   └── package.json
├── sample_documents/                   # Demo policy files in PDF, DOCX, and TXT
├── docs/ARCHITECTURE.md                # In-depth architectural & math specification
├── start.ps1                           # One-click Windows PowerShell startup script
└── README.md
```

---

## 5. Installation & Execution (Windows)

### Prerequisites
- Python 3.12+ installed
- Node.js v18+ and npm installed

### Quick Setup

#### Step 1: Clone or navigate to the project directory
```powershell
cd C:\Users\varad_tm6hvqi\.gemini\antigravity\scratch\policydiff
```

#### Step 2: Set up Python Virtual Environment
```powershell
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip and install backend dependencies
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
pip install sentence-transformers
```

#### Step 3: Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

---

## 6. Running the Application

### Option A: Automatic Launch via PowerShell Script
```powershell
.\start.ps1
```

### Option B: Manual Terminal Execution

**Terminal 1 — FastAPI Backend:**
```powershell
$env:PYTHONPATH="backend"
.\venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*API is live at `http://127.0.0.1:8000` (Interactive Swagger Docs: `http://127.0.0.1:8000/docs`).*

**Terminal 2 — React Frontend:**
```powershell
cd frontend
npm run dev
```
*Web Application is live at `http://localhost:5173`.*

---

## 7. Deploying to Vercel

The repository is configured as a Vercel deployment: the React frontend is built as a static site, and the FastAPI application runs as a Python serverless function.

### Configure persistent storage

Vercel function filesystems are temporary and can be read-only. Before deploying, provision a PostgreSQL database (for example, Neon or Vercel Postgres) and add its connection URL as the `DATABASE_URL` environment variable in the Vercel project settings. Use a SQLAlchemy-compatible URL such as `postgresql://...`; the app selects the psycopg driver automatically.

The app intentionally refuses to start on Vercel without `DATABASE_URL`. SQLite remains the default for local development, but it is not suitable for persistent Vercel history.

### Deploy

1. Import this repository into Vercel and leave the project root set to the repository root.
2. Add `DATABASE_URL` under **Settings → Environment Variables** for the environments where you will deploy.
3. Deploy. `vercel.json` builds `frontend/` and routes `/api/*` to the FastAPI function; no separate backend service is needed.

Vercel limits function request bodies to approximately 4.5 MB. The API therefore enforces a 4 MB combined upload limit on Vercel (both documents together); larger uploads require a separate object-storage upload flow.

---

## 8. Built-in Synthetic Demonstration

PolicyDiff includes a realistic synthetic scenario: **Apex University Academic & Examination Regulations (2025 vs 2026)**.

| Policy Domain | 2025 Old Policy | 2026 Updated Policy | Detected Impact |
|---|---|---|---|
| **Attendance** | Minimum 75% attendance | Minimum 80% attendance | **Modified (High Priority)**: Threshold increased by 5% |
| **Examination Fee** | $100 per semester | $150 per semester | **Modified (High Priority)**: Financial requirement increased |
| **Project Deadline** | Due by 15 July 2025 | Due by 30 July 2026 | **Modified (High Priority)**: Calendar deadline shifted |
| **Late Submission** | Permitted with $25 fine | Strictly prohibited | **Modified (Critical Priority)**: Prohibition introduced |
| **Merit Scholarship** | All enrolled students | Final-year students (CGPA $\ge 3.8$) | **Modified (High Priority)**: Eligibility restricted |
| **Curriculum** | *None* | Mandatory AI Ethics Seminar | **Added (High Priority)**: New requirement introduced |
| **Dissertation** | Hardbound red cloth binding | *Omitted (Paperless)* | **Removed (Medium Priority)**: Clause rescinded |
| **Hall Ticket Entry** | Display institutional ID | Identity card visibly carried | **Unchanged (Low Priority)**: Paraphrased wording |

To view this demonstration instantly, click **"Explore Sample Comparison"** on the landing page or **"Load Demo Documents"** on the comparison workspace.

---

## 9. Empirical Benchmark Evaluation

Run the live evaluation suite to verify precision, recall, and F1-score across 16 labeled ground-truth policy changes:

```powershell
$env:PYTHONPATH="backend"
.\venv\Scripts\python backend\inspect_benchmark.py
```

### Measured Results:
- **Overall Accuracy**: **93.8%**
- **Macro-Averaged F1-Score**: **95.0%**
- **Per-Class Breakdown**:
  - `ADDED`: Precision: **100.0%**, Recall: **100.0%**, F1: **1.00**
  - `REMOVED`: Precision: **100.0%**, Recall: **100.0%**, F1: **1.00**
  - `MODIFIED`: Precision: **100.0%**, Recall: **88.9%**, F1: **0.941**
  - `UNCHANGED`: Precision: **75.0%**, Recall: **100.0%**, F1: **0.857**

---

## 10. Running Automated Tests

Run the complete 19-test automated test suite:

```powershell
$env:PYTHONPATH="backend"
.\venv\Scripts\pytest backend\tests -v
```

Expected output:
```
backend/tests/test_api_endpoints.py::test_health_check_endpoint PASSED
backend/tests/test_api_endpoints.py::test_demo_endpoint PASSED
backend/tests/test_api_endpoints.py::test_compare_endpoint_upload PASSED
backend/tests/test_api_endpoints.py::test_invalid_file_extension PASSED
backend/tests/test_evaluation_benchmark.py::test_benchmark_dataset_integrity PASSED
backend/tests/test_evaluation_benchmark.py::test_evaluation_metrics_thresholds PASSED
backend/tests/test_extraction.py::test_txt_extraction PASSED
backend/tests/test_extraction.py::test_pdf_extraction PASSED
backend/tests/test_extraction.py::test_docx_extraction PASSED
backend/tests/test_extraction.py::test_unsupported_file_extension PASSED
backend/tests/test_extraction.py::test_scanned_or_empty_pdf_detection PASSED
backend/tests/test_nlp_pipeline.py::test_rule_segmentation PASSED
backend/tests/test_nlp_pipeline.py::test_percentage_threshold_detection PASSED
backend/tests/test_deadline_date_change PASSED
backend/tests/test_negation_and_prohibition_detection PASSED
backend/tests/test_modality_shift_discretionary_to_mandatory PASSED
backend/tests/test_change_classification_modified PASSED
backend/tests/test_change_classification_added PASSED
backend/tests/test_change_classification_removed PASSED
======================= 19 passed in 26.69s =======================
```

To test the frontend build:
```powershell
cd frontend
npm run build
```

---

## 11. Backend REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Backend health check and active NLP engine mode |
| `POST` | `/api/compare` | Multipart upload for comparing two policy documents |
| `GET` | `/api/comparisons` | List all persisted comparison sessions |
| `GET` | `/api/comparisons/{id}` | Retrieve comparison summary and detailed changes |
| `DELETE` | `/api/comparisons/{id}` | Delete a stored comparison record |
| `PATCH` | `/api/changes/{id}/review` | Toggle human review verification status |
| `GET` | `/api/comparisons/{id}/report/pdf` | Download formal executive PDF report |
| `GET` | `/api/comparisons/{id}/report/csv` | Export structured changes in CSV format |
| `GET` | `/api/demo` | Execute and retrieve synthetic demo comparison |
| `GET` | `/api/evaluation` | Run evaluation benchmark and return empirical metrics |

---

## 12. Known Limitations & Future Scope

- **Image-Only PDFs**: Scanned documents without an embedded text layer are flagged by the parser; future iterations will integrate an OCR engine (such as Tesseract).
- **Tabular Data**: Multi-column nested tables in complex PDFs are serialized into structured paragraph blocks; future work will incorporate table-structure extraction.
- **Institutional Disclaimer**: PolicyDiff is designed as an intelligent assistive review tool. It does not replace official academic administrative councils, legal counsel, or authoritative institutional interpretation.
#   p o l i c y d i f f  
 