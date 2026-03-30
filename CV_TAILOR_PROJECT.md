# CV Tailor App — Project Plan

## What It Does
User pastes a job description → AI selects and emphasizes relevant content from Melda's real CV data → outputs a tailored, downloadable PDF. **No fabrication — only real content from the source CVs.**

---

## Tech Stack
- **Language:** Python
- **Web framework:** Flask
- **AI:** Google Gemini API — model: `gemini-2.5-flash`
- **Word generation:** python-docx
- **PDF reading (setup only):** pdfplumber

---

## Project Structure
```
cv-tailor/
├── app.py              # Flask server — routes: /generate, /refine, /download
├── master_cv.json      # Melda's real data pool (source of truth)
├── ai_matcher.py       # Gemini API — tailor_cv() + refine_cv()
├── cv_template.py      # python-docx Word generation
├── templates/
│   └── index.html      # UI: job description form + AI chat refinement panel
├── .env                # API key (never commit this)
└── requirements.txt
```

---

## Source CVs Location
`C:\Users\akanr\OneDrive\Masaüstü\melda\Job Apply\CVs\CV\`

| File | Focus |
|---|---|
| Melda_Resume_AI.pdf | AI / Analytics positions |
| Melda_Resume_E.pdf | Energy / Engineering positions |
| Melda_Resume_F.pdf | Finance positions |
| Melda_Resume_R.pdf | Research positions |

---

## Melda's Master Data (extracted from all 4 CVs)

### Personal Info
- **Name:** Melda Akan
- **Location:** Arlington, Virginia, USA
- **Phone:** (571) 622 7403
- **Email:** melda_akan@gwu.edu
- **LinkedIn:** https://www.linkedin.com/in/mkarasahin/

### Experience

**The George Washington University** — Graduate Research Assistant (Jan 2024 – Present / Jan 2026)
- Coordinated all student support activities for the Public Finance (Taxation) course across three semesters
- Compiled comprehensive report via literature review, cross-country policy comparison, and data collection to support faculty research on tax design
- Conducted detailed policy analysis on Australia's family tax benefit system (historical development, measurement frameworks, fiscal impact)
- Contributed to broader analysis of social protection policies and women's labor force participation
- Identifying and extracting severance-related variables across SIPP panels (1983–2024) to construct annual time series
- Conducting data cleaning and exploratory analysis in STATA

**The World Bank** — Summer Research and Analytics Consultant/Intern (May 2025 – Aug 2025)
- Led migration of 300+ reporting templates from Excel to AI-driven platform, reducing processing time by 40%
- Developed and delivered MD&A content and financial statement disclosures
- Produced analytical reports strengthening accountability and transparency
- Analyzed and synthesized financial and economic data to identify performance drivers
- Facilitated digital transformation of financial data management and visualization systems
- Identified key financial trends and performance drivers, incorporating market insights

**Turkish Airlines** — Senior Global Corporate Account Manager (May 2019 – Mar 2022) / Global Corporate Account Manager (May 2016 – May 2019)
- Launched SME-focused product coordinating local sales teams and IT; gained 10,000 new clients in 3 months
- Designed product including marketing strategy, target analysis and policy formulation
- Directed project using PMP methodologies (time and team management)
- Led contract negotiations with global TMCs and global clients
- Added over 26 new markets to portfolio in 6 years; handled relations for 35+ markets
- Developed dashboards analyzing clients' travel policies and revenue potential
- Increased revenue on targeted O&Ds by over 20% for 3 consecutive years without increasing incentive cost
- Managed relationships with Fortune 500 companies: Google, Rolls-Royce, Mastercard
- Managed $600k/year marketing budget for corporate clients and TMCs globally

**Siemens** — Marketing & Proposal Manager / Technical Proposal Manager EMEA (May 2013 – May 2016)
- Organized complex bid activities; prepared 25+ solution proposals for EMEA and Turkish smart grid clients
- Represented technical, commercial and financial aspects during negotiations (Saudi Aramco, TANAP, LEPCO)
- Coordinated with legal, tax, and financing experts for comprehensive bids
- Defined and investigated market needs, trends, and portfolio; contributed to global marketing portfolio
- Collaborated with regional teams to design tailored energy and digital grid solutions
- Developed standardized bid templates and knowledge resources for regional teams
- Integrated smart grid, digitalization, and secure transmission features into proposals

### Education

**GWU — Applied Economics (MS)** | Jan 2024 – Dec 2025 (Expected) | GPA: 4.00/4.00
- Global Leaders Fellowship Awardee
- Coursework: Applied Financial Analysis, Quantitative Risk Management, Time Series, Applied Macroeconomics, Statistics, Econometrics, Applied Microeconomics, Finance 360, International Banking, Economic Development, Development Economics (PhD Course)
- International Business Ethics and Sustainability Case Competition Winner (2025)
- Dean's High Honor List with 4.00 GPA
- Paper: Economic Analysis of Corporate Expansions and Housing Prices: Amazon HQ2 Case in Arlington

**GWU — International Exchange Student, Economics (BA)** | Aug 2022 – May 2023 | GPA: 3.70/4.00
- International Exchange Student Scholarship (Full Tuition)
- Coursework: Portfolio Management, Financial Economics, Econometrics, Financial Management and Markets, Economic Development, Public Finance and Taxation, Entrepreneurial Leadership
- NWC (New Venture Competition) Semi-finalist

**Bogazici University — Economics (BA)** | Aug 2020 – Dec 2024 | GPA: 3.34/4.00
- Ranked as top university / top economics program in Turkey
- Dean's High Honor List (4 semesters); Graduated with Honors
- Coursework: Computing for Economists (R), Chinese I-II, Macroeconomics I-II, Management Simulation, Microeconomics I-II, Statistics I-II, Game Theory, Calculus I-II, International Economics

**Yildiz Technical University — Innovation, Administration and Entrepreneurship (MBA)** | Jan 2016 – Jul 2018 | GPA: 3.93/4.00
- Dean's list (2016 & 2017); Graduated with High Honors
- Thesis: The Moderating Role of Introversion–Extroversion in the Relationship Between Transformational Leadership and Individual Creativity Across Corporations and Startups
- Coursework: Project Management, Strategic Management, Cultural Differences in Business

**Istanbul Technical University — Electrical & Energy Engineering (BS)** | Sep 2008 – Jun 2013 | GPA: 3.16/4.00
- Ranked top technical university in Istanbul; top electrical engineering department in Turkey
- Siemens Future Professionals Scholarship, Finansbank Merit Based Scholarship
- Coursework: Power Systems Modelling and Analysis, Electrical Distribution, Energy Market Pricing, Linear Algebra, Differential Equations, Numerical Methods
- Thesis: Modeling of the dynamic behavior of squirrel-cage induction motors

### Volunteer Work

**Siemens Diversity Club** — Team Leader, Disabled Employee Committee (Sep 2014 – Sep 2015)
- Led volunteer team to improve working conditions for disabled employees; impacted 100+ employees
- Launched project enabling disabled candidates to apply to job ads on company website

### Skills

**Technical:** R, STATA, Python, Microsoft Office Tools (advanced), VBA, SQL, Power BI
**Data:** Processing, cleaning, transforming data; working with large datasets
**Analysis:** Statistical analysis, econometric modeling (OLS, panel data), regression analysis, forecasting, time series analysis, financial modeling and valuation (DCF, M&A analysis)
**Finance:** Financial analysis and reporting, financial statement disclosures, MD&A
**Other:** Competitive analysis, risk management, data management, stakeholder engagement, proposal management, risk assessment, financial reporting, working with survey data

**Certifications:**
- McKinsey Forward Program (2024)
- Build Project – Building 5 Year Financial Plan (2024)
- Build Project – Enterprise Valuation for M&A (2024)
- Draper University Hero Leadership Program (2023)
- Communication for Economists (2025)

**Languages:** Turkish (Native), English (Fluent), Chinese (Beginner)

---

## CV Format / Layout (to replicate in ReportLab)

Based on the PDFs, the format is:
- Clean single-column layout
- **Name** large at top, centered or left-aligned
- Contact info line below name
- Section headers: ALL CAPS, bold, with a horizontal line separator
- Bullet points with `•` for experience details
- Sub-bullets for nested items (some CVs use this)
- Consistent font throughout (likely Calibri or similar sans-serif)
- Margins: standard ~1 inch
- Single page preferred (content selection should target 1 page)

> TODO: Measure exact font sizes, margins, spacing from PDFs when building cv_template.py

---

## AI Matching Logic (ai_matcher.py)

### `tailor_cv(job_description)` — initial generation
1. Send Gemini: job description + full master_cv.json
2. Gemini selects which bullet points are most relevant
3. May reword/reorder bullets but CANNOT invent new skills or experience
4. Returns structured JSON → rendered to .docx

### `refine_cv(current_cv, user_message)` — iterative chat refinement
1. Send Gemini: current tailored CV + user's request + master_cv.json
2. Returns `{"cv": {...}, "reply": "explanation of changes"}`
3. Updated CV stored in memory, new .docx generated
4. User can refine repeatedly; each version downloadable

**Rules enforced in all prompts:**
- Only use skills/experience present in master data
- Do not add tools, software, or skills not listed
- Adjust emphasis and ordering, not facts
- Keep all dates, titles, and institutions exactly as provided

---

## Build Order

- [x] Step 1: Create `master_cv.json` from extracted data
- [x] Step 2: Build `cv_template.py` — python-docx Word output matching CV format
- [x] Step 3: Build `ai_matcher.py` — Gemini API with strict prompt (tailor + refine)
- [x] Step 4: Build `app.py` — Flask routes: /generate, /download, /refine
- [x] Step 5: Build `templates/index.html` — job form + AI chat refinement panel
- [x] Step 6: Deployed to Render.com — tested and working end-to-end
- [ ] Step 7 (later): Add URL scraping for job links

---

## Setup Notes (Local)

- API key goes in `.env` file as `GEMINI_API_KEY=...`
- **Never commit `.env` to git**
- Add `.env` to `.gitignore`
- Install: `pip install flask gunicorn python-docx pdfplumber python-dotenv google-genai`
- Run locally: `cd cv-tailor && python app.py` → http://localhost:5000

---

## Deployment (Render.com)

- Platform: **Render.com** (free tier, always-on)
- Repo: `serhose/Claude-Test`, branch: `master`
- Root directory is the repo root (render.yaml ignored by Render UI)
- **Build command:** `pip install -r cv-tailor/requirements.txt`
- **Start command:** `cd cv-tailor && gunicorn app:app --timeout 120 --workers 1`
- **Environment variable:** `GEMINI_API_KEY` set in Render dashboard → Environment tab
- Python version pinned to 3.11.9 via `.python-version` file
- Timeout set to 120s (Gemini API calls can take ~30-60s)
- Auto-deploys on every push to `master`

---

## Important Reminders

- The app is for one user (Melda). No auth needed.
- Output is `.docx` (Word), downloadable directly from the browser.
- In-memory state: CV data resets on every Render restart (free tier spins down after inactivity).
