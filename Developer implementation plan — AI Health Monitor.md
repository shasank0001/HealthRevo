# **Developer Implementation Plan — AI Health Monitoring & Prescription Analyzer (Hackathon MVP)**

This document outlines a complete, developer-friendly plan for building the MVP. It covers architecture, data model, API contracts, backend modules, frontend components, integrations, logic, testing, deployment, and a demo checklist.

### **1\. High-level architecture**

* **Frontend**: React (create-react-app / Vite) \+ component library (Material UI / Chakra)  
* **Backend**: FastAPI (ASGI) \+ Pydantic models \+ dependency injection  
* **DB**: PostgreSQL (SQLite acceptable for quick local hackathon demo)  
* **OCR**: Tesseract via python-pytesseract (English-only)  
* **Drug knowledge**: DrugBank preprocessed into a local table / JSON \+ your rule-based engine  
* **Chatbot**: GPT API (OpenAI or other provider) proxied through backend for prompt control  
* **Background jobs**: simple in-process scheduling (APScheduler) or use Celery/RQ if preferred  
* **Deployment**: Docker \+ docker-compose (Postgres \+ backend \+ frontend)

### **2\. Data model (SQL \+ explanation)**

Below are the main tables and key fields. Use PostgreSQL types.

\-- users: both patients and doctors  
CREATE TABLE users (  
  id SERIAL PRIMARY KEY,  
  email VARCHAR(255) UNIQUE NOT NULL,  
  password\_hash VARCHAR(255) NOT NULL,  
  full\_name VARCHAR(255),  
  role VARCHAR(20) NOT NULL CHECK (role IN ('patient','doctor','admin')),  
  created\_at TIMESTAMP WITH TIME ZONE DEFAULT now()  
);

\-- patients: profile details (separate from users for flexibility)  
CREATE TABLE patients (  
  id SERIAL PRIMARY KEY,  
  user\_id INTEGER REFERENCES users(id) UNIQUE,  
  dob DATE,  
  gender VARCHAR(20),  
  phone VARCHAR(30),  
  blood\_group VARCHAR(10),  
  created\_at TIMESTAMP WITH TIME ZONE DEFAULT now()  
);

\-- vitals: daily manual entries  
CREATE TABLE vitals (  
  id SERIAL PRIMARY KEY,  
  patient\_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,  
  recorded\_at TIMESTAMP WITH TIME ZONE NOT NULL,  
  systolic INTEGER,  
  diastolic INTEGER,  
  heart\_rate INTEGER,  
  temperature NUMERIC(4,2),  
  blood\_glucose NUMERIC(6,2),  
  oxygen\_saturation INTEGER,  
  notes TEXT,  
  created\_at TIMESTAMP WITH TIME ZONE DEFAULT now()  
);

\-- prescriptions: OCRed text \+ parsed meds JSON  
CREATE TABLE prescriptions (  
  id SERIAL PRIMARY KEY,  
  patient\_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,  
  uploaded\_by INTEGER REFERENCES users(id),  
  uploaded\_at TIMESTAMP WITH TIME ZONE DEFAULT now(),  
  ocr\_text TEXT,                 \-- raw OCR output  
  parsed\_medications JSONB,      \-- \[{"name": "...", "dose": "...", "freq":"..."}\]  
  flags JSONB DEFAULT '\[\]'::jsonb,-- e.g. interactions/warnings  
  original\_filename VARCHAR(255)  
);

\-- drug\_interactions: optional preprocessed DrugBank entries  
CREATE TABLE drug\_interactions (  
  id SERIAL PRIMARY KEY,  
  drug\_a VARCHAR(255),  
  drug\_b VARCHAR(255),  
  severity VARCHAR(20),  \-- minor/moderate/major  
  description TEXT  
);

