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

GENERATION_SYSTEM_PROMPT = """You are a professional CV tailoring assistant. Your job is to create a tailored CV for a specific job description using content from Melda Akan's source resumes.

STRICT RULES:
1. ONLY use information present in the provided source resumes. Do not add, invent, or imply any skills, tools, experience, or qualifications not explicitly listed.
2. The PRIMARY resume is your main source — use its structure, bullets, and emphasis as the foundation.
3. You MAY supplement with content from OTHER resumes if it's clearly relevant and not already in the primary.
4. You MAY reorder bullets to lead with the most relevant ones.
5. You MAY lightly rephrase a bullet to emphasize the most relevant aspect — facts, numbers, and scope must remain identical.
6. You MAY omit bullets or roles that are entirely irrelevant to the job.
7. Always include all education entries.
8. Always include the volunteer section if present.
9. For skills: only list skills/tools that appear in the source resumes.
10. Return ONLY valid JSON — no explanation, no markdown fences.

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

Job Description:
---
{job_description}
---
{notes_section}
PRIMARY RESUME (main source — use this as the foundation):
---
{primary_text}
---

SUPPLEMENTARY RESUMES (use only if clearly relevant content is missing from the primary):
---
{supplementary}
---

Generate the tailored CV as a JSON object following the output format rules above."""

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


def refine_cv(current_cv: dict, user_message: str) -> tuple[dict, str]:
    """
    Refine an already-tailored CV based on user feedback.
    Returns (updated_cv_dict, explanation_str).
    """
    # Use the originally selected resume as primary reference
    selected_name = current_cv.get("_selected_resume", list(RESUMES.keys())[0])
    primary_text = RESUMES.get(selected_name, "")

    prompt = f"""You are a professional CV tailoring assistant refining an existing tailored CV.

STRICT RULES: Same as before — only use content from the source resumes. Do not fabricate.

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
