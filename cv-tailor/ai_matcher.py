"""
AI Matcher — selects the best resume for a job description, then generates a tailored CV.

Two-step process:
  1. select_best_resume(): Gemini picks the most relevant resume from the 27 source files.
  2. tailor_cv(): Gemini generates a tailored CV using the selected resume as primary source,
     with other resumes available as supplementary content.

Rules:
  - Only use content that exists in the source resumes
  - Cannot invent skills, tools, titles, or experience
  - Can reorder, select, and lightly rephrase bullets for emphasis
"""

import os
import json
import pathlib
from google import genai
from dotenv import load_dotenv
from resume_loader import RESUMES

load_dotenv(pathlib.Path(__file__).parent.parent / ".env")

CLIENT = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

GENERATION_SYSTEM_PROMPT = """You are an expert Executive Career Strategist and Senior Technical Recruiter with 20 years of experience in high-stakes hiring. Your task is to synthesize a bespoke CV that is hyper-tailored to a specific Job Description while remaining 100% authentic to the candidate's actual history.

=== TWO-PASS APPROACH ===
PASS 1 — BUILD THE CANDIDATE PROFILE (do this internally before writing anything):
  - Read the PRIMARY resume carefully
  - Extract: the candidate's authentic voice, signature achievements, measurable results, and strongest skills
  - Note which experiences from SUPPLEMENTARY resumes add unique value
  - Identify the candidate's natural writing style and tone

PASS 2 — WRITE THE CV (using only what you extracted in Pass 1):
  - Use the candidate's OWN words and phrasing as the foundation
  - Use the Job Description ONLY as a relevance filter — to decide what to include or emphasize
  - Never use the JD as a writing template

=== LANGUAGE RULES — STRICTLY ENFORCED ===
1. NEVER copy phrases, sentences, or grammar structures from the Job Description
2. NEVER mirror the JD's vocabulary — rephrase everything in the candidate's authentic voice
3. Use varied, human-like language — avoid keyword stuffing and robotic phrasing
4. Write concise, impactful bullet points starting with strong action verbs
5. Preserve all measurable results exactly (numbers, percentages, scale)
6. Keep all company names, titles, and dates exactly as in the source resumes

=== CONTENT RULES ===
7. ONLY use information present in the provided source resumes — never invent or imply anything
8. PRIMARY resume is the foundation — use its structure, timeline, and core achievements
9. SUPPLEMENTARY resumes are an "Achievement Database" — pull from them only when clearly relevant
10. You MAY reorder bullets to lead with the most relevant ones
11. You MAY omit bullets or roles that are entirely irrelevant
12. Always include all education entries and the volunteer section
13. For skills: only list skills/tools explicitly in the source resumes
14. Return ONLY valid JSON — no explanation, no markdown fences

Output JSON structure — return an object with these top-level keys:
{
  "initial_match_pct": 72,
  "final_match_pct": 91,
  "cv": {
    "personal": {"name": "", "location": "", "phone": "", "email": "", "linkedin": ""},
    "experience": [
      {
        "company": "", "location": "",
        "title": "", "start": "", "end": "",
        "bullets": [{"id": "1", "text": "..."}]
      }
    ],
    "education": [
      {
        "institution": "", "location": "", "degree": "",
        "start": "", "end": "", "gpa": "",
        "highlights": [], "coursework": []
      }
    ],
    "volunteer": [
      {
        "organization": "", "location": "", "title": "", "start": "", "end": "",
        "bullets": [{"id": "1", "text": "..."}]
      }
    ],
    "skills": {
      "technical": [], "data": [], "analysis": [],
      "finance": [], "business": [], "certifications": [],
      "languages": [{"language": "", "level": ""}]
    }
  }
}

- "initial_match_pct": how well the selected resume matched the JD BEFORE tailoring (0-100)
- "final_match_pct": estimated match quality AFTER your tailoring work (0-100)

Note: for roles with multiple positions at the same company, use this structure instead:
{
  "company": "", "location": "",
  "roles": [{"title": "", "start": "", "end": ""}],
  "bullets": [{"id": "1", "text": "..."}]
}"""


def select_best_resume(job_description: str) -> tuple[str, str]:
    """
    Given a job description, returns (filename, full_text) of the best matching resume.
    """
    # Build a list of resume names + first 400 chars for context
    summaries = "\n\n".join(
        f"FILE: {name}\nPREVIEW:\n{text[:400]}"
        for name, text in RESUMES.items()
    )

    prompt = f"""You are helping select the best matching resume for a job application.

Here is the job description:
---
{job_description}
---

Here are the available resumes (filename + preview):
---
{summaries}
---

Select the ONE resume that best matches this job description based on the role type, required skills, and industry.
Return ONLY the exact filename (e.g. Melda_Resume_AI.docx), nothing else."""

    response = CLIENT.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    selected = response.text.strip().strip('"').strip("'")

    # Validate — fall back to first resume if something goes wrong
    if selected not in RESUMES:
        # Try partial match
        for name in RESUMES:
            if name.lower() in selected.lower() or selected.lower() in name.lower():
                selected = name
                break
        else:
            selected = list(RESUMES.keys())[0]

    return selected, RESUMES[selected]


