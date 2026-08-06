from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors

root = Path(__file__).resolve().parent
out_path = root / 'USER_MANUAL.pdf'

styles = getSampleStyleSheet()
if 'Title' not in styles:
    styles.add(ParagraphStyle(name='Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, spaceAfter=10, textColor=colors.HexColor('#1f2937')))
if 'Subtitle' not in styles:
    styles.add(ParagraphStyle(name='Subtitle', parent=styles['BodyText'], fontName='Helvetica', fontSize=11, leading=14, textColor=colors.HexColor('#4b5563'), spaceAfter=8))
if 'Body' not in styles:
    styles.add(ParagraphStyle(name='Body', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=13, alignment=TA_JUSTIFY, spaceAfter=6))
if 'Bullet' not in styles:
    styles.add(ParagraphStyle(name='Bullet', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=13, leftIndent=12, spaceAfter=4))
if 'Section' not in styles:
    styles.add(ParagraphStyle(name='Section', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=14, spaceBefore=8, spaceAfter=6, textColor=colors.HexColor('#111827')))

story = []
story.append(Paragraph('Smart DMS User Manual', styles['Title']))
story.append(Paragraph('Guide for end users of the document management portal', styles['Subtitle']))
story.append(Spacer(1, 8))

sections = [
    ("1. Login and Access", [
        "Open the app in your browser using the provided URL.",
        "Sign in with your email or employee ID and password.",
        "If you forgot your password, use the Forgot Password option to reset it.",
        "After login, you will be taken to the dashboard."
    ]),
    ("2. Dashboard Overview", [
        "The dashboard shows all documents available to you.",
        "Use the search box and filters to find documents quickly.",
        "You can view the status of each document such as Approved, Pending, or Rejected.",
        "Use the star icon to bookmark documents you use often."
    ]),
    ("3. Uploading Documents", [
        "Go to the Upload page and choose the relevant category and folder path.",
        "Select the document file and enter the required details.",
        "Submit the document to send it for review and approval."
    ]),
    ("4. Reviewing and Approving", [
        "Approvers can open pending items from the approval queue.",
        "Review the document, check the metadata, and approve or reject it.",
        "Approved items move forward, while rejected items are returned for correction."
    ]),
    ("5. Document Library", [
        "The document library helps you browse documents by category and folder.",
        "Use it to locate documents without searching the full dashboard."
        "You can open documents directly from the library view."
    ]),
    ("6. Revision History and Archive", [
        "Use Revision History to track changes made to a document over time.",
        "Archive is used to view documents that have been moved out of active use."
    ]),
    ("7. Best Practices", [
        "Use clear file names and complete document details.",
        "Check the correct category and plant before uploading.",
        "Contact your administrator if you cannot access a document or feature."
    ]),
]

for title, bullets in sections:
    story.append(Paragraph(title, styles['Section']))
    items = []
    for bullet in bullets:
        items.append(ListItem(Paragraph(bullet, styles['Bullet'])))
    story.append(ListFlowable(items, bulletType='bullet', leftIndent=18, bulletFontName='Helvetica', bulletFontSize=10))
    story.append(Spacer(1, 4))

story.append(Spacer(1, 8))
story.append(Paragraph('Support', styles['Section']))
story.append(Paragraph('For login issues, document access problems, or approval questions, contact the DMS administrator or your team lead.', styles['Body']))

pdf = SimpleDocTemplate(str(out_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
pdf.build(story)
print(f'Created {out_path}')
