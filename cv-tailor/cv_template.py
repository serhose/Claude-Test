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
pdfmetrics.registerFont(TTFont("Calibri",      "C:/Windows/Fonts/calibri.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-Bold", "C:/Windows/Fonts/calibrib.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-Italic","C:/Windows/Fonts/calibrii.ttf"))

# ── Layout constants (points) ─────────────────────────────────────────────────
PAGE_W        = 612
PAGE_H        = 792
MARGIN_LEFT   = 36
MARGIN_RIGHT  = 36
MARGIN_TOP    = 39          # first baseline (name)
MARGIN_BOTTOM = 36
CONTENT_W     = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT   # 540

BULLET_X      = MARGIN_LEFT           # 36  — bullet glyph
BULLET_TEXT_X = MARGIN_LEFT + 18      # 54  — bullet text start
SUB_BULLET_X      = MARGIN_LEFT + 14  # nested bullet glyph
SUB_BULLET_TEXT_X = MARGIN_LEFT + 32  # nested bullet text

# ── Font sizes ────────────────────────────────────────────────────────────────
SIZE_NAME          = 17
SIZE_CONTACT       = 11
SIZE_SECTION_BIG   = 16   # first letter of section header
SIZE_SECTION_SMALL = 13   # rest of section header
SIZE_COMPANY       = 12
SIZE_BODY          = 12

LINE_HEIGHT_BODY   = 14.4   # 12 * 1.2
LINE_HEIGHT_SMALL  = 13.2   # 11 * 1.2

SECTION_GAP_BEFORE = 8     # space before section header line
SECTION_GAP_AFTER  = 6     # space between rule and first entry
ENTRY_GAP          = 6     # space between entries within a section
BULLET_GAP         = 1     # extra leading between bullets


def _wrap(c_obj, text, font, size, max_w):
    """Return list of lines that fit within max_w."""
    return simpleSplit(text, font, size, max_w)