\-- risk\_scores: store computed scores & reasons  
CREATE TABLE risk\_scores (  
  id SERIAL PRIMARY KEY,  
  patient\_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,  
  computed\_at TIMESTAMP WITH TIME ZONE DEFAULT now(),  
  risk\_type VARCHAR(50),  \-- "diabetes","hypertension","heart\_disease"  
  score NUMERIC(5,2),     \-- 0-100  
  drivers JSONB,          \-- {"bp": "high", "glucose": "borderline"}  
  method VARCHAR(50)      \-- "heuristic-v1"  
);

\-- alerts: anomalies and escalation status  
CREATE TABLE alerts (  
  id SERIAL PRIMARY KEY,  
  patient\_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,  
  generated\_at TIMESTAMP WITH TIME ZONE DEFAULT now(),  
  severity VARCHAR(20),  \-- mild/serious/urgent  
  type VARCHAR(50),      \-- "anomaly","drug\_interaction"  
  message TEXT,  
  acknowledged BOOLEAN DEFAULT FALSE,  
  metadata JSONB  
);

\-- lifestyle logs (med adherence, exercise, sleep)  
CREATE TABLE lifestyle\_logs (  
  id SERIAL PRIMARY KEY,  
  patient\_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,  
  log\_date DATE,  
  medication\_taken BOOLEAN,  
  steps INTEGER,  
  sleep\_hours NUMERIC(4,2),  
  notes TEXT  
);

**Indexes & constraints**: add indexes on vitals(patient\_id, recorded\_at), alerts(patient\_id, generated\_at), and risk\_scores(patient\_id, computed\_at) for fast queries.

### **3\. API contract (core endpoints)**

Use JWT auth. Doctors have role='doctor'. Patients can only access their own patient record.

**Auth**

* POST /auth/signup — {email, password, full\_name, role (patient/doctor)} \-\> 201  
* POST /auth/login — {email, password} \-\> {access\_token, token\_type}

**Patients & records**

* GET /patients/ — doctor only \-\> list patients (paginated)  
* GET /patients/{patient\_id} — doctor or owner \-\> patient profile  
* POST /patients/{patient\_id}/vitals — patient user \-\> add vitals entry  
  * payload: {recorded\_at, systolic, diastolic, heart\_rate, temperature, blood\_glucose, oxygen\_saturation, notes}  
* GET /patients/{patient\_id}/vitals?from=\&to= — returns list

**Prescriptions (OCR flow)**

* POST /patients/{patient\_id}/prescription/upload — multipart file upload (PDF/JPG)  
  * backend: OCR \-\> parse \-\> store ocr\_text & parsed\_medications \-\> run drug checker \-\> create prescriptions \+ alerts if needed  
* GET /patients/{patient\_id}/prescriptions — list  
* GET /patients/{patient\_id}/prescriptions/{id} — details, parsed meds, flags

**Risk & alerts**

* POST /patients/{patient\_id}/compute\_risk — recompute heuristics (can be called after vitals insert)  
* GET /patients/{patient\_id}/risk\_scores — list  
* GET /alerts — doctor: all recent alerts (query by severity)  
* POST /alerts/{id}/acknowledge — mark as acknowledged

**Drug checker (manual)**

* POST /drug-check — body: {patient\_id?, medications: \[{name, dose, freq}\]} \-\> returns interactions \+ severity

**Chatbot**

* POST /patients/{patient\_id}/chat — body: {message, context?}  
  * backend composes system prompt with latest vitals/risk summary, forwards to GPT API, returns response (and stores chat logs if desired)

**Export**

* GET /patients/{patient\_id}/export?type=pdf|csv\&from=\&to= — doctor only: export consolidated record

### **4\. Backend modules & responsibilities**

