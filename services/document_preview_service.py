import csv
import json
import mimetypes
import os
import zipfile
from xml.etree import ElementTree as ET


class DocumentPreviewService:
    """Builds safe in-page previews for uploaded documents."""

    INLINE_EXTENSIONS = {".pdf", ".htm", ".html"}
    TEXT_EXTENSIONS = {".txt", ".log", ".md", ".json", ".xml", ".yaml", ".yml", ".ini", ".cfg"}
    DELIMITED_EXTENSIONS = {".csv", ".tsv"}
    MAX_TEXT_CHARS = 60000
    MAX_TABLE_ROWS = 75
    MAX_TABLE_COLS = 20
    MAX_DOCX_BLOCKS = 200

    @staticmethod
    def build_preview(file_path, file_url):
        extension = os.path.splitext(file_path)[1].lower()
        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type and mime_type.startswith("image/"):
            return {"mode": "image", "url": file_url}
        if extension == ".pdf":
            return {"mode": "pdf", "url": file_url}
        if extension in {".htm", ".html"}:
            return {"mode": "html", "url": file_url}
        if extension == ".docx":
            return DocumentPreviewService._build_docx_preview(file_path)
        if extension == ".xlsx":
            return DocumentPreviewService._build_xlsx_preview(file_path)
        if extension in DocumentPreviewService.DELIMITED_EXTENSIONS:
            return DocumentPreviewService._build_delimited_preview(file_path, extension)
        if extension in DocumentPreviewService.TEXT_EXTENSIONS:
            return DocumentPreviewService._build_text_preview(file_path, extension)

        return {
            "mode": "unsupported",
            "message": "This file type does not have an in-page preview yet.",
        }

    @staticmethod
    def can_stream_inline(file_path):
        extension = os.path.splitext(file_path)[1].lower()
        mime_type, _ = mimetypes.guess_type(file_path)
        return (mime_type and mime_type.startswith("image/")) or extension in DocumentPreviewService.INLINE_EXTENSIONS

    @staticmethod
    def _build_text_preview(file_path, extension):
        with open(file_path, "r", encoding="utf-8", errors="replace") as file_handle:
            content = file_handle.read(DocumentPreviewService.MAX_TEXT_CHARS)

        if extension == ".json":
            try:
                content = json.dumps(json.loads(content), indent=2, ensure_ascii=True)
            except json.JSONDecodeError:
                pass

        return {
            "mode": "text",
            "content": content,
        }

    @staticmethod
    def _build_delimited_preview(file_path, extension):
        delimiter = "\t" if extension == ".tsv" else ","
        rows = []
        with open(file_path, "r", encoding="utf-8", errors="replace", newline="") as file_handle:
            reader = csv.reader(file_handle, delimiter=delimiter)
            for index, row in enumerate(reader):
                if index >= DocumentPreviewService.MAX_TABLE_ROWS:
                    break
                rows.append(row[: DocumentPreviewService.MAX_TABLE_COLS])

        return {
            "mode": "table",
            "sheets": [
                {
                    "name": "Preview",
                    "rows": rows,
                }
            ],
        }

    @staticmethod
    def _build_docx_preview(file_path):
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        blocks = []

        with zipfile.ZipFile(file_path) as archive:
            document_xml = archive.read("word/document.xml")

        root = ET.fromstring(document_xml)
        body = root.find("w:body", namespace)
        if body is None:
            return {"mode": "unsupported", "message": "The document preview could not be generated."}

        for child in list(body):
            if len(blocks) >= DocumentPreviewService.MAX_DOCX_BLOCKS:
                break

            tag_name = child.tag.rsplit("}", 1)[-1]
            if tag_name == "p":
                text = "".join(node.text or "" for node in child.findall(".//w:t", namespace)).strip()
                if text:
                    blocks.append({"type": "paragraph", "text": text})
            elif tag_name == "tbl":
                rows = []
                for row in child.findall(".//w:tr", namespace):
                    cells = []
                    for cell in row.findall("./w:tc", namespace):
                        cell_text = " ".join(
                            (node.text or "").strip()
                            for node in cell.findall(".//w:t", namespace)
                            if (node.text or "").strip()
                        ).strip()
                        cells.append(cell_text)
                    if cells:
                        rows.append(cells[: DocumentPreviewService.MAX_TABLE_COLS])
                    if len(rows) >= DocumentPreviewService.MAX_TABLE_ROWS:
                        break
                if rows:
                    blocks.append({"type": "table", "rows": rows})

        if not blocks:
            return {"mode": "unsupported", "message": "The document does not contain previewable text."}

        return {
            "mode": "docx",
            "blocks": blocks,
        }

    @staticmethod
    def _build_xlsx_preview(file_path):
        namespace_main = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        namespace_rel = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}

        with zipfile.ZipFile(file_path) as archive:
            shared_strings = DocumentPreviewService._read_shared_strings(archive)
            workbook = ET.fromstring(archive.read("xl/workbook.xml"))
            relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))

            rel_map = {}
            for relationship in relationships.findall("rel:Relationship", namespace_rel):
                rel_map[relationship.attrib["Id"]] = relationship.attrib["Target"]

            sheets = []
            for sheet in workbook.findall("main:sheets/main:sheet", namespace_main):
                rel_id = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                target = rel_map.get(rel_id, "")
                if not target:
                    continue

                sheet_path = target if target.startswith("xl/") else f"xl/{target}"
                rows = DocumentPreviewService._read_sheet_rows(archive, sheet_path, shared_strings)
                if rows:
                    sheets.append({"name": sheet.attrib.get("name", "Sheet"), "rows": rows})

            if not sheets:
                return {"mode": "unsupported", "message": "The workbook does not contain previewable cells."}

            return {
                "mode": "table",
                "sheets": sheets,
            }

    @staticmethod
    def _read_shared_strings(archive):
        try:
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        except KeyError:
            return []

        namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        shared_strings = []
        for string_item in root.findall("main:si", namespace):
            text = "".join(node.text or "" for node in string_item.findall(".//main:t", namespace))
            shared_strings.append(text)
        return shared_strings

    @staticmethod
    def _read_sheet_rows(archive, sheet_path, shared_strings):
        namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        root = ET.fromstring(archive.read(sheet_path))
        rows = []

        for row in root.findall(".//main:sheetData/main:row", namespace):
            row_values = []
            last_column_index = -1
            for cell in row.findall("main:c", namespace):
                cell_ref = cell.attrib.get("r", "")
                column_index = DocumentPreviewService._column_index(cell_ref)
                if column_index > last_column_index + 1:
                    row_values.extend([""] * (column_index - last_column_index - 1))

                row_values.append(DocumentPreviewService._cell_value(cell, namespace, shared_strings))
                last_column_index = column_index

                if len(row_values) >= DocumentPreviewService.MAX_TABLE_COLS:
                    break

            rows.append(row_values[: DocumentPreviewService.MAX_TABLE_COLS])
            if len(rows) >= DocumentPreviewService.MAX_TABLE_ROWS:
                break

        return rows

    @staticmethod
    def _cell_value(cell, namespace, shared_strings):
        cell_type = cell.attrib.get("t")
        value_node = cell.find("main:v", namespace)

        if cell_type == "inlineStr":
            return "".join(node.text or "" for node in cell.findall(".//main:t", namespace))
        if value_node is None:
            return ""

        raw_value = value_node.text or ""
        if cell_type == "s":
            try:
                return shared_strings[int(raw_value)]
            except (IndexError, ValueError):
                return raw_value
        if cell_type == "b":
            return "TRUE" if raw_value == "1" else "FALSE"
        return raw_value

    @staticmethod
    def _column_index(cell_ref):
        column_letters = "".join(character for character in cell_ref if character.isalpha()).upper()
        if not column_letters:
            return 0

        index = 0
        for character in column_letters:
            index = (index * 26) + (ord(character) - 64)
        return max(index - 1, 0)
