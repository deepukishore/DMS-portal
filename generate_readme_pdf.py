from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors

root = Path(__file__).resolve().parent
md_path = root / 'README.md'
out_path = root / 'README.pdf'
text = md_path.read_text(encoding='utf-8')

styles = getSampleStyleSheet()
if 'Title' not in styles:  # pragma: no cover
    styles.add(ParagraphStyle(name='Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, spaceAfter=10, textColor=colors.HexColor('#1f2937')))
if 'Body' not in styles:  # pragma: no cover
    styles.add(ParagraphStyle(name='Body', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=13, alignment=TA_JUSTIFY, spaceAfter=6))
if 'Bullet' not in styles:  # pragma: no cover
    styles.add(ParagraphStyle(name='Bullet', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=13, leftIndent=12, spaceAfter=4))
story = []

for line in text.splitlines():
    if not line.strip():
        story.append(Spacer(1, 6))
    elif line.startswith('# '):
        story.append(Paragraph(line[2:].strip(), styles['Title']))
    elif line.startswith('## '):
        story.append(Paragraph(line[3:].strip(), styles['Heading2']))
    elif line.startswith('### '):
        story.append(Paragraph(line[4:].strip(), styles['Heading3']))
    elif line.startswith('- '):
        story.append(Paragraph(line[2:].strip(), styles['Bullet']))
    elif line.startswith('```') or line.startswith('---') or line.startswith('|'):
        continue
    else:
        story.append(Paragraph(line.strip(), styles['Body']))

pdf = SimpleDocTemplate(str(out_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
pdf.build(story)
print(f'Created {out_path}')