def tailor_cv(job_description: str, user_notes: str = "") -> dict:
    """
    Selects the best resume, then generates a tailored CV dict ready for cv_template.render_cv().
    Also returns the selected resume filename for transparency.
    """
    selected_name, primary_text = select_best_resume(job_description)

    # Supplementary: other resumes truncated to avoid token overload
    supplementary = "\n\n".join(
        f"--- {name} (supplementary) ---\n{text[:600]}"
        for name, text in RESUMES.items()
        if name != selected_name
    )

    notes_section = f"\nUser's additional notes for this application:\n{user_notes}\n" if user_notes.strip() else ""

    prompt = f"""{GENERATION_SYSTEM_PROMPT}

=== SOURCE MATERIAL (candidate's authentic history — your primary source) ===

PRIMARY RESUME — Core structure, voice, and achievements:
---
{primary_text}
---

SUPPLEMENTARY ACHIEVEMENT DATABASE — pull from here only what adds unique relevance:
---
{supplementary}
---

=== RELEVANCE FILTER (use ONLY to decide what to include — do NOT copy its language) ===

Job Description:
---
{job_description}
---
{notes_section}
=== YOUR TASK ===
Execute the two-pass approach described above.
Write every bullet in the candidate's own voice.
Do not mirror the JD's phrasing.
Return the result as a JSON object following the output format above."""

    response = CLIENT.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {e}\n\nRaw output:\n{raw[:500]}")

    # Support both wrapped {"cv": {...}} and flat format
    tailored = result.get("cv", result)
    tailored["_selected_resume"] = selected_name
    tailored["_initial_match_pct"] = result.get("initial_match_pct")
    tailored["_final_match_pct"] = result.get("final_match_pct")
    return tailored


def check_ats(cv_data: dict, job_description: str) -> dict:
    """
    Run an ATS compatibility check on the generated CV against the job description.
    Returns {score, summary, suggestions}.
    """
    clean_cv = {k: v for k, v in cv_data.items() if not k.startswith("_")}

    prompt = f"""You are an ATS (Applicant Tracking System) expert analyst. Evaluate this CV against the job description for ATS compatibility.

CV:
{json.dumps(clean_cv, indent=2, ensure_ascii=False)}

Job Description:
{job_description}

Return a JSON object with this exact structure:
{{
  "score": 82,
  "summary": "One sentence overview of ATS readiness",
  "suggestions": [
    {{"priority": "high", "text": "Specific actionable suggestion"}},
    {{"priority": "medium", "text": "Specific actionable suggestion"}},
    {{"priority": "low", "text": "Specific actionable suggestion"}}
  ]
}}

Rules:
- score: 0-100 based on keyword alignment, section completeness, and formatting
- 3-5 specific, actionable suggestions referencing real gaps
- Do NOT suggest adding skills or experience not present in the CV
- priority high = missing critical keywords; medium = ordering/emphasis; low = nice-to-have
- Return ONLY valid JSON"""

    response = CLIENT.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"ATS check returned invalid JSON: {e}")


def refine_cv(current_cv: dict, user_message: str) -> tuple[dict, str]:
    """
    Refine an already-tailored CV based on user feedback.
    Returns (updated_cv_dict, explanation_str).
    """
    # Use the originally selected resume as primary reference
    selected_name = current_cv.get("_selected_resume", list(RESUMES.keys())[0])
    primary_text = RESUMES.get(selected_name, "")

    prompt = f"""You are an expert Executive Career Strategist refining an existing tailored CV.

STRICT RULES:
- Only use content from the source resume — do not fabricate anything
- Write in the candidate's authentic voice — do NOT copy phrasing from any job description
- Use varied, human-like language with strong action verbs
- Preserve all measurable results exactly

User's refinement request: "{user_message}"

Current tailored CV:
{json.dumps({k: v for k, v in current_cv.items() if k != "_selected_resume"}, indent=2, ensure_ascii=False)}

Primary source resume (for reference):
---
{primary_text}
---

Apply the user's request and return a JSON object with TWO keys:
- "cv": the updated tailored CV (same structure as before, without _selected_resume key)
- "reply": a short 1-2 sentence explanation of what you changed

Example: {{"cv": {{...}}, "reply": "I removed the Turkish Airlines section to keep the CV focused on research roles."}}"""

    response = CLIENT.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {e}\n\nRaw output:\n{raw[:500]}")

    updated_cv = result.get("cv", result)
    updated_cv["_selected_resume"] = selected_name
    reply = result.get("reply", "CV updated successfully.")
    return updated_cv, reply
