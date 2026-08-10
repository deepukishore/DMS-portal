from pathlib import Path

import fitz


pdf_path = Path(r"C:\Users\deepu\OneDrive\Desktop\Rane\dms_portal_copy\output\pdf\DMS_Portal_User_Manual_Updated_Rev1.3.pdf")
output_dir = Path(r"C:\Users\deepu\OneDrive\Desktop\Rane\dms_portal_copy\tmp\manual_update_20260810\pdf-render")
output_dir.mkdir(parents=True, exist_ok=True)

document = fitz.open(pdf_path)
matrix = fitz.Matrix(2, 2)
for page_number, page in enumerate(document, start=1):
    pixmap = page.get_pixmap(matrix=matrix, alpha=False)
    pixmap.save(output_dir / f"page-{page_number:02d}.png")

print({"pages": len(document), "output_dir": str(output_dir)})