class CVCanvas:
    """Stateful drawing helper that tracks the current Y position."""

    def __init__(self):
        self.buf = io.BytesIO()
        self.c   = canvas.Canvas(self.buf, pagesize=(PAGE_W, PAGE_H))
        self.y   = PAGE_H - MARGIN_TOP   # current baseline (ReportLab: 0 = bottom)

    def _move(self, delta):
        """Move y downward by delta points."""
        self.y -= delta

    # ── Primitives ────────────────────────────────────────────────────────────

    def text(self, x, text, font, size, color=(0, 0, 0)):
        self.c.setFont(font, size)
        self.c.setFillColorRGB(*color)
        self.c.drawString(x, self.y, text)

    def text_right(self, x_right, text, font, size, color=(0, 0, 0)):
        self.c.setFont(font, size)
        self.c.setFillColorRGB(*color)
        self.c.drawRightString(x_right, self.y, text)

    def text_center(self, text, font, size, color=(0, 0, 0)):
        self.c.setFont(font, size)
        self.c.setFillColorRGB(*color)
        self.c.drawCentredString(PAGE_W / 2, self.y, text)

    def rule(self, x1=MARGIN_LEFT, x2=PAGE_W - MARGIN_RIGHT, thickness=0.8):
        self.c.setStrokeColorRGB(0, 0, 0)
        self.c.setLineWidth(thickness)
        self.c.line(x1, self.y, x2, self.y)

    # ── High-level blocks ─────────────────────────────────────────────────────

    def draw_header(self, personal):
        """Name + contact lines at top."""
        self.text_center(personal["name"], "Calibri-Bold", SIZE_NAME)
        self._move(SIZE_NAME + 2)

        self.text_center(f"Address: {personal['location']}", "Calibri", SIZE_CONTACT)
        self._move(SIZE_CONTACT + 2)

        contact_line = (
            f"Tel: {personal['phone']}  |  "
            f"Email: {personal['email']}  |  "
            f"{personal['linkedin']}"
        )
        self.text_center(contact_line, "Calibri", SIZE_CONTACT)
        self._move(SIZE_CONTACT + 4)

    def draw_section_header(self, title):
        """
        Section title with decorative large first letter + horizontal rule below.
        E.g. 'EXPERIENCE' → big 'E' + smaller 'XPERIENCE'
        """
        self._move(SECTION_GAP_BEFORE)

        first  = title[0]
        rest   = title[1:]

        # Measure widths to position correctly
        self.c.setFont("Calibri-Bold", SIZE_SECTION_BIG)
        w_first = self.c.stringWidth(first, "Calibri-Bold", SIZE_SECTION_BIG)

        self.c.setFont("Calibri-Bold", SIZE_SECTION_SMALL)
        # draw first letter
        self.c.setFillColorRGB(0, 0, 0)
        self.c.setFont("Calibri-Bold", SIZE_SECTION_BIG)
        self.c.drawString(MARGIN_LEFT, self.y, first)
        # draw rest slightly lower to baseline-align
        self.c.setFont("Calibri-Bold", SIZE_SECTION_SMALL)
        self.c.drawString(MARGIN_LEFT + w_first, self.y - 2, rest)

        self._move(SIZE_SECTION_BIG + 2)
        self.rule()
        self._move(SECTION_GAP_AFTER)

    def draw_company_line(self, company, location):
        """Bold company name left, bold location right — same line."""
        self.text(MARGIN_LEFT, company, "Calibri-Bold", SIZE_COMPANY)
        self.text_right(PAGE_W - MARGIN_RIGHT, location, "Calibri-Bold", SIZE_COMPANY)
        self._move(LINE_HEIGHT_BODY)

    def draw_title_date_line(self, title, date_str):
        """Bold title left, regular date right — same line."""
        self.text(MARGIN_LEFT, title, "Calibri-Bold", SIZE_COMPANY)
        self.text_right(PAGE_W - MARGIN_RIGHT, date_str, "Calibri", SIZE_COMPANY)
        self._move(LINE_HEIGHT_BODY)

    def draw_bullet(self, text, indent_x=BULLET_TEXT_X, bullet_x=BULLET_X):
        """Draw a bullet point, wrapping if necessary."""
        max_w = PAGE_W - MARGIN_RIGHT - indent_x
        lines = _wrap(self.c, text, "Calibri", SIZE_BODY, max_w)

        # bullet glyph on first line
        self.c.setFont("Calibri", SIZE_BODY)
        self.c.setFillColorRGB(0, 0, 0)
        self.c.drawString(bullet_x, self.y, "\u2022")

        for i, line in enumerate(lines):
            self.c.setFont("Calibri", SIZE_BODY)
            self.c.drawString(indent_x, self.y, line)
            self._move(LINE_HEIGHT_BODY + BULLET_GAP)

    def draw_sub_bullet(self, text):
        """Nested bullet (one level deeper)."""
        self.draw_bullet(text, indent_x=SUB_BULLET_TEXT_X, bullet_x=SUB_BULLET_X)

    def draw_label_line(self, label, value):
        """Bold label + regular value on same line (for Skills section)."""
        self.c.setFont("Calibri-Bold", SIZE_BODY)
        w = self.c.stringWidth(label + " ", "Calibri-Bold", SIZE_BODY)
        self.c.setFillColorRGB(0, 0, 0)
        self.c.drawString(MARGIN_LEFT, self.y, label)

        self.c.setFont("Calibri", SIZE_BODY)
        # wrap remaining text
        max_w = PAGE_W - MARGIN_RIGHT - (MARGIN_LEFT + w)
        lines = _wrap(self.c, value, "Calibri", SIZE_BODY, max_w)
        self.c.drawString(MARGIN_LEFT + w, self.y, lines[0])
        self._move(LINE_HEIGHT_BODY)
        for line in lines[1:]:
            self.c.drawString(MARGIN_LEFT, self.y, line)
            self._move(LINE_HEIGHT_BODY)

    def done(self):
        """Finalize and return PDF bytes."""
        self.c.save()
        return self.buf.getvalue()


