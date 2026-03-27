"""
AI Matcher — uses Google Gemini to select and tailor CV content for a job description.
Rules:
  - Only uses content that exists in master_cv.json
  - Cannot invent skills, tools, titles, or experience
  - Can reorder, select, and lightly rephrase bullets for emphasis
  - Returns a structured dict ready for cv_template.render_cv()
"""

import os
import json
import pathlib
from google import genai
from dotenv import load_dotenv

load_dotenv(pathlib.Path(__file__).parent.parent / ".env")

CLIENT = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MASTER_CV = json.loads(
    (pathlib.Path(__file__).parent / "master_cv.json").read_text(encoding="utf-8")
)

SYSTEM_PROMPT = """You are a professional CV tailoring assistant. Your job is to select and adapt content from a candidate's master CV to best match a given job description.

STRICT RULES — you must follow these without exception:
1. ONLY use information present in the master CV. Do not add, invent, or imply any skills, tools, software, experience, certifications, or qualifications that are not explicitly listed.
2. Do NOT add any technology, software, or tool (e.g. Bloomberg, SAP, Salesforce) unless it appears in the master CV's skills section.
3. You MAY reorder bullet points within a role to lead with the most relevant ones.
4. You MAY lightly rephrase a bullet point to emphasize the most relevant aspect — but the facts, numbers, and scope must remain identical.
5. You MAY omit bullet points, roles, or education entries that are entirely irrelevant.
6. Always include all education entries — they are always relevant.
7. Always include the volunteer section.
8. For skills: only list skills/tools that appear in the master CV. Select the most relevant subset.
9. Return ONLY valid JSON, no explanation, no markdown code fences.

Output format: Return a JSON object with the exact same structure as the master CV (personal, experience, education, volunteer, skills), but containing only the selected/adapted content. Each bullet in experience and volunteer must be an object with "id" and "text" fields."""


def tailor_cv(job_description: str) -> dict:
    """
    Given a job description string, returns a tailored CV dict
    ready to be passed to cv_template.render_cv().
    """
    prompt = f"""{SYSTEM_PROMPT}

Here is the job description:

---
{job_description}
---

Here is the master CV (source of truth — do not use anything outside this):

{json.dumps(MASTER_CV, indent=2, ensure_ascii=False)}

Return the tailored CV as a JSON object following the output format rules."""

    response = CLIENT.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
    )

    raw = response.text.strip()

    # Strip markdown code fences if model included them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        tailored = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {e}\n\nRaw output:\n{raw}")

    tailored = _safety_filter(tailored)
    return tailored


def _safety_filter(tailored: dict) -> dict:
    """Remove any skill/tool that isn't in the master CV's skills.technical list."""
    allowed_technical = set(s.lower() for s in MASTER_CV["skills"]["technical"])

    if "skills" in tailored and "technical" in tailored["skills"]:
        tailored["skills"]["technical"] = [
            s for s in tailored["skills"]["technical"]
            if s.lower() in allowed_technical
        ]

    return tailored


if __name__ == "__main__":
    sample_jd = """
    We are looking for a Financial Analyst to join our team.

    Responsibilities:
    - Conduct financial modeling and valuation analysis
    - Prepare financial reports and dashboards
    - Analyze market trends and present findings to management
    - Support M&A due diligence processes

    Requirements:
    - Bachelor's degree in Finance, Economics, or related field
    - 2+ years of experience in financial analysis
    - Strong Excel and data analysis skills
    - Knowledge of financial statements and accounting principles
    - Experience with Power BI or similar visualization tools
    """

    print("Calling Gemini API...")
    result = tailor_cv(sample_jd)
    print("Success!")
    out = pathlib.Path("tailored_test.json")
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Written to {out}")