* **auth module**: JWT token issuance, role checks, password hashing (bcrypt)  
* **models module**: Pydantic models for validation  
* **db module**: SQLAlchemy / async SQLAlchemy models & CRUD functions  
* **vitals\_service**: insert, validate ranges, trigger risk compute and anomaly check  
* **risk\_service**: heuristic rules engine to compute scores per risk\_type  
* **alert\_service**: evaluate alert severity and persist alerts  
* **ocr\_service**: file preprocessing → pytesseract OCR → return text  
* **prescription\_service**: parse OCR text → call drug\_checker → persist  
* **drug\_checker**: wrapper for your prebuilt rule engine using DrugBank  
* **chat\_service**: prompt templating, call GPT API, session context  
* **export\_service**: generate CSV/PDF for exports  
* **scheduler**: light scheduler to recompute weekly stats or expire unacknowledged alerts (APScheduler or cron)

### **5\. Heuristics (risk scoring & anomaly detection)**

**Example hypertension heuristic**

* Compute average of last 7 days systolic & diastolic (if entries exist).  
* Score calculation (example approach):  
  * score \= min(100, (avg\_systolic \- 120\) \* 1.2 \+ (avg\_diastolic \- 80\) \* 1.0) clipped 0..100.  
* Drivers: if systolic elevates frequently, add driver "recent\_systolic": true.

**Diabetes heuristic (simplified)**

* Use blood\_glucose values:  
  * fasting glucose \> 126 \-\> high risk  
  * random glucose \> 200 \-\> high risk  
* Score mapping: map thresholds to 0..100.

**Anomaly detection**

* Define window \= 7 days. For new vitals entry:  
  * If current value deviates \> 20% from window mean → generate mild alert.  
  * If absolute reading crosses medical emergency threshold → urgent (e.g., systolic \> 180 or O2 \< 88\) → urgent.

Provide these heuristic thresholds as a config file (YAML) so the team can tweak during demo.

### **6\. OCR & prescription parsing details**

* **Preprocess image/PDF**: convert PDF pages to images (pdf2image), grayscale, denoise, increase contrast.  
* Use pytesseract.image\_to\_string(image, lang='eng').  
* **Regex-based parsing**:  
  * Look for patterns like (\[A-Za-z0-9\\-\\s\]+)\\s+(\\d+\\.?\\d\*\\s\*(mg|g|mcg|IU)?)\\s\*(once daily|twice daily|bd|tds|q\\d+h)?  
* Use fuzzy matching (fuzzywuzzy / rapidfuzz) to map OCR drug names to DrugBank canonical names (handle OCR mistakes).  
* Run matched meds through your rule-based DrugBank engine:  
  * produce flags: interactions and unsafe dose warnings (store in prescriptions.flags and create alerts if severity \>= moderate).

**Note**: Since OCR can be flaky, show parsed result on UI for quick human review/edit before finalizing.

### **7\. DrugBank integration & rule-based checker**

* Preprocess DrugBank into a drug\_interactions table (CSV \-\> SQL load).  
* drug\_checker accepts an array of meds and:  
  * normalizes names using fuzzy matching,  
  * queries pairwise interactions,  
  * computes cumulative risk (e.g., multiple drugs with QT prolongation),  
  * returns severity per pair and an overall recommendation (monitoring plan or alternative).  
* Add an allowlist/override system (doctor can mark interaction as accepted with monitoring instructions).

### **8\. Chatbot integration (GPT API)**

* **Backend role**: protect the API key, control the context, and filter content.  
* **Prompt design (system prompt example)**:

You are a medical assistant helping patients understand prescriptions and vitals. Use plain, non-judgmental language. The question must not replace a doctor's advice.

Patient summary: {name}, Age: {age}, Latest vitals: {vitals\_summary}, Latest risk scores: {risk\_summary}.

Conversation:

* Always attach a short summary of the patient (no raw PHI beyond mock POC) and the latest risk drivers.  
* Limit the amount of personal data sent to the GPT API to what's necessary for the single response.  
* Save chat logs (optional). Rate-limit requests to API.

### **9\. Frontend structure & components**

**Pages / Routes**:

