# CV Tailor App — Project Plan

## What It Does
User pastes a job description + optional notes → AI picks the best matching resume from 27 tailored source files → generates a tailored `.docx` CV using it as the primary source → user can further refine via chat. **No fabrication — only real content from the source CVs.**

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
├── resume_loader.py    # Loads all 27 source .docx resumes at startup
├── ai_matcher.py       # Gemini API — select_best_resume(), tailor_cv(), refine_cv()
├── cv_template.py      # python-docx Word generation
├── master_cv.json      # Legacy — kept for reference, no longer used
├── templates/
│   └── index.html      # UI: JD form + optional notes + AI chat refinement panel
├── .env                # API key (never commit this)
└── requirements.txt

source-cvs/             # 27 .docx resumes (repo root, one level up from cv-tailor/)
├── Melda_Resume_AI.docx
├── Melda_Resume_FinanceSon.docx
├── Melda_Resume_Strategy.docx
└── ... (27 total)
```

---

## Source CVs
27 `.docx` files committed to the repo under `source-cvs/`. Each is a role-specific version of Melda's CV. `resume_loader.py` extracts text from all of them at startup.

| Resume | Focus |
|---|---|
| AI | AI / Analytics |
| Data, Data3, DataSurvey, DataSurveyEnerji | Data roles |
| FinanceSon | Finance |
| Strategy, Strategy2 | Strategy |
| IMF2, IMFRA, IMFSTAFI, Travel IMF | IMF / International orgs |
| IDB2 | Inter-American Development Bank |
| macro research, RA, RA2, ResearchAI, EVVRA | Research |
| Energy Policy, Energy Policy_FB | Energy policy |
| AirlineMarketing, Marketing, Partnership, Pricing | Marketing / commercial |
| Contract Management | Contract management |
| Event planning Volunteer | Events / volunteer |
| emre3 | General |

**Personal Info (consistent across all):**
- **Name:** Melda Akan — **Email:** melda_akan@gwu.edu — **Phone:** (571) 622 7403
- **Location:** Arlington, Virginia, USA — **LinkedIn:** linkedin.com/in/mkarasahin/

---

## AI Matching Logic (ai_matcher.py)

### `select_best_resume(job_description)` — resume selection
1. Sends Gemini: JD + filename + first 400 chars of all 27 resumes
2. Gemini returns the filename of the best match
3. Returns `(filename, full_text)` of the selected resume

### `tailor_cv(job_description, user_notes="")` — initial generation (returns match percentages)
1. Calls `select_best_resume()` first
2. Sends Gemini: JD + user notes + primary resume (full text) + other 26 resumes (first 600 chars each)
3. Primary resume is the main source; others are supplementary only
4. Returns structured JSON dict + `_selected_resume`, `_initial_match_pct`, `_final_match_pct` keys

### `refine_cv(current_cv, user_message)` — iterative chat refinement
1. Sends Gemini: user request + current CV JSON + primary resume full text
2. Returns `{"cv": {...}, "reply": "explanation of changes"}`
3. Updated CV stored in memory, new .docx generated; repeatable

**Rules enforced in all prompts:**
- Candidate voice comes first — JD is used only as a relevance filter, never as a writing template
- Two-pass approach: Pass 1 extracts candidate profile/voice; Pass 2 writes the CV
- NEVER copy phrases or grammar structures from the JD
- Only use content present in the source resumes — no fabrication
- Preserve measurable results exactly (numbers, percentages, scale)
- Varied, human-like language with strong action verbs — no keyword stuffing

---

## Build Order

- [x] Step 1: Create source CV pool (27 .docx files in source-cvs/)
- [x] Step 2: Build `cv_template.py` — python-docx Word output matching CV format
- [x] Step 3: Build `resume_loader.py` — loads all 27 resumes at startup
- [x] Step 4: Build `ai_matcher.py` — resume selection + tailoring + refinement
- [x] Step 5: Build `app.py` — Flask routes: /generate, /download, /refine
- [x] Step 6: Build `templates/index.html` — JD form + optional notes + AI chat panel
- [x] Step 7: Deployed to Render.com — tested and working end-to-end
- [x] Step 8: UI redesign + date alignment fix + match percentage display
- [ ] Step 9 (later): Add URL scraping for job links

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
