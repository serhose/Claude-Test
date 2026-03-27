"""
CV PDF Template — Melda Akan
Replicates the exact format of the source CVs using ReportLab.
"""

import io
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

# ── Font registration ─────────────────────────────────────────────────────────
pdfmetrics.registerFont(TTFont("Calibri",       "C:/Windows/Fonts/calibri.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-Bold",  "C:/Windows/Fonts/calibrib.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-Italic","C:/Windows/Fonts/calibrii.ttf"))

# ── Layout constants (points) ─────────────────────────────────────────────────
PAGE_W        = 612
PAGE_H        = 792
MARGIN_LEFT   = 36
MARGIN_RIGHT  = 36
MARGIN_TOP    = 39
MARGIN_BOTTOM = 40
CONTENT_W     = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT   # 540

BULLET_X      = MARGIN_LEFT       # 36  — bullet glyph
BULLET_TEXT_X = MARGIN_LEFT + 18  # 54  — bullet text start

# ── Font sizes ────────────────────────────────────────────────────────────────
SIZE_NAME          = 17
SIZE_CONTACT       = 11
SIZE_SECTION       = 12   # section header text (all bold caps)
SIZE_BODY          = 11

LINE_HEIGHT_NAME    = 20
LINE_HEIGHT_CONTACT = 13
LINE_HEIGHT_SECTION = 14
LINE_HEIGHT_BODY    = 13.5

SECTION_GAP_BEFORE = 7
SECTION_GAP_AFTER  = 5
ENTRY_GAP          = 5


def _wrap(c_obj, text, font, size, max_w):
    return simpleSplit(text, font, size, max_w)


class CVCanvas:
    """Stateful drawing helper that tracks Y and handles page breaks."""

    def __init__(self):
        self.buf = io.BytesIO()
        self.c   = canvas.Canvas(self.buf, pagesize=(PAGE_W, PAGE_H))
        self.y   = PAGE_H - MARGIN_TOP

    def _move(self, delta):
        self.y -= delta

    def _new_page(self):
        self.c.showPage()
        self.y = PAGE_H - MARGIN_TOP

    def _check_break(self, needed=LINE_HEIGHT_BODY):
        """Start a new page if there isn't enough room for `needed` points."""
        if self.y - needed < MARGIN_BOTTOM:
            self._new_page()

    # ── Primitives ────────────────────────────────────────────────────────────

    def _text(self, x, y, text, font, size):
        self.c.setFont(font, size)
        self.c.setFillColorRGB(0, 0, 0)
        self.c.drawString(x, y, text)

    def _text_right(self, x_right, y, text, font, size):
        self.c.setFont(font, size)
        self.c.setFillColorRGB(0, 0, 0)
        self.c.drawRightString(x_right, y, text)

    def _text_center(self, y, text, font, size):
        self.c.setFont(font, size)
        self.c.setFillColorRGB(0, 0, 0)
        self.c.drawCentredString(PAGE_W / 2, y, text)

    def _rule(self, y, x1=MARGIN_LEFT, x2=PAGE_W - MARGIN_RIGHT, thickness=0.75):
        self.c.setStrokeColorRGB(0, 0, 0)
        self.c.setLineWidth(thickness)
        self.c.line(x1, y, x2, y)

    # ── High-level blocks ─────────────────────────────────────────────────────

    def draw_header(self, personal):
        self._text_center(self.y, personal["name"], "Calibri-Bold", SIZE_NAME)
        self._move(LINE_HEIGHT_NAME)

        self._text_center(self.y, f"Address: {personal['location']}", "Calibri", SIZE_CONTACT)
        self._move(LINE_HEIGHT_CONTACT)

        contact = (
            f"Tel: {personal['phone']}  |  "
            f"Email: {personal['email']}  |  "
            f"{personal['linkedin']}"
        )
        self._text_center(self.y, contact, "Calibri", SIZE_CONTACT)
        self._move(LINE_HEIGHT_CONTACT + 2)

    def draw_section_header(self, title):
        self._check_break(needed=30)
        self._move(SECTION_GAP_BEFORE)

        # Draw section title bold
        self._text(MARGIN_LEFT, self.y, title, "Calibri-Bold", SIZE_SECTION)
        self._move(LINE_HEIGHT_SECTION - 2)

        self._move(SECTION_GAP_AFTER)

    def draw_company_line(self, company, location):
        self._check_break()
        self._text(MARGIN_LEFT, self.y, company, "Calibri-Bold", SIZE_BODY)
        self._text_right(PAGE_W - MARGIN_RIGHT, self.y, location, "Calibri-Bold", SIZE_BODY)
        self._move(LINE_HEIGHT_BODY)

    def draw_title_date_line(self, title, date_str):
        self._check_break()
        self._text(MARGIN_LEFT, self.y, title, "Calibri-Bold", SIZE_BODY)
        self._text_right(PAGE_W - MARGIN_RIGHT, self.y, date_str, "Calibri", SIZE_BODY)
        self._move(LINE_HEIGHT_BODY)

    def draw_bullet(self, text, indent_x=BULLET_TEXT_X, bullet_x=BULLET_X):
        max_w = PAGE_W - MARGIN_RIGHT - indent_x
        lines = _wrap(self.c, text, "Calibri", SIZE_BODY, max_w)

        for i, line in enumerate(lines):
            self._check_break()
            if i == 0:
                self._text(bullet_x, self.y, "\u2022", "Calibri", SIZE_BODY)
            self._text(indent_x, self.y, line, "Calibri", SIZE_BODY)
            self._move(LINE_HEIGHT_BODY)

    def done(self):
        self.c.save()
        return self.buf.getvalue()