* /login, /signup  
* /patient/dashboard — vitals entry widget, today's summary, risk badges, quick chat  
* /patient/records — timeline of vitals & prescriptions, lifestyle logs  
* /patient/upload-prescription — file upload \+ parsed preview \+ confirm  
* /doctor/dashboard — patient list with filters: High Risk, New Alerts, Unsafe Prescriptions  
* /doctor/patient/{id} — tabs: Overview, Vitals (charts), Prescriptions, Alerts, Lifestyle, Export

**Key components**:

* VitalsForm — daily entry (validate ranges)  
* RiskBadge — color-coded (green/yellow/red)  
* TimeSeriesChart — plot vitals with Chart.js (systolic/diastolic on same chart)  
* AlertsPanel — list with severity icons and actions  
* PrescriptionUploader — file drop \+ OCR progress \+ parsed edit UI  
* ChatWidget — conversation UI with GPT responses  
* PatientRecordsViewer — consolidated view with export button

**UX notes**:

* On prescription upload, show editable parsed meds before final save.  
* On vitals save, show immediate risk badge update and highlight if an alert is generated.

### **10\. Auth & Role-based access**

* Use JWT tokens with role in claims.  
* FastAPI dependencies to enforce @depends(get\_current\_user) and @depends(require\_role('doctor')).  
* Patient endpoints validate current\_user.id \== patient.user\_id except where role \== doctor.

### **11\. Background jobs & event triggers**

**On-write triggers (synchronous)**:

* After vitals insert: compute risk (call risk\_service) and run anomaly detection → store risk\_scores and alerts.  
* After prescription upload: run drug\_checker → create alerts if needed.

**Scheduled jobs (simple scheduler)**:

* Daily summary generation (optional).  
* Recompute weekly risk for patients with sparse data.  
* Escalation job: check unacknowledged urgent alerts and mark for follow-up (create summary for doctor).

Use APScheduler for in-process scheduling during hackathon; move to Celery if you need out-of-process workers.

### **12\. Testing**

* **Unit tests** for:  
  * heuristics functions for risk computations (edge cases)  
  * alert generation logic (threshold boundaries)  
  * prescription parser with example OCR outputs  
  * drug\_checker with sample drug pairs  
* **Integration tests**:  
  * full flow: upload file \-\> OCR \-\> parse \-\> store \-\> doctor sees alert  
  * auth \+ role checks for endpoints  
* **Frontend**: basic React component tests for form validation and mocking API responses

### **13\. Deployment & devops**

* Dockerize backend and frontend; docker-compose with Postgres. Example services:  
  * db (postgres)  
  * backend (fastapi \+ uvicorn)  
  * frontend (nginx serve or dev server)  
* **Environment variables**:  
  * DATABASE\_URL, JWT\_SECRET, GPT\_API\_KEY, DRUGBANK\_PATH  
* **Logging**: simple structured JSON logs for backend  
* **Local dev**: provide seed script to create mock users \+ sample vitals/prescriptions  
* **For demo**: either run locally or deploy backend to Render/Heroku and frontend to Vercel with env vars.

### **14\. Security & privacy (POC-level)**

* Use HTTPS in production (demo via deployed url or local tunnel).  
* Hash passwords (bcrypt), never store plain text.  
* Validate & sanitize OCR output before saving/display.  
* Limit exposure to GPT API (no wide PHI dumps).  
* Add CORS policy that allows frontend origin only.  
* Basic rate limiting on chatbot endpoint.

### **15\. Monitoring & observability**

* Simple health endpoint GET /healthz.  
* On backend, instrument counters for:  
  * OCR failures  
  * alerts generated by severity  
  * chatbot requests  
* Surface these in a small admin page or logs.

### **16\. Demo script & acceptance criteria**

Create a short demo script that shows these flows:

