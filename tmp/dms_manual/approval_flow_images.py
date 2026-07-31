from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1600
HEIGHT = 860

BG = "#F1F5F8"
WHITE = "#FFFFFF"
INK = "#17212D"
MUTED = "#607184"
BLUE = "#006DB6"
NAVY = "#0B356B"
LINE = "#C8D5E1"
CARD = "#EAF0F4"
GREEN = "#159447"
GREEN_PALE = "#EAF7EE"
RED = "#D23B36"
RED_PALE = "#FDECEC"
AMBER = "#E59A00"
AMBER_PALE = "#F7EED8"


def _font(size, bold=False):
    path = Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf")
    return ImageFont.truetype(str(path), size)


def _text(draw, xy, value, size, fill=INK, bold=False, anchor=None):
    draw.text(xy, value, font=_font(size, bold), fill=fill, anchor=anchor)


def _wrap(draw, value, size, max_width, bold=False):
    font = _font(size, bold)
    words = value.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _wrapped_text(draw, xy, value, size, max_width, fill=INK, bold=False, spacing=7):
    x, y = xy
    for line in _wrap(draw, value, size, max_width, bold):
        _text(draw, (x, y), line, size, fill, bold)
        y += size + spacing
    return y


def _card(draw, box, radius=12, fill=WHITE, outline=LINE, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def _section_title(draw, x, y, title, subtitle=""):
    draw.rectangle((x, y + 2, x + 5, y + 31), fill=BLUE)
    _text(draw, (x + 17, y), title, 25, INK, True)
    if subtitle:
        _text(draw, (x + 17, y + 42), subtitle, 18, MUTED)


def _header(draw):
    _card(draw, (45, 28, WIDTH - 45, 112), radius=10)
    draw.ellipse((70, 48, 115, 93), outline=BLUE, width=4)
    _text(draw, (92, 70), "ZF", 20, BLUE, True, anchor="mm")
    draw.line((130, 46, 130, 95), fill=BLUE, width=2)
    _text(draw, (150, 59), "Rane", 24, NAVY, True)
    _text(draw, (228, 61), "Document Management System", 20, INK, True)
    _text(draw, (555, 63), "SGD", 16, BLUE, True)


def _metadata_card(draw, x, y, label, value, width=300, height=78):
    _card(draw, (x, y, x + width, y + height), radius=8, fill=CARD)
    _text(draw, (x + 18, y + 16), label.upper(), 15, MUTED)
    _wrapped_text(draw, (x + 18, y + 41), value, 17, width - 36, INK, True, spacing=3)


def _email_table(draw, x, y, rows, label_width=165, value_width=470):
    yy = y
    for label, value in rows:
        _text(draw, (x, yy), label, 18, INK, True)
        _wrapped_text(draw, (x + label_width, yy), value, 18, value_width, INK, False, spacing=4)
        yy += 43
    return yy


def build_approval_request(output_path):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    _header(draw)

    _text(draw, (45, 147), "APPROVAL REQUEST", 17, BLUE, True)
    _text(draw, (45, 178), "Industry_4.O_20260731102439.pptx", 34, INK, True)
    _text(draw, (45, 220), "Documents move through first-stage review and final approval or rejection.", 18, MUTED)
    draw.rounded_rectangle((1410, 147, 1547, 180), radius=17, fill=AMBER_PALE)
    draw.ellipse((1424, 158, 1434, 168), fill=AMBER)
    _text(draw, (1443, 153), "PENDING", 16, "#A36A00", True)

    _card(draw, (45, 260, 1165, 825), radius=10)
    _section_title(draw, 72, 288, "Preview", "Review the document below and make your decision.")
    _card(draw, (930, 280, 1138, 326), radius=7)
    _text(draw, (1034, 303), "Open file in new tab", 16, MUTED, anchor="mm")

    _card(draw, (72, 375, 1138, 793), radius=7, fill="#FDFDFD", outline="#2D333A", width=6)
    _text(draw, (200, 465), "Slide 1", 32, "#000000", True)
    _text(draw, (200, 522), "Industry 4.0", 24, "#000000")
    _text(draw, (200, 559), "Core Learning & Implementation Areas", 23, "#000000")
    _wrapped_text(
        draw,
        (200, 596),
        "APM / OEE Tracking - Digitalization - Vision System - Energy Management",
        22,
        760,
        "#000000",
    )

    _card(draw, (1190, 260, 1555, 825), radius=10)
    _section_title(draw, 1217, 288, "Document Details")
    metadata = [
        ("Document number", "IND1"),
        ("Revision number", "Rev.00"),
        ("Category", "qms"),
        ("Uploaded by", "Diva Chandra (U001)"),
        ("Plant", "P2 - Guduvachery Plant"),
    ]
    yy = 385
    for label, value in metadata:
        _metadata_card(draw, 1217, yy, label, value, width=310, height=72)
        yy += 83

    image.save(output_path, quality=96)


def build_first_stage(output_path):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    _card(draw, (35, 30, 825, 680), radius=12)
    _text(draw, (72, 66), "Approval request: Industry_4.O_20260731102439.pptx", 27, INK)
    draw.ellipse((72, 116, 130, 174), fill="#E5E8EC")
    _text(draw, (101, 145), "A", 25, WHITE, True, anchor="mm")
    _text(draw, (150, 118), "approver@example.com", 20, INK, True)
    _text(draw, (150, 146), "to reviewer", 16, MUTED)
    _text(draw, (72, 201), "A new document is waiting for approval.", 19, INK)
    rows = [
        ("File", "Industry_4.O_20260731102439.pptx"),
        ("Uploaded by", "Diva Chandra (U001)"),
        ("Plant", "P2 - Guduvachery Plant"),
        ("Department", "QAD - Quality Assurance Department"),
        ("Customer", "Internal"),
        ("Document number", "IND1"),
        ("Revision number", "Rev.00"),
        ("Category", "qms"),
        ("Status", "Pending"),
    ]
    yy = _email_table(draw, 82, 250, rows, label_width=175, value_width=510)
    draw.rounded_rectangle((82, yy + 5, 280, yy + 57), radius=8, fill=AMBER)
    _text(draw, (181, yy + 31), "Review document", 18, "#111111", True, anchor="mm")

    _card(draw, (850, 30, 1565, 680), radius=12)
    _section_title(draw, 885, 70, "Decision", "The designated first-stage reviewer completes the initial review.")
    _text(draw, (885, 166), "Selected recipients after final approval", 18, MUTED, True)
    _card(draw, (885, 200, 1530, 280), radius=7, fill="#FAFCFD")
    _text(draw, (905, 219), "recipient@example.com", 18, MUTED)
    _text(draw, (885, 311), "Rejection comments are required when rejecting.", 18, MUTED, True)
    _card(draw, (885, 345, 1530, 425), radius=7, fill="#FAFCFD")
    _text(draw, (905, 364), "Explain exactly what must be corrected.", 18, MUTED)
    draw.rounded_rectangle((885, 463, 1530, 525), radius=8, fill=GREEN_PALE, outline="#9EDCAE", width=2)
    _text(draw, (1208, 494), "Approve first stage", 22, GREEN, True, anchor="mm")
    draw.rounded_rectangle((885, 545, 1530, 607), radius=8, fill=RED_PALE, outline="#F1AAA5", width=2)
    _text(draw, (1208, 576), "Reject", 22, RED, True, anchor="mm")

    _card(draw, (235, 718, 1365, 830), radius=10, fill=WHITE, outline=GREEN, width=3)
    _text(draw, (800, 750), "First approval accepted. Document moved to final approval.", 27, INK, True, anchor="mm")
    _text(draw, (800, 790), "Status updated on this page.", 19, MUTED, anchor="mm")

    image.save(output_path, quality=96)


def build_final_stage(output_path):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    _card(draw, (35, 30, 790, 610), radius=12)
    _text(draw, (70, 64), "Approval request: Industry_4.O_20260731102439.pptx", 25, INK)
    _text(draw, (70, 110), "A new document is waiting for final approval.", 18, INK)
    rows = [
        ("File", "Industry_4.O_20260731102439.pptx"),
        ("Uploaded by", "Diva Chandra (U001)"),
        ("Plant", "P2 - Guduvachery Plant"),
        ("Department", "QAD - Quality Assurance Department"),
        ("Customer", "Internal"),
        ("Document number", "IND1"),
        ("Revision number", "Rev.00"),
        ("Category", "qms"),
        ("Status", "Pending Final Approval"),
    ]
    yy = _email_table(draw, 70, 158, rows, label_width=175, value_width=455)
    draw.rounded_rectangle((70, yy + 3, 268, yy + 55), radius=8, fill=AMBER)
    _text(draw, (169, yy + 29), "Review document", 18, "#111111", True, anchor="mm")

    _card(draw, (825, 30, 1565, 265), radius=12, fill=WHITE, outline=GREEN, width=3)
    draw.line((1175, 78, 1189, 92), fill=GREEN, width=6)
    draw.line((1189, 92, 1217, 62), fill=GREEN, width=6)
    _text(draw, (1195, 137), "Document marked as Approved.", 28, INK, True, anchor="mm")
    _text(draw, (1195, 178), "Uploader notified via email.", 23, INK, True, anchor="mm")
    _text(draw, (1195, 220), "Status updated on this page.", 18, MUTED, anchor="mm")

    _card(draw, (825, 295, 1565, 830), radius=12)
    _text(draw, (860, 330), "Document approved and shared", 26, INK, True)
    _text(draw, (860, 375), "recipient@example.com", 18, INK, True)
    _text(draw, (860, 410), "A document received final approval and has been shared with you.", 18, INK)
    final_rows = [
        ("File", "Industry_4.O_20260731102439.pptx"),
        ("Plant", "P2 - Guduvachery Plant"),
        ("Department", "QAD - Quality Assurance Department"),
        ("Document number", "IND1"),
        ("Revision number", "Rev.00"),
        ("First approver", "First-stage approver"),
        ("Final approver", "Final approver"),
        ("Approved at", "2026-07-31 11:23:13"),
    ]
    _email_table(draw, 860, 458, final_rows, label_width=175, value_width=460)

    image.save(output_path, quality=96)


def build_all(output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "approval_request": output_dir / "approval_request_walkthrough.png",
        "first_stage": output_dir / "first_stage_decision.png",
        "final_stage": output_dir / "final_stage_notifications.png",
    }
    build_approval_request(paths["approval_request"])
    build_first_stage(paths["first_stage"])
    build_final_stage(paths["final_stage"])
    return paths


if __name__ == "__main__":
    build_all(Path(__file__).resolve().parent / "manual_assets")