# ── Main render function ───────────────────────────────────────────────────────

def render_cv(cv_data: dict) -> bytes:
    """
    Render a tailored CV from structured cv_data dict.
    cv_data mirrors master_cv.json but with only selected bullets/sections.
    Returns PDF bytes.
    """
    cv = CVCanvas()

    # ── Header ──────────────────────────────────────────────────────────────
    cv.draw_header(cv_data["personal"])

    # ── Experience ──────────────────────────────────────────────────────────
    if cv_data.get("experience"):
        cv.draw_section_header("EXPERIENCE")

        for i, exp in enumerate(cv_data["experience"]):
            if i > 0:
                cv._move(ENTRY_GAP)

            # Handle single role vs multiple roles
            if "roles" in exp:
                cv.draw_company_line(exp["company"], exp["location"])
                for role in exp["roles"]:
                    date_str = f"{role['start']} \u2013 {role['end']}"
                    cv.draw_title_date_line(role["title"], date_str)
            else:
                cv.draw_company_line(exp["company"], exp["location"])
                date_str = f"{exp['start']} \u2013 {exp['end']}"
                cv.draw_title_date_line(exp["title"], date_str)

            for bullet in exp.get("bullets", []):
                if isinstance(bullet, dict):
                    text = bullet["text"]
                else:
                    text = bullet
                cv.draw_bullet(text)

    # ── Education ───────────────────────────────────────────────────────────
    if cv_data.get("education"):
        cv.draw_section_header("EDUCATION")

        for i, edu in enumerate(cv_data["education"]):
            if i > 0:
                cv._move(ENTRY_GAP)

            gpa_suffix = f" ({edu['gpa']} GPA)" if edu.get("gpa") else ""
            cv.draw_company_line(
                edu["institution"] + gpa_suffix,
                edu["location"]
            )
            date_str = f"{edu['start']} \u2013 {edu['end']}"
            cv.draw_title_date_line(edu["degree"], date_str)

            for hl in edu.get("highlights", []):
                cv.draw_bullet(hl)

            if edu.get("coursework"):
                cv.draw_bullet("Relevant Coursework: " + ", ".join(edu["coursework"]))

    # ── Volunteer Work ──────────────────────────────────────────────────────
    if cv_data.get("volunteer"):
        cv.draw_section_header("VOLUNTEER WORK")

        for vol in cv_data["volunteer"]:
            cv.draw_company_line(vol["organization"], vol["location"])
            date_str = f"{vol['start']} \u2013 {vol['end']}"
            cv.draw_title_date_line(vol["title"], date_str)
            for bullet in vol.get("bullets", []):
                text = bullet["text"] if isinstance(bullet, dict) else bullet
                cv.draw_bullet(text)

    # ── Skills ──────────────────────────────────────────────────────────────
    if cv_data.get("skills"):
        cv.draw_section_header("SKILLS/ACTIVITIES")
        skills = cv_data["skills"]

        if skills.get("technical"):
            cv.draw_bullet("\u25aa Technical skills: " + ", ".join(skills["technical"]))

        if skills.get("data"):
            cv.draw_bullet("\u25aa " + "; ".join(skills["data"]))

        if skills.get("finance"):
            cv.draw_bullet("\u25aa Skills: " + ", ".join(skills["finance"]))

        if skills.get("business"):
            extra = [s for s in skills.get("business", []) if s not in skills.get("finance", [])]
            if extra:
                cv.draw_bullet("\u25aa " + ", ".join(extra))

        if skills.get("certifications"):
            cv.draw_bullet("\u25aa Certifications: " + ", ".join(skills["certifications"]))

        if skills.get("languages"):
            lang_str = ", ".join(
                f"{l['language']} ({l['level']})" for l in skills["languages"]
            )
            cv.draw_bullet("\u25aa Language skills: " + lang_str)

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
    print(f"Written {len(pdf_bytes):,} bytes to {out}")