1. Login as patient1 → Enter daily vitals for a few days (or load seeded data).  
2. Save vitals → show updated risk badge and chart.  
3. Upload a sample prescription PDF → show OCR stage → show parsed meds → show generated interaction alert (if any).  
4. Login as doctor → open doctor dashboard → see patient flagged under "High Risk" or "New Alerts" → open patient's consolidated records → export CSV/PDF.  
5. Use Chatbot from patient page to ask “Is this drug safe with my BP medicine?” and display GPT response referencing risk summary.

**Acceptance criteria for MVP**:

* Manual vitals entry stores data and updates risk scores.  
* OCR \> parser works reliably for supplied English demo prescriptions and allows user correction.  
* Drug checker returns interactions and creates alerts.  
* Doctor can see consolidated patient records and alerts.  
* Chatbot returns context-aware responses with sanitized patient info.

### **17\. Developer checklist (concrete tasks)**

Group by priority for hackathon MVP:

**Core (must-have for demo)**

* \[ \] Project scaffolding: FastAPI \+ React \+ docker-compose \+ Postgres  
* \[ \] Auth (signup/login) \+ roles  
* \[ \] DB schema \+ migrations (Alembic)  
* \[ \] Vitals CRUD \+ frontend form \+ charts  
* \[ \] Heuristic risk engine \+ store risk\_scores  
* \[ \] Alert generation on vitals insert  
* \[ \] Prescription upload (file input) \+ OCR (tesseract) \+ parsed preview \+ save  
* \[ \] Integrate existing rule-based drug checker with DrugBank → create alerts  
* \[ \] Doctor dashboard: patient list \+ patient consolidated view  
* \[ \] Chat endpoint that proxies to GPT API \+ frontend chat widget  
* \[ \] Seed script: create mock users and demo data

**Enhancements (if time permits)**

* \[ \] Export PDF/CSV  
* \[ \] Browser push notifications (service worker)  
* \[ \] PDF-to-image preprocessing improvements  
* \[ \] Simple analytics on doctor dashboard  
* \[ \] Tests and CI pipeline

### **18\. Example pseudocode snippets**

**risk compute (simplified)**

def compute\_hypertension\_score(vitals\_list):  
    if not vitals\_list: return 0, {}  
    avg\_sys \= mean(\[v.systolic for v in vitals\_list if v.systolic\])  
    avg\_dia \= mean(\[v.diastolic for v in vitals\_list if v.diastolic\])  
    score \= max(0, (avg\_sys \- 120\) \* 1.2 \+ (avg\_dia \- 80\) \* 1.0)  
    score \= min(score, 100\)  
    drivers \= {"avg\_systolic": avg\_sys, "avg\_diastolic": avg\_dia}  
    return round(score,2), drivers

**alert trigger (simplified)**

def check\_anomaly(patient\_id, new\_vital):  
    window \= get\_vitals(patient\_id, days=7)  
    mean\_hr \= mean(\[v.heart\_rate for v in window\]) or 0  
    if mean\_hr and abs(new\_vital.heart\_rate \- mean\_hr)/mean\_hr \> 0.2:  
        create\_alert(patient\_id, severity="mild", type="anomaly", message="Heart rate changed \>20%")  
    if new\_vital.systolic and new\_vital.systolic \> 180:  
        create\_alert(... severity="urgent" ...)

### **19\. Backlog / future improvements**

* Replace heuristics with small ML models trained on public datasets (Pima Indians, MIMIC-lite) once POC validated.  
* Two-way integration with wearable streams (BLE or simulated).  
* Doctor collaboration: notes, in-app messaging, shared task lists.  
* Audit logs for regulatory traceability.  
* Fine-grained patient consent management (data sharing toggles).

### **20\. Final notes & deliverables to produce now**

* Provide this plan to devs; then produce:  
  * README with setup & demo script  
  * seed script to create mock users \+ data  
  * OpenAPI docs (FastAPI auto-generates /docs)  
  * Sample prescription PDF(s) to test OCR parsing