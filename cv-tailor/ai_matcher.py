"""
AI Matcher — generates a tailored CV using all 27 source resumes as equal sources.

For each experience entry, Gemini synthesizes the strongest bullets from across
the entire resume pool, filtered and enriched for the specific job description.

Rules:
  - All 27 resumes are equal sources — no single "primary" resume
  - Never copy phrases or grammar structures from the JD
  - Only use content that exists in the source resumes
  - ATS standards are built into the core generation prompt
"""

import os
import json
import pathlib
from google import genai
from dotenv import load_dotenv
from resume_loader import RESUMES

load_dotenv(pathlib.Path(__file__).parent.parent / ".env")

CLIENT = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

GENERATION_SYSTEM_PROMPT = """You are an expert Executive Career Strategist and Senior Technical Recruiter with 20 years of experience crafting high-impact CVs.

You have access to 27 versions of Melda's resume. Each version emphasizes different aspects of the same real work history. Your job is to synthesize the strongest, most JD-relevant content from across ALL 27 versions into a single tailored CV.

=== CORE APPROACH ===
For EVERY experience entry:
  1. Scan all 27 resume versions for bullets related to that role
  2. Select the 4-6 bullets that are most relevant to the JD themes
  3. Enrich each selected bullet by connecting the real achievement to the JD context
  4. Lead with the most impactful, JD-relevant aspect of each bullet
  5. Use strong, varied action verbs — never repeat the same verb twice in a section

=== SUMMARY SECTION ===
Write a 2-4 sentence professional summary that:
  - Opens with Melda's professional identity (seniority + key expertise)
  - Highlights 2-3 strengths most relevant to THIS specific role, drawn from real experience
  - Closes with a clear value proposition for this employer
  - Uses natural, confident language — not a list of buzzwords
  - Weaves in 1-2 key JD themes organically — in Melda's own voice

=== BULLET ENRICHMENT RULES ===
You SHOULD:
  - Reframe each bullet to lead with the most JD-relevant aspect
  - Add 1-2 words of context to make the connection to the JD explicit
    (e.g. original: "Analyzed financial data" → enriched: "Analyzed financial and economic data to surface ESG performance drivers aligned with stakeholder reporting requirements")
  - Ensure measurable results are prominent and exact (never change numbers)
  - Use varied, human-sounding language with strong action verbs

You MUST NEVER:
  - Copy full phrases or sentences verbatim from the JD
  - Mirror the JD's sentence structure or grammar patterns
  - Invent experiences, companies, tools, metrics, or titles not in any source resume
  - Change any company names, job titles, or dates
  - Keyword-stuff — every word must serve the sentence naturally

=== ATS STANDARDS (built into every CV) ===
  - Use standard section headers: EXPERIENCE, EDUCATION, VOLUNTEER WORK, SKILLS/ACTIVITIES
  - Include keywords from the JD naturally within bullets — never as a standalone list
  - Spell out acronyms on first use where relevant (e.g. "ESG (Environmental, Social, Governance)")
  - Keep bullets concise: 1-2 lines each, starting with a strong action verb
  - Quantify achievements wherever the source material supports it
  - Match seniority language in the JD (if JD says "senior", use senior-level framing)
  - Include all education entries — ATS systems scan for degree requirements
  - Skills section must list tools/technologies exactly as they appear in the JD (when genuinely present in source resumes)

=== CONTENT RULES ===
  - ONLY use information present in the provided source resumes
  - You MAY reorder bullets to lead with the most JD-relevant ones
  - You MAY omit bullets entirely irrelevant to the role
  - Always include all education entries and the volunteer section
  - For skills: only list skills/tools explicitly mentioned in the source resumes
  - Return ONLY valid JSON — no explanation, no markdown fences

=== OUTPUT FORMAT ===
Return a JSON object with this structure:
{
  "cv": {
    "personal": {"name": "", "location": "", "phone": "", "email": "", "linkedin": ""},
    "summary": "2-4 sentence professional summary tailored to this role",
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
  },
  "gap_report": {
    "covered": ["skill or requirement found in resumes and included"],
    "bridged": [
      {
        "jd_requirement": "exact term or skill from JD not found in resumes",
        "bridge": "what was emphasized instead and why it is a genuine proxy"
      }
    ]
  }
}

The gap_report is mandatory:
- "covered": list the key JD requirements (skills, tools, concepts) that ARE present in the resumes and were included
- "bridged": list JD requirements NOT found in the resumes — for each, explain what real experience was used as the closest honest proxy
- Be specific and honest — this report is shown to the candidate so they know exactly how their CV was positioned

Note: for roles with multiple positions at the same company, use this structure instead:
{
  "company": "", "location": "",
  "roles": [{"title": "", "start": "", "end": ""}],
  "bullets": [{"id": "1", "text": "..."}]
}"""


def tailor_cv(job_description: str, user_notes: str = "") -> dict:
    """
    Uses all 27 resumes as equal sources to generate a tailored CV.
    Returns a CV dict ready for cv_template.render_cv().
    """
    # Build the full resume pool — all 27 resumes in full
    resume_pool = "\n\n".join(
        f"--- {name} ---\n{text}"
        for name, text in RESUMES.items()
    )

    notes_section = f"\nUser's additional notes for this application:\n{user_notes}\n" if user_notes.strip() else ""

    prompt = f"""{GENERATION_SYSTEM_PROMPT}

=== RESUME POOL (all 27 versions — scan all for every experience entry) ===
{resume_pool}

=== JOB DESCRIPTION (relevance filter ONLY — never copy its language or sentence structure) ===
{job_description}
{notes_section}
=== YOUR TASK ===
For each experience entry in Melda's career history, scan all 27 resume versions and synthesize the 4-6 strongest, most JD-relevant bullets. Enrich each bullet to connect the real achievement to the JD context — in Melda's own voice, never mirroring the JD's phrasing.

Write the professional summary first. Then build each section.
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

    tailored = result.get("cv", result)
    gap_report = result.get("gap_report", {"covered": [], "bridged": []})
    return tailored, gap_report


def refine_cv(current_cv: dict, user_message: str) -> tuple[dict, str]:
    """
    Refine an already-tailored CV based on user feedback.
    Returns (updated_cv_dict, explanation_str).
    """
    # Build a compact resume pool for refinement context
    resume_pool = "\n\n".join(
        f"--- {name} ---\n{text[:800]}"
        for name, text in RESUMES.items()
    )

    prompt = f"""You are an expert Executive Career Strategist refining an existing tailored CV.

STRICT RULES:
- Only use content from the source resumes — do not fabricate anything
- Write in the candidate's authentic voice — do NOT copy phrasing from any job description
- Use varied, human-like language with strong action verbs
- Preserve all measurable results exactly
- Follow ATS best practices: strong action verbs, quantified achievements, natural keyword use

User's refinement request: "{user_message}"

Current tailored CV:
{json.dumps(current_cv, indent=2, ensure_ascii=False)}

Source resume pool (for reference — use when adding or changing content):
{resume_pool}

Apply the user's request and return a JSON object with TWO keys:
- "cv": the updated tailored CV (same structure as before)
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
    reply = result.get("reply", "CV updated successfully.")
    return updated_cv, reply
