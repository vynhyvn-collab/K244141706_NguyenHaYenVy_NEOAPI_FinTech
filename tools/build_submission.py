import hashlib
import re
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(r"d:\K244141706_NguyenHaYenVy_NEOAPI_FinTech")
SUBMISSION = ROOT / "submission"
REPORT_MD = ROOT / "report" / "K244141706_NguyenHaYenVy_BaoCao.md"
PDF_NAME = "K244141706_NguyenHaYenVy_BaoCao.pdf"
DOCX_NAME = "K244141706_NguyenHaYenVy_BaoCao.docx"
ZIP_NAME = "K244141706_NguyenHaYenVy_NEOAPI_FinTech.zip"


def clean_markdown(text) -> str:
    if isinstance(text, list):
        text = "\n".join(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\$\\?(.+?)\$", r"\1", text)
    text = text.replace("\\frac", "frac")
    return text


def md_blocks(text: str):
    blocks = []
    code = False
    code_lines = []
    table_lines = []

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            if code:
                blocks.append(("code", "\n".join(code_lines)))
                code_lines = []
                code = False
            else:
                code = True
            continue
        if code:
            code_lines.append(line)
            continue
        if line.startswith("|"):
            table_lines.append(line)
            continue
        if table_lines:
            blocks.append(("table", table_lines))
            table_lines = []
        if re.match(r"^!\[(.+?)\]\((.+?)\)$", line):
            match = re.match(r"^!\[(.+?)\]\((.+?)\)$", line)
            blocks.append(("image", (match.group(1), match.group(2))))
        elif not line:
            blocks.append(("blank", ""))
        elif line.startswith("### "):
            blocks.append(("h3", line[4:]))
        elif line.startswith("## "):
            blocks.append(("h2", line[3:]))
        elif line.startswith("# "):
            blocks.append(("h1", line[2:]))
        elif line.startswith("* ") or line.startswith("- "):
            blocks.append(("bullet", line[2:]))
        elif re.match(r"^\d+\. ", line):
            blocks.append(("bullet", re.sub(r"^\d+\. ", "", line)))
        else:
            blocks.append(("p", line))

    if code_lines:
        blocks.append(("code", "\n".join(code_lines)))
    if table_lines:
        blocks.append(("table", table_lines))
    return blocks


def make_docx():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(11)

    for kind, value in md_blocks(REPORT_MD.read_text(encoding="utf-8")):
        if kind == "blank":
            continue
        if kind == "image":
            alt_text, relative_path = value
            image_path = REPORT_MD.parent / relative_path
            if image_path.exists():
                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.add_run().add_picture(str(image_path), width=Inches(6.2))
                caption = doc.add_paragraph(alt_text)
                caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue
        value = clean_markdown(value)
        if kind == "h1":
            p = doc.add_heading(value, level=1)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif kind == "h2":
            doc.add_heading(value, level=2)
        elif kind == "h3":
            doc.add_heading(value, level=3)
        elif kind == "bullet":
            doc.add_paragraph(value, style="List Bullet")
        elif kind == "code":
            p = doc.add_paragraph()
            p.style = doc.styles["Normal"]
            run = p.add_run(value)
            run.font.name = "Courier New"
            run.font.size = Pt(8)
        elif kind == "table":
            rows = [row.strip("|").split("|") for row in value]
            rows = [[cell.strip() for cell in row] for row in rows if len(row) > 1]
            if len(rows) >= 2:
                table = doc.add_table(rows=len(rows), cols=len(rows[0]))
                table.style = "Table Grid"
                for i, row in enumerate(rows):
                    for j, cell in enumerate(row[:len(rows[0])]):
                        table.cell(i, j).text = clean_markdown(cell)
                for j in range(len(rows[0])):
                    if j < len(table.rows[0].cells):
                        table.rows[0].cells[j]._tc.get_or_add_tcPr()
        else:
            doc.add_paragraph(value)

    output = SUBMISSION / DOCX_NAME
    doc.save(output)


def make_pdf():
    output = SUBMISSION / PDF_NAME

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleVN", parent=styles["Title"], alignment=TA_CENTER, fontSize=16, leading=20, spaceAfter=8))
    styles.add(ParagraphStyle(name="HeadingVN", parent=styles["Heading1"], fontSize=13, leading=16, textColor=colors.HexColor("#1E3A8A"), spaceBefore=10, spaceAfter=5))
    styles.add(ParagraphStyle(name="SubHeadingVN", parent=styles["Heading2"], fontSize=11, leading=14, textColor=colors.HexColor("#334155"), spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle(name="BodyVN", parent=styles["BodyText"], fontName="Helvetica", fontSize=10, leading=14, spaceAfter=5))
    styles.add(ParagraphStyle(name="BulletVN", parent=styles["BodyText"], fontName="Helvetica", fontSize=10, leading=13, leftIndent=12, firstLineIndent=-6, spaceAfter=3))
    styles.add(ParagraphStyle(name="CodeVN", parent=styles["Code"], fontName="Courier", fontSize=7.5, leading=9, leftIndent=8, spaceAfter=5))
    styles.add(ParagraphStyle(name="CaptionVN", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#475569"), spaceBefore=3, spaceAfter=5))

    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm)
    story = []

    for kind, value in md_blocks(REPORT_MD.read_text(encoding="utf-8")):
        if kind == "blank":
            continue
        if kind == "image":
            alt_text, relative_path = value
            image_path = REPORT_MD.parent / relative_path
            if image_path.exists():
                from reportlab.platypus import Image
                story.append(Image(str(image_path), width=170*mm, height=95*mm, kind="proportional"))
                story.append(Paragraph(alt_text, styles["CaptionVN"]))
            continue
        value = clean_markdown(value)
        if kind == "h1":
            story.append(Paragraph(value, styles["TitleVN"]))
        elif kind == "h2":
            story.append(Paragraph(value, styles["HeadingVN"]))
        elif kind == "h3":
            story.append(Paragraph(value, styles["SubHeadingVN"]))
        elif kind == "bullet":
            story.append(Paragraph("• " + value, styles["BulletVN"]))
        elif kind == "code":
            story.append(Paragraph(value.replace("\n", "<br/>"), styles["CodeVN"]))
        elif kind == "table":
            rows = [row.strip("|").split("|") for row in value]
            rows = [[clean_markdown(cell.strip()) for cell in row] for row in rows if len(row) > 1]
            if rows:
                table = Table(rows, repeatRows=1, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DBEAFE")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94A3B8")),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEADING", (0, 0), (-1, -1), 9),
                ]))
                story.append(table)
                story.append(Spacer(1, 4*mm))
        else:
            story.append(Paragraph(value, styles["BodyVN"]))

    doc.build(story)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_zip():
    zip_path = SUBMISSION / ZIP_NAME
    include_dirs = ["src", "tests", "data_sample", "docs", "report"]
    include_files = ["README.md", "requirements.txt", "pyproject.toml", ".env.example", ".gitignore"]

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename in include_files:
            path = ROOT / filename
            if path.exists():
                archive.write(path, filename)
        for dirname in include_dirs:
            base = ROOT / dirname
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if not path.is_file():
                    continue
                if any(part.lower() in {"__pycache__", ".pytest_cache", ".venv", ".git"} for part in path.parts):
                    continue
                archive.write(path, path.relative_to(ROOT).as_posix())


def main():
    SUBMISSION.mkdir(exist_ok=True)
    make_docx()
    make_pdf()
    make_zip()

    lines = ["CÁC TỆP NỘP", ""]
    for path in sorted(SUBMISSION.iterdir(), key=lambda item: item.name):
        if path.is_file():
            lines.append(f"{path.name}")
            lines.append(f"SHA256: {sha256(path)}")
            lines.append("")
    (SUBMISSION / "K244141706_NguyenHaYenVy_DanhSachNop.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
