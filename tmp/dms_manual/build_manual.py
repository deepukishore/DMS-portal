from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image as PILImage
from PIL import ImageFilter, ImageDraw
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


ROOT = Path(r"C:\Users\deepu\OneDrive\Desktop\Rane\dms_portal_copy")
CURRENT_SCREENSHOTS = ROOT / "tmp" / "dms_manual" / "current_screenshots"
SCREENSHOTS = CURRENT_SCREENSHOTS
ASSETS = ROOT / "tmp" / "dms_manual" / "manual_assets"
OUTPUT = ROOT / "output" / "pdf" / "DMS_Portal_User_Manual_Clear.pdf"
LOGO = ROOT / "static" / "images" / "logo.jpg"

ASSETS.mkdir(parents=True, exist_ok=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

W, H = A4
LEFT = 38
RIGHT = 38
CONTENT_W = W - LEFT - RIGHT
CONTENT_TOP = H - 108
CONTENT_BOTTOM = 42
TOTAL_PAGES = 24

NAVY = colors.HexColor("#0B356B")
BLUE = colors.HexColor("#0877B9")
TEAL = colors.HexColor("#008B95")
GREEN = colors.HexColor("#1A7A3A")
PURPLE = colors.HexColor("#5E258C")
ORANGE = colors.HexColor("#D98400")
PINK = colors.HexColor("#D52F73")
YELLOW = colors.HexColor("#F8B900")
RED = colors.HexColor("#C62828")
INK = colors.HexColor("#14213D")
MUTED = colors.HexColor("#5A6B82")
LIGHT = colors.HexColor("#F4F7FB")
LINE = colors.HexColor("#C9D6E5")
PALE_BLUE = colors.HexColor("#EAF3FA")
PALE_YELLOW = colors.HexColor("#FFF7DA")
PALE_GREEN = colors.HexColor("#EAF6EE")
PALE_RED = colors.HexColor("#FDECEC")
WHITE = colors.white


def register_fonts():
    regular = Path(r"C:\Windows\Fonts\arial.ttf")
    bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
    italic = Path(r"C:\Windows\Fonts\ariali.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("ManualSans", str(regular)))
        pdfmetrics.registerFont(TTFont("ManualSans-Bold", str(bold)))
        if italic.exists():
            pdfmetrics.registerFont(TTFont("ManualSans-Italic", str(italic)))
        else:
            pdfmetrics.registerFont(TTFont("ManualSans-Italic", str(regular)))
        return "ManualSans", "ManualSans-Bold", "ManualSans-Italic"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


FONT, FONT_BOLD, FONT_ITALIC = register_fonts()

BODY = ParagraphStyle(
    "Body",
    fontName=FONT,
    fontSize=9.4,
    leading=12.8,
    textColor=INK,
    alignment=TA_LEFT,
    spaceAfter=0,
)
SMALL = ParagraphStyle(
    "Small",
    fontName=FONT,
    fontSize=8.2,
    leading=10.8,
    textColor=MUTED,
    alignment=TA_LEFT,
)
CAPTION = ParagraphStyle(
    "Caption",
    fontName=FONT_ITALIC,
    fontSize=7.6,
    leading=9.2,
    textColor=MUTED,
    alignment=TA_CENTER,
)
PANEL_TITLE = ParagraphStyle(
    "PanelTitle",
    fontName=FONT_BOLD,
    fontSize=10,
    leading=12,
    textColor=NAVY,
)
TABLE_TEXT = ParagraphStyle(
    "TableText",
    fontName=FONT,
    fontSize=7.8,
    leading=9.8,
    textColor=INK,
)
TABLE_HEAD = ParagraphStyle(
    "TableHead",
    fontName=FONT_BOLD,
    fontSize=7.8,
    leading=9.8,
    textColor=WHITE,
)


def crop_image(source_name, output_name, box):
    source = SCREENSHOTS / source_name
    return crop_path(source, output_name, box)


def crop_path(source, output_name, box):
    output = ASSETS / output_name
    with PILImage.open(source) as image:
        left, top, right, bottom = box
        clamped = (
            max(0, min(left, image.width)),
            max(0, min(top, image.height)),
            max(1, min(right, image.width)),
            max(1, min(bottom, image.height)),
        )
        image.crop(clamped).save(output, quality=95)
    return output


def sanitize_image(source_name, output_name, blur_regions=None, cover_regions=None):
    source = SCREENSHOTS / source_name
    output = ASSETS / output_name
    with PILImage.open(source).convert("RGB") as image:
        for region in blur_regions or []:
            blurred = image.crop(region).filter(ImageFilter.GaussianBlur(radius=11))
            image.paste(blurred, region)
        if cover_regions:
            draw = ImageDraw.Draw(image)
            for region, fill in cover_regions:
                draw.rounded_rectangle(region, radius=10, fill=fill)
        image.save(output, quality=95)
    return output


dashboard_top = crop_image("02_dashboard.png", "dashboard_top.png", (255, 58, 1238, 478))
upload_top = crop_image("03_upload.png", "upload_top.png", (255, 58, 1238, 478))
upload_bottom = crop_image("03_upload_bottom.png", "upload_bottom.png", (255, 0, 1238, 478))
approvals_focus = crop_image("04_approvals.png", "approvals_focus.png", (255, 58, 1238, 478))
review_top = crop_image("05_approval_review.png", "approval_review_top.png", (0, 20, 1240, 478))
tracking_top = crop_image("06_tracking.png", "tracking_top.png", (255, 58, 1238, 478))
library_focus = crop_image("07_document_library.png", "library_focus.png", (255, 58, 1238, 478))
procedures_focus = crop_image("20_procedures.png", "procedures_focus.png", (285, 210, 1200, 478))
manuals_focus = crop_image("22_std_manual.png", "manuals_focus.png", (285, 210, 1200, 478))
master_focus = crop_image("09_master_records.png", "master_focus.png", (285, 210, 1200, 478))
customer_focus = crop_image("10_customer_records.png", "customer_focus.png", (285, 210, 1200, 478))
report_top = crop_image("16_graphics_report.png", "graphics_report_top.png", (255, 58, 1238, 478))
revision_focus = crop_image("11_revision_history.png", "revision_focus.png", (255, 58, 1238, 478))
archive_focus = crop_image("17_archive.png", "archive_focus.png", (255, 58, 1238, 478))
log_focus = crop_image("12_system_log.png", "log_focus.png", (255, 58, 1238, 478))
notifications_top = crop_image("23_notifications_open.png", "notifications_top.png", (255, 45, 1238, 478))
login_safe = sanitize_image(
    "01_login.png",
    "login_safe.png",
    cover_regions=[((750, 650, 1380, 870), (246, 248, 252))],
)
people_safe = sanitize_image(
    "18_people.png",
    "people_safe.png",
    blur_regions=[
        (995, 5, 1120, 50),
        (300, 385, 1195, 478),
    ],
)
profile_safe = sanitize_image(
    "13_profile.png",
    "profile_safe.png",
    blur_regions=[
        (995, 5, 1120, 50),
        (660, 90, 1195, 255),
        (300, 360, 850, 478),
        (880, 355, 1195, 478),
    ],
)
people_focus = crop_path(people_safe, "people_focus.png", (255, 58, 1238, 478))
profile_focus = crop_path(profile_safe, "profile_focus.png", (255, 58, 1238, 478))


def para(c, text, x, y_top, width, style=BODY):
    p = Paragraph(text, style)
    _, h = p.wrap(width, H)
    p.drawOn(c, x, y_top - h)
    return y_top - h


def fit_image(path, max_w, max_h):
    with PILImage.open(path) as image:
        iw, ih = image.size
    scale = min(max_w / iw, max_h / ih)
    return iw * scale, ih * scale


def image_panel(c, path, x, y_top, max_w, max_h, caption=None):
    draw_w, draw_h = fit_image(path, max_w, max_h)
    draw_x = x + (max_w - draw_w) / 2
    c.setFillColor(colors.HexColor("#D7E1ED"))
    c.roundRect(draw_x + 3, y_top - draw_h - 3, draw_w, draw_h, 5, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setStrokeColor(LINE)
    c.roundRect(draw_x, y_top - draw_h, draw_w, draw_h, 5, fill=1, stroke=1)
    c.drawImage(
        ImageReader(str(path)),
        draw_x + 1,
        y_top - draw_h + 1,
        draw_w - 2,
        draw_h - 2,
        preserveAspectRatio=True,
        mask="auto",
    )
    y = y_top - draw_h
    if caption:
        y -= 5
        y = para(c, escape(caption), x, y, max_w, CAPTION)
    return y


def step_list(c, steps, x, y_top, width, color=NAVY, compact=False):
    y = y_top
    number_size = 18 if compact else 22
    title_size = 8.6 if compact else 9.2
    body_size = 7.7 if compact else 8.2
    for idx, (title, body) in enumerate(steps, 1):
        title_style = ParagraphStyle(
            f"StepTitle{idx}",
            fontName=FONT_BOLD,
            fontSize=title_size,
            leading=title_size + 2,
            textColor=INK,
        )
        body_style = ParagraphStyle(
            f"StepBody{idx}",
            fontName=FONT,
            fontSize=body_size,
            leading=body_size + 2.5,
            textColor=MUTED,
        )
        text_x = x + number_size + 11
        text_w = width - number_size - 18
        title_p = Paragraph(escape(title), title_style)
        body_p = Paragraph(escape(body), body_style)
        _, title_h = title_p.wrap(text_w, H)
        _, body_h = body_p.wrap(text_w, H)
        box_h = max(number_size + 8, title_h + body_h + 11)
        c.setFillColor(LIGHT)
        c.setStrokeColor(LINE)
        c.roundRect(x, y - box_h, width, box_h, 5, fill=1, stroke=1)
        c.setFillColor(color)
        c.circle(x + number_size / 2 + 7, y - box_h / 2, number_size / 2, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(FONT_BOLD, 9 if compact else 10)
        c.drawCentredString(x + number_size / 2 + 7, y - box_h / 2 - 3.2, str(idx))
        title_p.drawOn(c, text_x, y - 5 - title_h)
        body_p.drawOn(c, text_x, y - 6 - title_h - body_h)
        y -= box_h + 6
    return y


def callout(c, title, body, x, y_top, width, kind="note"):
    palette = {
        "note": (PALE_BLUE, BLUE),
        "tip": (PALE_GREEN, GREEN),
        "warning": (PALE_YELLOW, ORANGE),
        "danger": (PALE_RED, RED),
    }
    fill, accent = palette[kind]
    title_p = Paragraph(escape(title), PANEL_TITLE)
    body_p = Paragraph(escape(body), SMALL)
    _, title_h = title_p.wrap(width - 28, H)
    _, body_h = body_p.wrap(width - 28, H)
    box_h = title_h + body_h + 18
    c.setFillColor(fill)
    c.setStrokeColor(accent)
    c.roundRect(x, y_top - box_h, width, box_h, 5, fill=1, stroke=1)
    c.setFillColor(accent)
    c.rect(x, y_top - box_h, 5, box_h, fill=1, stroke=0)
    title_p.drawOn(c, x + 15, y_top - 7 - title_h)
    body_p.drawOn(c, x + 15, y_top - 8 - title_h - body_h)
    return y_top - box_h


def table_at(c, data, x, y_top, col_widths, row_heights=None, style_commands=None):
    table = Table(data, colWidths=col_widths, rowHeights=row_heights)
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTNAME", (0, 1), (-1, -1), FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 7.8),
        ("LEADING", (0, 0), (-1, -1), 9.8),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
    ]
    if style_commands:
        commands.extend(style_commands)
    table.setStyle(TableStyle(commands))
    _, h = table.wrap(sum(col_widths), H)
    table.drawOn(c, x, y_top - h)
    return y_top - h


def header(c, page_num, section, title, color=NAVY):
    c.setFillColor(WHITE)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.drawImage(ImageReader(str(LOGO)), LEFT, H - 47, 86, 32, preserveAspectRatio=True, mask="auto")
    c.setFillColor(MUTED)
    c.setFont(FONT, 6.8)
    c.drawString(LEFT + 96, H - 24, "ZF Rane Automotive India PVT LTD - SGD")
    c.drawString(LEFT + 96, H - 36, "Smart DMS Portal User Manual")

    meta_x = W - RIGHT - 228
    meta_y = H - 48
    meta_w = 228
    meta_h = 35
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    c.rect(meta_x, meta_y, meta_w, meta_h, fill=0, stroke=1)
    c.line(meta_x, meta_y + meta_h / 2, meta_x + meta_w, meta_y + meta_h / 2)
    c.line(meta_x + 114, meta_y, meta_x + 114, meta_y + meta_h)
    c.setFillColor(INK)
    c.setFont(FONT, 6.5)
    c.drawString(meta_x + 5, meta_y + 23, "Document: DMS-UM-001")
    c.drawString(meta_x + 119, meta_y + 23, "Revision: 1.0")
    c.drawString(meta_x + 5, meta_y + 6, "Effective: 29-Jul-2026")
    c.drawString(meta_x + 119, meta_y + 6, f"Page: {page_num} of {TOTAL_PAGES}")

    c.setFillColor(color)
    c.rect(0, H - 95, W, 34, fill=1, stroke=0)
    c.setFillColor(YELLOW)
    c.roundRect(LEFT, H - 88, 42, 20, 5, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 8)
    c.drawCentredString(LEFT + 21, H - 81.5, section)
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 15)
    c.drawString(LEFT + 52, H - 84, title)

    c.setStrokeColor(LINE)
    c.line(LEFT, 31, W - RIGHT, 31)
    c.setFillColor(MUTED)
    c.setFont(FONT, 6.7)
    c.drawString(LEFT, 19, "Internal user guide - controlled copy when viewed in the DMS portal")
    c.drawRightString(W - RIGHT, 19, "Smart DMS v2.0.0")


def start_page(c, page_num, section, title, subtitle=None, color=NAVY):
    header(c, page_num, section, title, color)
    y = CONTENT_TOP
    if subtitle:
        y = para(c, escape(subtitle), LEFT, y, CONTENT_W, SMALL) - 8
    return y


def end_page(c):
    c.showPage()


def cover_page(c):
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#092A55"))
    c.circle(W + 20, H - 70, 210, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#0E467F"))
    c.circle(-40, 90, 180, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.roundRect(LEFT, H - 96, 122, 51, 7, fill=1, stroke=0)
    c.drawImage(ImageReader(str(LOGO)), LEFT + 11, H - 87, 100, 35, preserveAspectRatio=True, mask="auto")

    c.setFillColor(YELLOW)
    c.setFont(FONT_BOLD, 10)
    c.drawString(LEFT, H - 138, "CONTROLLED DOCUMENT")
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 30)
    c.drawString(LEFT, H - 182, "SMART DMS PORTAL")
    c.setFont(FONT_BOLD, 23)
    c.drawString(LEFT, H - 215, "USER MANUAL")
    c.setFillColor(colors.HexColor("#CFE5FA"))
    c.setFont(FONT, 12)
    c.drawString(LEFT, H - 244, "Document submission, approval, access, reporting and audit")

    card_y = H - 337
    c.setFillColor(WHITE)
    c.roundRect(LEFT, card_y, CONTENT_W, 64, 7, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 8)
    c.drawString(LEFT + 14, card_y + 43, "DOCUMENT NUMBER")
    c.drawString(LEFT + 160, card_y + 43, "REVISION")
    c.drawString(LEFT + 262, card_y + 43, "EFFECTIVE DATE")
    c.drawString(LEFT + 402, card_y + 43, "OWNER")
    c.setFont(FONT, 9)
    c.drawString(LEFT + 14, card_y + 22, "DMS-UM-001")
    c.drawString(LEFT + 160, card_y + 22, "1.0")
    c.drawString(LEFT + 262, card_y + 22, "29-Jul-2026")
    c.drawString(LEFT + 402, card_y + 22, "DMS Team")

    image_panel(c, dashboard_top, LEFT, card_y - 22, CONTENT_W, 290)
    c.setFillColor(YELLOW)
    c.rect(LEFT, 67, CONTENT_W, 5, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 9)
    c.drawString(LEFT, 48, "ZF Rane Automotive India PVT LTD - SGD")
    c.setFont(FONT, 8)
    c.drawRightString(W - RIGHT, 48, "Internal use only")
    c.showPage()


def document_control_page(c):
    y = start_page(c, 2, "1.0", "Document Control and Contents", "Use the latest controlled copy available in the portal.")
    control = [
        [Paragraph("Field", TABLE_HEAD), Paragraph("Value", TABLE_HEAD), Paragraph("Field", TABLE_HEAD), Paragraph("Value", TABLE_HEAD)],
        [Paragraph("Document title", TABLE_TEXT), Paragraph("Smart DMS Portal User Manual", TABLE_TEXT), Paragraph("Document number", TABLE_TEXT), Paragraph("DMS-UM-001", TABLE_TEXT)],
        [Paragraph("Revision", TABLE_TEXT), Paragraph("1.0", TABLE_TEXT), Paragraph("Effective date", TABLE_TEXT), Paragraph("29-Jul-2026", TABLE_TEXT)],
        [Paragraph("Prepared for", TABLE_TEXT), Paragraph("ZF Rane Automotive India PVT LTD - SGD", TABLE_TEXT), Paragraph("Classification", TABLE_TEXT), Paragraph("Internal user guide", TABLE_TEXT)],
        [Paragraph("System", TABLE_TEXT), Paragraph("Smart DMS v2.0.0", TABLE_TEXT), Paragraph("Source", TABLE_TEXT), Paragraph("Portal UI, project SOP and reference deck", TABLE_TEXT)],
    ]
    y = table_at(c, control, LEFT, y, [86, 174, 86, 173]) - 15
    y = para(c, "<b>Contents</b>", LEFT, y, CONTENT_W, PANEL_TITLE) - 7
    contents = [
        ("1", "Document control and contents", "2"),
        ("2", "Purpose, scope and access levels", "3"),
        ("3", "End-to-end process overview", "4"),
        ("4", "Login and account access", "5-6"),
        ("5", "Dashboard and document submission", "7-9"),
        ("6", "Approvals and status tracking", "10-13"),
        ("7", "Document library and repositories", "14-16"),
        ("8", "Reports and revision control", "17-18"),
        ("9", "Archive, audit and people administration", "19-21"),
        ("10", "Notifications, profile, logout and troubleshooting", "22-24"),
    ]
    col1 = contents[:5]
    col2 = contents[5:]
    for col_index, col in enumerate((col1, col2)):
        x = LEFT + col_index * 263
        yy = y
        for number, title, page in col:
            c.setFillColor(PALE_BLUE)
            c.roundRect(x, yy - 42, 250, 36, 5, fill=1, stroke=0)
            c.setFillColor(NAVY)
            c.circle(x + 18, yy - 24, 11, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont(FONT_BOLD, 7.5)
            c.drawCentredString(x + 18, yy - 26.5, number)
            c.setFillColor(INK)
            c.setFont(FONT_BOLD, 7.8)
            text = Paragraph(escape(title), TABLE_TEXT)
            text.wrapOn(c, 176, 28)
            text.drawOn(c, x + 35, yy - 34)
            c.setFont(FONT_BOLD, 8)
            c.setFillColor(NAVY)
            c.drawRightString(x + 238, yy - 26, page)
            yy -= 46
    y -= 245
    callout(
        c,
        "Controlled-copy rule",
        "Screenshots are representative of the current portal. Field availability and administrative actions may vary by role, QMS level and configured library category.",
        LEFT,
        y,
        CONTENT_W,
        "note",
    )
    end_page(c)


def purpose_access_page(c):
    y = start_page(c, 3, "2.0", "Purpose, Scope and Access Levels", "This manual enables users to complete routine DMS work safely and consistently.", TEAL)
    x_gap = 12
    panel_w = (CONTENT_W - x_gap) / 2
    for idx, (title, text, color) in enumerate([
        ("Purpose", "Provide a practical guide for login, upload, approval, document access, reporting, audit review and secure logout.", BLUE),
        ("Scope", "Applies to portal users, L2 first approvers, L1 final approvers, managers, supervisors and administrators.", TEAL),
    ]):
        x = LEFT + idx * (panel_w + x_gap)
        c.setFillColor(LIGHT)
        c.setStrokeColor(color)
        c.roundRect(x, y - 82, panel_w, 74, 6, fill=1, stroke=1)
        c.setFillColor(color)
        c.rect(x, y - 82, 5, 74, fill=1, stroke=0)
        para(c, f"<b>{escape(title)}</b><br/>{escape(text)}", x + 15, y - 18, panel_w - 28, BODY)
    y -= 100

    access = [
        [Paragraph("Level / role", TABLE_HEAD), Paragraph("Primary access", TABLE_HEAD), Paragraph("Approval responsibility", TABLE_HEAD)],
        [Paragraph("<b>L1 - HOD / final approver</b>", TABLE_TEXT), Paragraph("All QMS files; final review; edit/delete rights where configured.", TABLE_TEXT), Paragraph("Approve or reject after L2 review. Admin is treated as L1.", TABLE_TEXT)],
        [Paragraph("<b>L2 - Assistant Manager / Manager</b>", TABLE_TEXT), Paragraph("All QMS files and first-stage review workspace.", TABLE_TEXT), Paragraph("Review, select recipients and send to L1; or reject with comments.", TABLE_TEXT)],
        [Paragraph("<b>L3 - Procedure viewer</b>", TABLE_TEXT), Paragraph("SOPs, plans, checklists and other reports.", TABLE_TEXT), Paragraph("No approval decision.", TABLE_TEXT)],
        [Paragraph("<b>L4 - Checksheet viewer</b>", TABLE_TEXT), Paragraph("Checklists and checksheets only.", TABLE_TEXT), Paragraph("No approval decision.", TABLE_TEXT)],
        [Paragraph("<b>High-level roles</b>", TABLE_TEXT), Paragraph("Admin, Manager, Supervisor and Approver can access Archive and System Log.", TABLE_TEXT), Paragraph("Decision rights still follow QMS level.", TABLE_TEXT)],
        [Paragraph("<b>Admin</b>", TABLE_TEXT), Paragraph("Full system access including People directory.", TABLE_TEXT), Paragraph("Final approval capability and user oversight.", TABLE_TEXT)],
    ]
    y = table_at(c, access, LEFT, y, [132, 204, 183]) - 13
    callout(
        c,
        "Key distinction",
        "Role controls administrative pages. QMS level controls document visibility and who can complete each approval stage.",
        LEFT,
        y,
        CONTENT_W,
        "warning",
    )
    end_page(c)


def process_overview_page(c):
    y = start_page(c, 4, "3.0", "End-to-End Process Overview", "The workflow below reflects the current two-stage approval design.", GREEN)
    stages = [
        ("1", "Sign in", "Email or GENID", NAVY),
        ("2", "Choose upload", "Open Upload Documents", BLUE),
        ("3", "Select files", "Approved Office/PDF formats", TEAL),
        ("4", "Add metadata", "Number, revision, plant, path", ORANGE),
        ("5", "Submit", "Status becomes Pending", PURPLE),
        ("6", "L2 review", "Select recipients and first approve", GREEN),
        ("7", "L1 review", "Final approve or reject", NAVY),
        ("8", "Use and report", "View, download, track, analyze", BLUE),
        ("9", "Retain and audit", "Revise, archive, restore/log", TEAL),
    ]
    box_w = (CONTENT_W - 24) / 3
    box_h = 116
    for idx, (number, title, body, color) in enumerate(stages):
        row = idx // 3
        col = idx % 3
        x = LEFT + col * (box_w + 12)
        top = y - row * (box_h + 18)
        c.setFillColor(LIGHT)
        c.setStrokeColor(color)
        c.roundRect(x, top - box_h, box_w, box_h, 8, fill=1, stroke=1)
        c.setFillColor(color)
        c.roundRect(x, top - 27, box_w, 27, 8, fill=1, stroke=0)
        c.rect(x, top - 27, box_w, 8, fill=1, stroke=0)
        c.setFillColor(YELLOW)
        c.circle(x + 20, top - 13.5, 9, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 7.5)
        c.drawCentredString(x + 20, top - 16, number)
        c.setFillColor(WHITE)
        c.setFont(FONT_BOLD, 9)
        c.drawString(x + 35, top - 17, title)
        para(c, escape(body), x + 12, top - 43, box_w - 24, SMALL)
        if col < 2:
            c.setStrokeColor(MUTED)
            c.setLineWidth(1)
            line_y = top - box_h / 2
            c.line(x + box_w + 2, line_y, x + box_w + 9, line_y)
            c.setFillColor(MUTED)
            c.wedge(x + box_w + 7, line_y - 3, x + box_w + 13, line_y + 3, 270, 180, fill=1, stroke=0)
    y -= 3 * (box_h + 18) - 3
    callout(
        c,
        "Status path",
        "Pending -> Pending Final Approval -> Approved. A rejection can occur at either approval stage and must include comments so the uploader knows what to correct.",
        LEFT,
        y,
        CONTENT_W,
        "note",
    )
    end_page(c)


def login_page(c):
    y = start_page(c, 5, "4.1", "Login to the Portal", "Use the portal URL supplied by your DMS administrator.", NAVY)
    y = image_panel(c, CURRENT_SCREENSHOTS / "01_login.png", LEFT, y, CONTENT_W, 340, "Figure 1 - Current Smart DMS login page") - 10
    steps = [
        ("Open the Smart DMS portal", "Use a supported browser and the approved internal URL."),
        ("Enter your identity", "Use your registered email address or employee GENID."),
        ("Enter your password", "Passwords are case-sensitive. Do not share credentials."),
        ("Select Sign in", "Successful login opens the Master Dashboard. An audit event is recorded."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, NAVY, compact=True)
    callout(c, "Access problem?", "Use Forgot password for a registered email address or contact the DMS administrator if the account is not active.", LEFT, y, CONTENT_W, "warning")
    end_page(c)


def register_page(c):
    y = start_page(c, 6, "4.2", "Register and Reset Password", "New accounts start with the User role and standard QMS access.", BLUE)
    y = image_panel(c, CURRENT_SCREENSHOTS / "01_login.png", LEFT, y, CONTENT_W, 336, "Figure 2 - Create account and Forgot password entry points on the current login page") - 10
    steps = [
        ("Open Create account", "From the login page, select Create account."),
        ("Complete identity fields", "Enter full name, optional employee ID, plant, official department and a unique email."),
        ("Create a password", "Use at least 8 characters and enter the same value in Confirm password."),
        ("Submit the registration", "Return to the login page after the success message. An administrator manages any elevated role or QMS-level assignment."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, BLUE, compact=True)
    callout(c, "Forgot password", "Select Forgot password on the login page, submit the registered email and follow the time-limited reset link. Reset links expire after 1 hour.", LEFT, y, CONTENT_W, "note")
    end_page(c)


def dashboard_page(c):
    y = start_page(c, 7, "5.1", "Use the Master Dashboard", "The dashboard is the main operational view for documents, filters and quick actions.", TEAL)
    y = image_panel(c, dashboard_top, LEFT, y, CONTENT_W, 326, "Figure 3 - Dashboard summary, quick actions and filters") - 10
    steps = [
        ("Review summary cards", "Check total, pending, approved and archived document counts."),
        ("Use quick actions", "Open Upload Documents, Pending Items, Document Library or Graphics Report."),
        ("Search and filter", "Filter by text, plant, department, customer and approval status."),
        ("Open a document", "Use row actions to view, download or bookmark. Deletion is restricted and moves the item to Archive."),
        ("Export the current view", "Use CSV export when a filtered list is required for offline review."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, TEAL, compact=True)
    callout(c, "Good practice", "Reset filters before concluding that a document is missing. Status and department filters can hide valid records.", LEFT, y, CONTENT_W, "tip")
    end_page(c)


def upload_files_page(c):
    y = start_page(c, 8, "5.2", "Upload Files and Enter Metadata", "Every upload is routed into the Document Library and sent for approval.", GREEN)
    y = image_panel(c, upload_top, LEFT, y, CONTENT_W, 309, "Figure 4 - File selection and the start of the upload form") - 10
    steps = [
        ("Select one or more files", "Drag files into the drop zone or choose Browse files."),
        ("Check format and size", "Accepted formats: PDF, DOC/DOCX, XLS/XLSX and PPT/PPTX. Maximum size is 100 MB per file."),
        ("Enter the document number", "Use the approved numbering convention, for example DOC-2026-001."),
        ("Confirm revision", "Enter the revision value. If left blank, the system uses Rev.00."),
        ("Select ownership", "Confirm plant and department. Choose a customer or enable Internal Document."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, GREEN, compact=True)
    callout(c, "Before upload", "Remove passwords from files intended for browser preview and confirm the file name does not expose confidential personal data.", LEFT, y, CONTENT_W, "warning")
    end_page(c)


def upload_path_page(c):
    y = start_page(c, 9, "5.3", "Choose the Library Path and Submit", "The selected category and folder determine where users find the approved document.", ORANGE)
    y = image_panel(c, upload_bottom, LEFT, y, CONTENT_W, 350, "Figure 5 - Current upload workflow; continue down the form to set the library path and submit") - 10
    steps = [
        ("Select the category", "Choose the correct library category, such as QMS."),
        ("Choose document type and folder", "Complete every path field until the path indicator shows the exact destination."),
        ("Add a revision summary when needed", "Enable the summary option when replacing or revising an existing controlled document."),
        ("Review all details", "Verify file, document number, revision, plant, department, customer and library path."),
        ("Submit for approval", "The document is stored with status Pending, the L2 reviewer is notified and the action is logged."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, ORANGE, compact=True)
    callout(c, "Required path", "Do not submit against a broad category when a lower-level folder is required. Incorrect placement makes controlled documents difficult to retrieve.", LEFT, y, CONTENT_W, "danger")
    end_page(c)


def pending_items_page(c):
    y = start_page(c, 10, "6.1", "Find Documents in Pending Items", "All logged-in users can view the approval list; decision rights depend on QMS level.", PURPLE)
    y = image_panel(c, approvals_focus, LEFT, y, CONTENT_W, 435, "Figure 6 - Pending Items list with status filters and review actions") - 10
    steps = [
        ("Choose a status tab", "View All, Pending, Pending Final Approval, Approved or Rejected items."),
        ("Search the list", "Search by file name, document number or uploader."),
        ("Open Review", "Inspect the file preview, metadata and current approval stage."),
        ("Export when required", "Download the filtered list as CSV for controlled reporting."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, PURPLE, compact=True)
    callout(c, "No bulk decisions", "Approvals must be reviewed individually because the workflow requires stage-specific review, recipient selection and comments.", LEFT, y, CONTENT_W, "note")
    end_page(c)


def review_workspace_page(c):
    y = start_page(c, 11, "6.2", "Review the Document Before Deciding", "Review the file and metadata together before completing an approval action.", NAVY)
    y = image_panel(c, review_top, LEFT, y, CONTENT_W, 345, "Figure 7 - Approval review workspace with preview and document details") - 10
    steps = [
        ("Confirm document identity", "Check file name, document number, revision, plant, department, customer and category."),
        ("Inspect the preview", "Open or download the source file when an inline preview is unavailable."),
        ("Check revision context", "Read the revision summary and compare with the previous approved version when applicable."),
        ("Confirm the current stage", "Pending requires L2 action. Pending Final Approval requires L1 or Admin action."),
        ("Record a clear decision", "Follow the correct stage procedure on the next page."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, NAVY, compact=True)
    callout(c, "Review standard", "Never approve from the list view alone. Open the review page and verify the actual file content.", LEFT, y, CONTENT_W, "warning")
    end_page(c)


def decision_page(c):
    y = start_page(c, 12, "6.3", "Complete the Two-Stage Approval", "Approval responsibility is assigned by QMS level, independent of general role.", GREEN)
    panel_gap = 14
    panel_w = (CONTENT_W - panel_gap) / 2
    panels = [
        (
            LEFT,
            "L2 - First-stage review",
            GREEN,
            [
                "Verify document accuracy and library placement.",
                "Choose the recipients or department heads who should receive the final approved document.",
                "Select First Approve to move the item to Pending Final Approval.",
                "Or select Reject and enter a clear correction comment.",
            ],
        ),
        (
            LEFT + panel_w + panel_gap,
            "L1 - Final review",
            NAVY,
            [
                "Confirm the L2 review and selected recipients.",
                "Verify the final content, revision and controlled-document location.",
                "Select Approve to publish the final status and notify stakeholders.",
                "Or select Reject and enter a mandatory rejection comment.",
            ],
        ),
    ]
    for x, title, color, bullets in panels:
        c.setFillColor(LIGHT)
        c.setStrokeColor(color)
        c.roundRect(x, y - 260, panel_w, 250, 8, fill=1, stroke=1)
        c.setFillColor(color)
        c.roundRect(x, y - 42, panel_w, 32, 8, fill=1, stroke=0)
        c.rect(x, y - 42, panel_w, 8, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(FONT_BOLD, 10)
        c.drawString(x + 12, y - 31, title)
        yy = y - 60
        for number, bullet in enumerate(bullets, 1):
            c.setFillColor(color)
            c.circle(x + 17, yy - 7, 8, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont(FONT_BOLD, 7)
            c.drawCentredString(x + 17, yy - 9.5, str(number))
            yy = para(c, escape(bullet), x + 31, yy, panel_w - 43, SMALL) - 10
    y -= 282

    status_data = [
        [Paragraph("Status", TABLE_HEAD), Paragraph("Meaning", TABLE_HEAD), Paragraph("Next action", TABLE_HEAD)],
        [Paragraph("Pending", TABLE_TEXT), Paragraph("Awaiting L2 first review.", TABLE_TEXT), Paragraph("L2 reviews and first approves or rejects.", TABLE_TEXT)],
        [Paragraph("Pending Final Approval", TABLE_TEXT), Paragraph("L2 review completed.", TABLE_TEXT), Paragraph("L1/Admin approves or rejects.", TABLE_TEXT)],
        [Paragraph("Approved", TABLE_TEXT), Paragraph("Final approval completed.", TABLE_TEXT), Paragraph("Document is available for controlled use.", TABLE_TEXT)],
        [Paragraph("Rejected", TABLE_TEXT), Paragraph("Correction is required.", TABLE_TEXT), Paragraph("Uploader corrects and resubmits as required.", TABLE_TEXT)],
    ]
    y = table_at(c, status_data, LEFT, y, [126, 177, 216]) - 12
    callout(c, "Mandatory rejection comments", "State what is wrong, where it occurs and what the uploader must change. Avoid comments such as 'incorrect' without detail.", LEFT, y, CONTENT_W, "danger")
    end_page(c)


def tracking_page(c):
    y = start_page(c, 13, "6.4", "Track Approval Progress", "The timeline shows the current stage and completed workflow events.", TEAL)
    y = image_panel(c, tracking_top, LEFT, y, CONTENT_W, 382, "Figure 8 - Track Approvals summary and document timelines") - 10
    steps = [
        ("Start with My submissions", "Standard users see documents they uploaded."),
        ("Use All documents when authorized", "High-level users can switch scope to review all records."),
        ("Filter by status or search", "Narrow the list to pending, approved or rejected documents."),
        ("Read the timeline", "Each marker shows submission, first approval, final approval or rejection."),
        ("Open the source record", "Use the linked document or review action when follow-up is required."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, TEAL, compact=True)
    callout(c, "Status interpretation", "A green timeline is complete. A red marker identifies rejection. A neutral future marker means that stage has not yet occurred.", LEFT, y, CONTENT_W, "note")
    end_page(c)


def library_page(c):
    y = start_page(c, 14, "7.1", "Browse the Document Library", "The library organizes controlled content by category and access hierarchy.", BLUE)
    y = image_panel(c, library_focus, LEFT, y, CONTENT_W, 345, "Figure 9 - Document Library category browser") - 10
    steps = [
        ("Open Document Library", "Use the left navigation menu."),
        ("Choose a category", "Select QMS, Customer Procedures, Standard Manuals, Awards and other configured categories."),
        ("Drill into the hierarchy", "Choose the required QMS level, document group, plant, department or subfolder."),
        ("Open the file", "View inline when supported or download the approved source file."),
        ("Use your access level correctly", "L3 is limited to procedure-related groups; L4 is limited to checklists and checksheets."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, BLUE, compact=True)
    callout(c, "Controlled use", "Use the document from the library instead of a locally saved copy when the latest revision is required.", LEFT, y, CONTENT_W, "tip")
    end_page(c)


def procedures_page(c):
    y = start_page(c, 15, "7.2", "Open Procedures and Standard Manuals", "Category cards provide a shorter route to frequently used controlled documents.", ORANGE)
    gap = 14
    image_w = (CONTENT_W - gap) / 2
    y1 = image_panel(c, procedures_focus, LEFT, y, image_w, 220, "Figure 10 - Procedure category cards")
    y2 = image_panel(c, manuals_focus, LEFT + image_w + gap, y, image_w, 220, "Figure 11 - Standard Manual category cards")
    y = min(y1, y2) - 12
    steps = [
        ("Select the entry card", "Open the required procedure or manual family."),
        ("Choose plant and department where shown", "Use the repository hierarchy to reach the correct controlled location."),
        ("Select the document", "Open the approved file and confirm its revision before use."),
        ("Return through breadcrumbs", "Use the page breadcrumb or category browser to move back without losing context."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, ORANGE, compact=True)
    callout(c, "If a card is empty", "Confirm your QMS access level and selected plant/department. Then contact the document owner if the file is still unavailable.", LEFT, y, CONTENT_W, "warning")
    end_page(c)


def repositories_page(c):
    y = start_page(c, 16, "7.3", "Use Plant and Customer Repositories", "Use these views when the retrieval question begins with a plant, department or customer.", TEAL)
    gap = 14
    image_w = (CONTENT_W - gap) / 2
    y1 = image_panel(c, master_focus, LEFT, y, image_w, 215, "Figure 12 - Plant-based Master Records")
    y2 = image_panel(c, customer_focus, LEFT + image_w + gap, y, image_w, 215, "Figure 13 - Customer Records")
    y = min(y1, y2) - 12
    steps = [
        ("Master Records", "Choose a plant, then a department, and open the required controlled record."),
        ("Customer Records", "Choose the customer card, review the available files and open the required record."),
        ("Confirm context", "Check the plant, department, customer, document number and revision before use."),
        ("View only", "These repository pages are for retrieval. Use Upload Documents to submit new controlled files."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, TEAL, compact=True)
    callout(c, "Search strategy", "Use the dashboard for broad metadata search; use repository pages for structured browsing by ownership.", LEFT, y, CONTENT_W, "note")
    end_page(c)


def reports_page(c):
    y = start_page(c, 17, "8.1", "Read the Graphics Report", "Charts summarize approval health, ownership and upload activity.", PINK)
    y = image_panel(c, report_top, LEFT, y, CONTENT_W, 385, "Figure 14 - Graphics Report summary cards and charts") - 10
    steps = [
        ("Review KPI cards", "Check total, approved, pending, rejected and recent upload counts."),
        ("Read status distribution", "Use the doughnut chart to identify approval backlog and rejection volume."),
        ("Compare ownership", "Use plant, customer and department charts to locate concentration or imbalance."),
        ("Review upload trend", "Use the time-series chart to identify peaks and changes in submission volume."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, PINK, compact=True)
    callout(c, "Reporting caution", "Charts reflect the current database and active filters. Use exported lists or System Log for record-level audit evidence.", LEFT, y, CONTENT_W, "warning")
    end_page(c)


def revisions_page(c):
    y = start_page(c, 18, "8.2", "Review Revision History", "Revision History records what changed, who changed it and where the document belongs.", PURPLE)
    y = image_panel(c, revision_focus, LEFT, y, CONTENT_W, 344, "Figure 15 - Revision History list and filters") - 10
    steps = [
        ("Filter the history", "Select plant and department, then apply the filter."),
        ("Identify the document", "Use file name, document number and revision number."),
        ("Review ownership", "Confirm the person, plant, department and revision date."),
        ("Read the change summary", "Use the recorded summary to understand what changed between revisions."),
        ("Open the current approved file", "Use the Document Library for the controlled version currently in force."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, PURPLE, compact=True)
    callout(c, "Revision discipline", "Use a meaningful summary such as 'Updated torque specification in Section 4' rather than 'new version'.", LEFT, y, CONTENT_W, "tip")
    end_page(c)


def archive_page(c):
    y = start_page(c, 19, "9.1", "Manage Archived Documents", "Archive is restricted to Admin, Manager, Supervisor and Approver roles.", ORANGE)
    y = image_panel(c, archive_focus, LEFT, y, CONTENT_W, 370, "Figure 16 - Archive list with retained document metadata") - 10
    steps = [
        ("Understand soft delete", "Removing a document from the dashboard moves its record to Archive instead of immediately erasing it."),
        ("Locate the archived item", "Use the list, pagination and record metadata."),
        ("Retain for audit", "Keep archived records when the retention period or investigation is still active."),
        ("Permanently delete only when authorized", "Permanent deletion removes the archived record and is logged."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, ORANGE, compact=True)
    callout(c, "Destructive action", "Confirm retention requirements and the exact document before permanent deletion. This action cannot be reversed through the portal.", LEFT, y, CONTENT_W, "danger")
    end_page(c)


def system_log_page(c):
    y = start_page(c, 20, "9.2", "Use the System Log for Audit", "System Log is available to high-level roles and records significant user actions.", NAVY)
    y = image_panel(c, log_focus, LEFT, y, CONTENT_W, 356, "Figure 17 - System Log with action filters") - 10
    steps = [
        ("Choose an action filter", "Filter login, logout, upload, view, delete, approval, rejection, email and password events."),
        ("Review who and when", "Confirm timestamp, user name, employee ID or email and action type."),
        ("Read the details", "Use the details field to identify the affected document or activity."),
        ("Preserve audit context", "Capture the filtered result or export supporting records according to local audit practice."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, NAVY, compact=True)
    callout(c, "Audit principle", "Use System Log as the activity trail; use Revision History for version changes and Track Approvals for workflow progress.", LEFT, y, CONTENT_W, "note")
    end_page(c)


def people_page(c):
    y = start_page(c, 21, "9.3", "Review People and Access Assignments", "The People page is restricted to Admin users.", BLUE)
    y = image_panel(c, people_focus, LEFT, y, CONTENT_W, 430, "Figure 18 - People directory; sample personal details obscured") - 10
    steps = [
        ("Review level counts", "Confirm the number of L1, L2, L3 and L4 users."),
        ("Search or filter", "Filter by name, email, employee ID, department, role or QMS level."),
        ("Verify assignments", "Ensure L1 and L2 approvers are current and aligned with the approved responsibility matrix."),
        ("Correct access through the approved admin process", "Do not share accounts or use another user's approval privileges."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, BLUE, compact=True)
    callout(c, "Least privilege", "Assign only the role and QMS level required for the user's current responsibility. Review access when a person changes role or department.", LEFT, y, CONTENT_W, "warning")
    end_page(c)


def notifications_page(c):
    y = start_page(c, 22, "10.1", "Use In-Portal Notifications", "Notifications highlight uploads, required approvals, decisions and other events.", TEAL)
    y = image_panel(c, notifications_top, LEFT, y, CONTENT_W, 368, "Figure 19 - Notification panel opened from the top bar") - 10
    steps = [
        ("Open the bell icon", "The badge shows unread notifications."),
        ("Select a notification", "Use the linked item to open the related document or approval."),
        ("Mark items as read", "Clear individual notifications or use Mark all read."),
        ("Use email as a secondary channel", "Approval and decision emails supplement the in-portal notification; the portal remains the source of truth."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, TEAL, compact=True)
    callout(c, "If email is delayed", "Check the notification panel and Track Approvals. Report repeated email failures to the DMS administrator.", LEFT, y, CONTENT_W, "note")
    end_page(c)


def profile_logout_page(c):
    y = start_page(c, 23, "10.2", "Maintain Your Profile and Sign Out", "Keep personal details secure and end the session when work is complete.", GREEN)
    y = image_panel(c, profile_focus, LEFT, y, CONTENT_W, 365, "Figure 20 - Profile and activity page; sample personal details obscured") - 10
    steps = [
        ("Review account details", "Confirm name, employee ID, plant, department, role and QMS level."),
        ("Update the profile image if required", "Use an approved JPG, PNG, GIF or WebP image."),
        ("Change password securely", "Enter the current password, then a new password of at least 8 characters."),
        ("Review My Activity", "Use the personal activity list to identify unexpected access or actions."),
        ("Sign out", "Select Sign out in the top-right corner. The session is cleared and the login page reopens."),
    ]
    y = step_list(c, steps, LEFT, y, CONTENT_W, GREEN, compact=True)
    callout(c, "Shared workstation rule", "Always sign out before leaving the workstation. Closing only the browser tab may not be sufficient on a shared device.", LEFT, y, CONTENT_W, "danger")
    end_page(c)


def quick_reference_page(c):
    y = start_page(c, 24, "10.3", "Best Practices and Troubleshooting", "Use this page as a quick operating checklist.", ORANGE)
    gap = 14
    panel_w = (CONTENT_W - gap) / 2
    panels = [
        (
            LEFT,
            "Before submission",
            GREEN,
            [
                "Use the approved document-number format.",
                "Verify revision, plant, department and customer.",
                "Choose the exact library path.",
                "Add a specific revision summary.",
                "Open the final file before upload.",
            ],
        ),
        (
            LEFT + panel_w + gap,
            "Before approval",
            NAVY,
            [
                "Review the actual file and metadata.",
                "Confirm the current approval stage.",
                "L2 selects final recipients.",
                "L1 completes the final decision.",
                "Rejection comments must be actionable.",
            ],
        ),
    ]
    for x, title, color, bullets in panels:
        c.setFillColor(LIGHT)
        c.setStrokeColor(color)
        c.roundRect(x, y - 185, panel_w, 175, 7, fill=1, stroke=1)
        c.setFillColor(color)
        c.roundRect(x, y - 39, panel_w, 29, 7, fill=1, stroke=0)
        c.rect(x, y - 39, panel_w, 7, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(FONT_BOLD, 10)
        c.drawString(x + 12, y - 29, title)
        yy = y - 58
        for bullet in bullets:
            c.setFillColor(color)
            c.circle(x + 15, yy - 5, 3, fill=1, stroke=0)
            yy = para(c, escape(bullet), x + 26, yy, panel_w - 38, SMALL) - 6
    y -= 205

    troubleshooting = [
        [Paragraph("Issue", TABLE_HEAD), Paragraph("Check", TABLE_HEAD), Paragraph("Action", TABLE_HEAD)],
        [Paragraph("Cannot sign in", TABLE_TEXT), Paragraph("Email/GENID, password case and account status.", TABLE_TEXT), Paragraph("Use Forgot password or contact Admin.", TABLE_TEXT)],
        [Paragraph("Upload blocked", TABLE_TEXT), Paragraph("File type/size and all required metadata/path fields.", TABLE_TEXT), Paragraph("Correct the field marked in the form and retry.", TABLE_TEXT)],
        [Paragraph("Cannot approve", TABLE_TEXT), Paragraph("Document stage and your QMS level.", TABLE_TEXT), Paragraph("L2 handles Pending; L1/Admin handles Pending Final Approval.", TABLE_TEXT)],
        [Paragraph("Document not found", TABLE_TEXT), Paragraph("Filters, QMS access and library path.", TABLE_TEXT), Paragraph("Reset filters, browse the correct category, then contact owner.", TABLE_TEXT)],
        [Paragraph("Preview unavailable", TABLE_TEXT), Paragraph("File format and browser support.", TABLE_TEXT), Paragraph("Use the authorized download/open action.", TABLE_TEXT)],
        [Paragraph("Email not received", TABLE_TEXT), Paragraph("Notification panel and Track Approvals.", TABLE_TEXT), Paragraph("Continue in portal and report repeated email failures.", TABLE_TEXT)],
    ]
    y = table_at(c, troubleshooting, LEFT, y, [112, 194, 213]) - 12
    callout(
        c,
        "Support information to provide",
        "Share the page name, document number, time of issue, your role/QMS level and the exact error message. Do not send passwords or confidential file content in support messages.",
        LEFT,
        y,
        CONTENT_W,
        "warning",
    )
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 10)
    c.drawCentredString(W / 2, 47, "End of controlled user manual")
    end_page(c)


def build():
    pdf = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    pdf.setTitle("Smart DMS Portal User Manual")
    pdf.setAuthor("ZF Rane Automotive India PVT LTD - SGD")
    pdf.setSubject("Operating manual for the Smart DMS Document Management Portal")
    pdf.setKeywords("Smart DMS, user manual, document management, approval, QMS")

    cover_page(pdf)
    document_control_page(pdf)
    purpose_access_page(pdf)
    process_overview_page(pdf)
    login_page(pdf)
    register_page(pdf)
    dashboard_page(pdf)
    upload_files_page(pdf)
    upload_path_page(pdf)
    pending_items_page(pdf)
    review_workspace_page(pdf)
    decision_page(pdf)
    tracking_page(pdf)
    library_page(pdf)
    procedures_page(pdf)
    repositories_page(pdf)
    reports_page(pdf)
    revisions_page(pdf)
    archive_page(pdf)
    system_log_page(pdf)
    people_page(pdf)
    notifications_page(pdf)
    profile_logout_page(pdf)
    quick_reference_page(pdf)
    pdf.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
