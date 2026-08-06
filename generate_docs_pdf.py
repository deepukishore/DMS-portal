from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors

root = Path(__file__).resolve().parent


def build_pdf(source_name: str, output_name: str, title: str):
    source_path = root / source_name
    output_path = root / output_name
    text = source_path.read_text(encoding='utf-8')
    styles = getSampleStyleSheet()
    if 'Title' not in styles:
        styles.add(ParagraphStyle(name='Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, spaceAfter=10, textColor=colors.HexColor('#111827')))
    if 'Body' not in styles:
        styles.add(ParagraphStyle(name='Body', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=13, alignment=TA_JUSTIFY, spaceAfter=6))
    if 'Bullet' not in styles:
        styles.add(ParagraphStyle(name='Bullet', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=13, leftIndent=12, spaceAfter=4))
    if 'Section' not in styles:
        styles.add(ParagraphStyle(name='Section', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=14, spaceBefore=8, spaceAfter=6, textColor=colors.HexColor('#1f2937')))

    story = []
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 6))

    for line in text.splitlines():
        if not line.strip():
            story.append(Spacer(1, 4))
        elif line.startswith('# '):
            continue
        elif line.startswith('## '):
            story.append(Paragraph(line[3:].strip(), styles['Section']))
        elif line.startswith('- '):
            story.append(Paragraph(line[2:].strip(), styles['Bullet']))
        elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. ') or line.startswith('4. ') or line.startswith('5. ') or line.startswith('6. ') or line.startswith('7. ') or line.startswith('8. '):
            story.append(Paragraph(line.strip(), styles['Body']))
        elif line.startswith('```'):
            continue
        else:
            story.append(Paragraph(line.strip(), styles['Body']))

    doc = SimpleDocTemplate(str(output_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    doc.build(story)
    print(f'Created {output_path}')


build_pdf('README.md', 'README.pdf', 'Smart DMS Documentation')
build_pdf('USER_MANUAL.md', 'USER_MANUAL.pdf', 'Smart DMS User Manual')