# ── Main render function ───────────────────────────────────────────────────────

def render_cv(cv_data: dict) -> bytes:
    cv = CVCanvas()

    # Header
    cv.draw_header(cv_data["personal"])

    # Experience
    if cv_data.get("experience"):
        cv.draw_section_header("EXPERIENCE")
        for i, exp in enumerate(cv_data["experience"]):
            if i > 0:
                cv._move(ENTRY_GAP)
            if "roles" in exp:
                cv.draw_company_line(exp["company"], exp["location"])
                for role in exp["roles"]:
                    cv.draw_title_date_line(
                        role["title"],
                        f"{role['start']} \u2013 {role['end']}"
                    )
            else:
                cv.draw_company_line(exp["company"], exp["location"])
                cv.draw_title_date_line(
                    exp["title"],
                    f"{exp['start']} \u2013 {exp['end']}"
                )
            for bullet in exp.get("bullets", []):
                cv.draw_bullet(bullet["text"] if isinstance(bullet, dict) else bullet)

    # Education
    if cv_data.get("education"):
        cv.draw_section_header("EDUCATION")
        for i, edu in enumerate(cv_data["education"]):
            if i > 0:
                cv._move(ENTRY_GAP)
            gpa = f" ({edu['gpa']} GPA)" if edu.get("gpa") else ""
            cv.draw_company_line(edu["institution"] + gpa, edu["location"])
            cv.draw_title_date_line(
                edu["degree"],
                f"{edu['start']} \u2013 {edu['end']}"
            )
            for hl in edu.get("highlights", []):
                cv.draw_bullet(hl)
            if edu.get("coursework"):
                cv.draw_bullet("Relevant Coursework: " + ", ".join(edu["coursework"]))

    # Volunteer
    if cv_data.get("volunteer"):
        cv.draw_section_header("VOLUNTEER WORK")
        for vol in cv_data["volunteer"]:
            cv.draw_company_line(vol["organization"], vol["location"])
            cv.draw_title_date_line(
                vol["title"],
                f"{vol['start']} \u2013 {vol['end']}"
            )
            for bullet in vol.get("bullets", []):
                cv.draw_bullet(bullet["text"] if isinstance(bullet, dict) else bullet)

    # Skills
    if cv_data.get("skills"):
        cv.draw_section_header("SKILLS/ACTIVITIES")
        skills = cv_data["skills"]

        if skills.get("technical"):
            cv.draw_bullet("Technical skills: " + ", ".join(skills["technical"]))

        if skills.get("data"):
            cv.draw_bullet("Data skills: " + "; ".join(skills["data"]))

        if skills.get("finance"):
            cv.draw_bullet("Skills: " + ", ".join(skills["finance"]))

        if skills.get("business"):
            extras = [s for s in skills["business"] if s not in skills.get("finance", [])]
            if extras:
                cv.draw_bullet(", ".join(extras))

        if skills.get("certifications"):
            cv.draw_bullet("Certifications: " + ", ".join(skills["certifications"]))

        if skills.get("languages"):
            lang_str = ", ".join(
                f"{l['language']} ({l['level']})" for l in skills["languages"]
            )
            cv.draw_bullet("Language skills: " + lang_str)

    return cv.done()


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json, pathlib

    master = json.loads(
        pathlib.Path("master_cv.json").read_text(encoding="utf-8")
    )
    pdf_bytes = render_cv(master)
    out = pathlib.Path("test_output.pdf")
    out.write_bytes(pdf_bytes)
    print(f"Written {len(pdf_bytes):,} bytes → {out}  ({len(pdf_bytes):,} bytes)")
