import os
import re
from datetime import datetime

from itsdangerous import URLSafeSerializer
from werkzeug.utils import secure_filename

from data.customers import customer_query_values, normalize_customer
from data.departments import normalize_department
from data.document_categories import infer_document_category
from database import get_connection, is_mysql
from services.pdf_conversion_service import convert_to_pdf, is_allowed_file


class DocumentService:
    """Manages document records used across dashboard and approvals."""

    PENDING_APPROVAL_STATUSES = {"Pending", "Pending Final Approval", "Hold"}
    DOCUMENT_NUMBER_PREFIX = "ZRAI-DOC"
    _DOCUMENT_NUMBER_PATTERN = re.compile(
        r"^ZRAI-DOC-(P[1-4])-(\d{4})-(\d+)$",
        re.IGNORECASE,
    )

    @staticmethod
    def _document_plant_code(plant):
        match = re.match(r"^\s*(P[1-4])(?=\s*(?:-|$))", str(plant or ""), re.IGNORECASE)
        if not match:
            raise ValueError("Please select a valid plant (P1, P2, P3, or P4).")
        return match.group(1).upper()

    @staticmethod
    def format_document_number(plant, file_number, year=None):
        """Build a controlled document number from a plant and numeric file number."""
        plant_id = DocumentService._document_plant_code(plant)
        document_year = int(year or datetime.now().year)
        if document_year < 1000 or document_year > 9999:
            raise ValueError("Document year must contain four digits.")
        value = str(file_number or "").strip()
        if not re.fullmatch(r"\d+", value) or int(value) < 1:
            raise ValueError("File number must contain digits only and be at least 001.")
        return (
            f"{DocumentService.DOCUMENT_NUMBER_PREFIX}-{plant_id}-"
            f"{document_year:04d}-{int(value):03d}"
        )

    @staticmethod
    def validate_document_number(document_number, plant=None):
        """Validate and normalize a full controlled document number."""
        value = str(document_number or "").strip().upper()
        match = DocumentService._DOCUMENT_NUMBER_PATTERN.fullmatch(value)
        if not match or int(match.group(3)) < 1:
            raise ValueError(
                "Enter the complete document number, for example "
                "ZRAI-DOC-P1-2026-001."
            )

        number_plant = match.group(1).upper()
        if plant and number_plant != DocumentService._document_plant_code(plant):
            raise ValueError("The document number must match the selected plant.")

        return DocumentService.format_document_number(
            number_plant,
            match.group(3),
            year=int(match.group(2)),
        )

    @staticmethod
    def _max_persisted_document_number(cursor, plant_id, document_year):
        prefix = f"{DocumentService.DOCUMENT_NUMBER_PREFIX}-{plant_id}-{document_year:04d}-"
        cursor.execute(
            "SELECT document_number FROM documents WHERE document_number LIKE ?",
            (f"{prefix}%",),
        )
        highest = 0
        for row in cursor.fetchall():
            value = row.get("document_number") if isinstance(row, dict) else row["document_number"]
            match = DocumentService._DOCUMENT_NUMBER_PATTERN.fullmatch(value or "")
            if (
                match
                and match.group(1).upper() == plant_id
                and int(match.group(2)) == document_year
            ):
                highest = max(highest, int(match.group(3)))
        return highest

    @staticmethod
    def _reserve_document_number(cursor, plant):
        """Atomically reserve the next number for a plant in the active transaction."""
        plant_id = DocumentService._document_plant_code(plant)
        document_year = datetime.now().year
        sequence_key = f"{plant_id}-{document_year:04d}"
        insert_sql = (
            "INSERT IGNORE INTO document_number_sequences (plant_code, last_number) VALUES (?, 0)"
            if is_mysql()
            else "INSERT OR IGNORE INTO document_number_sequences (plant_code, last_number) VALUES (?, 0)"
        )
        cursor.execute(insert_sql, (sequence_key,))
        select_sql = "SELECT last_number FROM document_number_sequences WHERE plant_code = ?"
        if is_mysql():
            select_sql += " FOR UPDATE"
        cursor.execute(select_sql, (sequence_key,))
        row = cursor.fetchone()
        stored_number = int(row.get("last_number", 0) if isinstance(row, dict) else row["last_number"])
        next_number = max(
            stored_number,
            DocumentService._max_persisted_document_number(
                cursor,
                plant_id,
                document_year,
            ),
        ) + 1
        cursor.execute(
            "UPDATE document_number_sequences SET last_number = ? WHERE plant_code = ?",
            (next_number, sequence_key),
        )
        return DocumentService.format_document_number(
            plant_id,
            next_number,
            year=document_year,
        )

    @staticmethod
    def peek_next_document_number(plant):
        """Return an advisory next number for the upload form without reserving it."""
        plant_id = DocumentService._document_plant_code(plant)
        document_year = datetime.now().year
        sequence_key = f"{plant_id}-{document_year:04d}"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT last_number FROM document_number_sequences WHERE plant_code = ?",
                (sequence_key,),
            )
            row = cursor.fetchone()
            stored_number = (
                int(row.get("last_number", 0) if isinstance(row, dict) else row["last_number"])
                if row else 0
            )
            next_number = max(
                stored_number,
                DocumentService._max_persisted_document_number(
                    cursor,
                    plant_id,
                    document_year,
                ),
            ) + 1
            return DocumentService.format_document_number(
                plant_id,
                next_number,
                year=document_year,
            )
        finally:
            conn.close()

    @staticmethod
    def is_pending_status(status):
        return (status or "Pending") in DocumentService.PENDING_APPROVAL_STATUSES

    @staticmethod
    def count_pending(records):
        return sum(1 for record in records if DocumentService.is_pending_status(record.get("approval_status")))

    @staticmethod
    def filter_by_status(records, status):
        if not status:
            return records
        if status == "Pending":
            return [
                record for record in records
                if (record.get("approval_status") or "Pending")
                in {"Pending", "Pending Final Approval"}
            ]
        return [
            record for record in records
            if (record.get("approval_status") or "Pending") == status
        ]

    @staticmethod
    def _sorted(records):
        return sorted(
            records,
            key=lambda record: (record.get("uploaded_at", ""), record.get("id", -1)),
            reverse=True,
        )

    @staticmethod
    def _normalize_record(record):
        record["department"] = normalize_department(record.get("department", ""))
        record["customer"] = normalize_customer(record.get("customer", ""))
        record["category"] = infer_document_category(record)
        return record

    @staticmethod
    def _parse_search(search):
        raw_search = (search or "").strip()
        date_matches = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", raw_search)
        cleaned = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " ", raw_search)
        cleaned = re.sub(r"\bto\b", " ", cleaned, flags=re.IGNORECASE)
        tokens = [token.strip().lower() for token in cleaned.split() if token.strip()]

        date_from = ""
        date_to = ""
        if len(date_matches) >= 2:
            ordered = sorted(date_matches[:2])
            date_from, date_to = ordered[0], ordered[1]
        elif len(date_matches) == 1:
            date_from = date_to = date_matches[0]

        return {
            "raw": raw_search.lower(),
            "tokens": tokens,
            "date_from": date_from,
            "date_to": date_to,
        }

    @staticmethod
    def _field_values(record):
        return {
            "file_name": f'{record.get("file_name", "")} {record.get("original_file_name", "")}'.strip(),
            "uploader": f'{record.get("name", "")} {record.get("user_id", "")}'.strip(),
            "customer": record.get("customer", ""),
            "department": record.get("department", ""),
            "revision_number": record.get("revision_number", ""),
            "document_number": record.get("document_number", ""),
            "category": record.get("category", ""),
            "uploaded_at": record.get("uploaded_at", ""),
            "plant": record.get("plant", ""),
            "status": record.get("approval_status", ""),
            "version": str(record.get("current_version", "")),
        }

    @staticmethod
    def _record_search_score(record, parsed_search):
        tokens = parsed_search["tokens"]
        date_from = parsed_search["date_from"]
        date_to = parsed_search["date_to"]
        uploaded_at = (record.get("uploaded_at") or "")[:10]

        if date_from and date_to and uploaded_at:
            if uploaded_at < date_from or uploaded_at > date_to:
                return 0
        elif date_from and date_from == date_to and uploaded_at:
            if uploaded_at != date_from:
                return 0

        if not tokens:
            return 1 if (date_from or parsed_search["raw"]) else 0

        weights = {
            "file_name": 18,
            "document_number": 16,
            "revision_number": 14,
            "uploader": 12,
            "customer": 10,
            "department": 9,
            "category": 8,
            "uploaded_at": 7,
            "plant": 6,
            "status": 5,
            "version": 4,
        }

        score = 0
        field_values = {
            key: (value or "").lower()
            for key, value in DocumentService._field_values(record).items()
        }
        raw_match_text = " ".join(field_values.values())

        for token in tokens:
            token_score = 0
            for field_name, field_value in field_values.items():
                if not field_value:
                    continue
                weight = weights[field_name]
                if field_value == token:
                    token_score = max(token_score, weight * 12)
                elif field_value.startswith(token):
                    token_score = max(token_score, weight * 8)
                elif token in field_value:
                    token_score = max(token_score, weight * 4)
            if token_score == 0 and token not in raw_match_text:
                continue
            score += token_score

        if parsed_search["raw"] and parsed_search["raw"] in raw_match_text:
            score += 25

        return score

    @staticmethod
    def get_all_documents(search="", plant="", department="", customer="", access_department=""):
        customer = normalize_customer(customer) if customer else customer
        access_department = normalize_department(access_department) if access_department else access_department
        # access_department is the hard security boundary — it always wins over the UI filter
        effective_department = access_department if access_department else (normalize_department(department) if department else "")
        conn = get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM documents WHERE 1=1'
        params = []
        if plant:
            query += ' AND plant = ?'
            params.append(plant)
        if effective_department:
            query += ' AND department = ?'
            params.append(effective_department)
        if customer:
            customer_values = customer_query_values(customer)
            placeholders = ','.join('?' for _ in customer_values)
            query += f' AND customer IN ({placeholders})'
            params.extend(customer_values)
        
        cursor.execute(query, params)
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        records = [DocumentService._normalize_record(record) for record in records]

        if not search:
            return DocumentService._sorted(records)

        parsed_search = DocumentService._parse_search(search)
        ranked_records = []
        for record in records:
            score = DocumentService._record_search_score(record, parsed_search)
            if score > 0:
                ranked_records.append({**record, "_search_score": score})

        ranked_records.sort(
            key=lambda record: (
                record.get("_search_score", 0),
                record.get("uploaded_at", ""),
                record.get("id", -1),
            ),
            reverse=True,
        )
        return ranked_records

    @staticmethod
    def get_documents_by_ids(doc_ids, access_department=""):
        valid_ids = [int(doc_id) for doc_id in doc_ids if str(doc_id).strip().isdigit()]
        if not valid_ids:
            return []

        access_department = normalize_department(access_department) if access_department else access_department
        placeholders = ",".join("?" for _ in valid_ids)
        query = f"SELECT * FROM documents WHERE id IN ({placeholders})"
        params = list(valid_ids)
        if access_department:
            query += " AND department = ?"
            params.append(access_department)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return [DocumentService._normalize_record(row) for row in rows]

    @staticmethod
    def get_document_by_id(doc_id, access_department=""):
        records = DocumentService.get_documents_by_ids([doc_id], access_department=access_department)
        return records[0] if records else None

    @staticmethod
    def get_document_by_document_number(document_number, access_department=""):
        """Return the latest document matching an exact controlled document number."""
        normalized_number = DocumentService.validate_document_number(document_number)
        access_department = normalize_department(access_department) if access_department else ""
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM documents WHERE UPPER(document_number) = ?"
        params = [normalized_number]
        if access_department:
            query += " AND department = ?"
            params.append(access_department)
        query += " ORDER BY id DESC LIMIT 1"
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        return DocumentService._normalize_record(dict(row)) if row else None

    @staticmethod
    def get_document_by_file_name(file_name, access_department=""):
        access_department = normalize_department(access_department) if access_department else access_department
        conn = get_connection()
        cursor = conn.cursor()
        query = '''
            SELECT * FROM documents
            WHERE (file_name = ? OR original_file_name = ? OR pdf_file_name = ?)
        '''
        params = [file_name, file_name, file_name]
        if access_department:
            query += ' AND department = ?'
            params.append(access_department)
        query += ' ORDER BY uploaded_at DESC, id DESC LIMIT 1'
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        return DocumentService._normalize_record(dict(row)) if row else None

    @staticmethod
    def delete_document(doc_id):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE id = ?', (int(doc_id),))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None, "Document not found."
        
        removed = dict(row)
        cursor.execute('DELETE FROM documents WHERE id = ?', (int(doc_id),))
        
        # Move to archive
        cursor.execute('''INSERT INTO archive 
            (timestamp, file_name, plant, department, customer, uploaded_by, user_id, approval_status, original_upload_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), removed["file_name"], removed["plant"],
             removed["department"], removed.get("customer", ""), removed.get("name", ""),
             removed.get("user_id", ""), removed.get("approval_status", ""), removed.get("uploaded_at", ""))
        )
        
        conn.commit()
        conn.close()
        return removed, None

    @staticmethod
    def save_upload(
        file,
        user_name,
        user_id,
        user_email,
        plant,
        department,
        customer,
        upload_folder,
        document_number,
        revision_number,
        category,
    ):
        department = normalize_department(department)
        customer = normalize_customer(customer)
        filename = secure_filename(file.filename or "")
        if not filename:
            return None, "Invalid file name."

        if not is_allowed_file(filename):
            return None, f"File type not allowed. Accepted: PDF, Word, Excel, PowerPoint."

        base, extension = os.path.splitext(filename)
        timestamp = datetime.now()
        unique_name = f"{base}_{timestamp.strftime('%Y%m%d%H%M%S')}{extension}"
        orig_path = os.path.join(upload_folder, unique_name)
        file.save(orig_path)

        # Convert to PDF for viewing
        pdf_name = f"{base}_{timestamp.strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_path = os.path.join(upload_folder, pdf_name)
        _, conv_err = convert_to_pdf(orig_path, pdf_path)
        if conv_err:
            pdf_name = unique_name  # fallback: use original if conversion fails

        conn = get_connection()
        cursor = conn.cursor()
        if not is_mysql():
            cursor.execute("BEGIN IMMEDIATE")
        document_number = (document_number or "").strip()
        if not document_number:
            document_number = DocumentService._reserve_document_number(cursor, plant)
        cursor.execute('''INSERT INTO documents 
            (name, user_id, uploader_email, plant, department, customer, file_name, uploaded_at, approval_status, original_file_name, pdf_file_name, current_version, category, document_number, revision_number, rejection_comment, decision_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_name, user_id, user_email, plant, department, customer, unique_name,
             timestamp.strftime("%Y-%m-%d"), "Pending", filename, pdf_name, 1, category, document_number, revision_number, "", "")
        )
        new_id = cursor.lastrowid

        # Save version 1
        cursor.execute('''INSERT INTO document_versions
            (document_id, version_number, file_name, original_file_name, pdf_file_name, uploaded_by, user_id, uploaded_at, change_summary, document_number, revision_number, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (new_id, 1, unique_name, filename, pdf_name, user_email, user_id,
             timestamp.strftime("%Y-%m-%d %H:%M:%S"), "Initial upload", document_number, revision_number, category)
        )
        conn.commit()
        conn.close()

        record = {
            "id": new_id,
            "name": user_name,
            "user_id": user_id,
            "uploader_email": user_email,
            "plant": plant,
            "department": department,
            "customer": customer,
            "file_name": unique_name,
            "original_file_name": filename,
            "pdf_file_name": pdf_name,
            "uploaded_at": timestamp.strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "current_version": 1,
            "document_number": document_number,
            "revision_number": revision_number,
            "category": category,
            "rejection_comment": "",
        }
        return record, None

    @staticmethod
    def save_updated_version(doc_id, file, user_name, user_id, user_email, upload_folder, revision_number, change_summary=""):
        """Admin-only: upload a new version of an existing document."""
        filename = secure_filename(file.filename or "")
        if not filename:
            return None, "Invalid file name."
        if not is_allowed_file(filename):
            return None, "File type not allowed. Accepted: PDF, Word, Excel, PowerPoint."

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents WHERE id = ?', (int(doc_id),))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None, "Document not found."
        doc = dict(row)

        base, extension = os.path.splitext(filename)
        timestamp = datetime.now()
        unique_name = f"{base}_{timestamp.strftime('%Y%m%d%H%M%S')}{extension}"
        orig_path = os.path.join(upload_folder, unique_name)
        file.save(orig_path)

        pdf_name = f"{base}_{timestamp.strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_path = os.path.join(upload_folder, pdf_name)
        _, conv_err = convert_to_pdf(orig_path, pdf_path)
        if conv_err:
            pdf_name = unique_name

        new_version = (doc.get('current_version') or 1) + 1

        cursor.execute('''UPDATE documents SET file_name=?, original_file_name=?, pdf_file_name=?,
            current_version=?, approval_status=?, approval_updated_at=NULL, revision_number=?,
            rejection_comment=?, decision_by=?, selected_recipients=NULL, first_approver=NULL,
            first_approved_at=NULL, final_approver=NULL, final_approved_at=NULL WHERE id=?''',
            (unique_name, filename, pdf_name, new_version, 'Pending', revision_number, "", "", int(doc_id))
        )
        cursor.execute('''INSERT INTO document_versions
            (document_id, version_number, file_name, original_file_name, pdf_file_name, uploaded_by, user_id, uploaded_at, change_summary, document_number, revision_number, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (int(doc_id), new_version, unique_name, filename, pdf_name, user_email, user_id,
             timestamp.strftime("%Y-%m-%d %H:%M:%S"), change_summary, doc.get("document_number", ""), revision_number, doc.get("category", ""))
        )
        conn.commit()
        cursor.execute('SELECT * FROM documents WHERE id = ?', (int(doc_id),))
        updated = DocumentService._normalize_record(dict(cursor.fetchone()))
        updated["previous_file_name"] = doc.get("file_name", "")
        updated["previous_revision_number"] = doc.get("revision_number", "")
        conn.close()
        return updated, None

    @staticmethod
    def resubmit_held_document(
        doc_id,
        file,
        user_name,
        user_id,
        user_email,
        upload_folder,
        correction_summary,
        revision_number="",
    ):
        """Replace a held document and return it to the reviewer who placed the hold."""
        filename = secure_filename(file.filename or "")
        correction_summary = (correction_summary or "").strip()
        if not filename:
            return None, "Please select the corrected document."
        if not is_allowed_file(filename):
            return None, "File type not allowed. Accepted: PDF, Word, Excel, PowerPoint."
        if not correction_summary:
            return None, "Please describe the corrections that were made."

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (int(doc_id),))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None, "Document not found."
        doc = dict(row)
        if doc.get("approval_status") != "Hold":
            conn.close()
            return None, "Only a document currently on hold can be resubmitted."
        if (doc.get("uploader_email") or "").strip().lower() != (user_email or "").strip().lower():
            conn.close()
            return None, "Only the original uploader can resubmit this document."

        base, extension = os.path.splitext(filename)
        timestamp = datetime.now()
        file_stamp = timestamp.strftime("%Y%m%d%H%M%S%f")
        unique_name = f"{base}_{file_stamp}{extension}"
        orig_path = os.path.join(upload_folder, unique_name)
        file.save(orig_path)

        pdf_name = f"{base}_{file_stamp}.pdf"
        pdf_path = os.path.join(upload_folder, pdf_name)
        _, conv_err = convert_to_pdf(orig_path, pdf_path)
        if conv_err:
            pdf_name = unique_name

        new_version = (doc.get("current_version") or 1) + 1
        next_status = "Pending Final Approval" if doc.get("first_approved_at") else "Pending"
        effective_revision = (revision_number or "").strip() or doc.get("revision_number", "")
        updated_at = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """UPDATE documents
               SET file_name = ?, original_file_name = ?, pdf_file_name = ?,
                   current_version = ?, approval_status = ?, approval_updated_at = ?,
                   revision_number = ?, resubmission_comment = ?, resubmitted_at = ?,
                   decision_by = ?
               WHERE id = ?""",
            (
                unique_name,
                filename,
                pdf_name,
                new_version,
                next_status,
                updated_at,
                effective_revision,
                correction_summary,
                updated_at,
                "",
                int(doc_id),
            ),
        )
        cursor.execute(
            """INSERT INTO document_versions
               (document_id, version_number, file_name, original_file_name, pdf_file_name,
                uploaded_by, user_id, uploaded_at, change_summary, document_number,
                revision_number, category)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                int(doc_id),
                new_version,
                unique_name,
                filename,
                pdf_name,
                user_email,
                user_id,
                updated_at,
                correction_summary,
                doc.get("document_number", ""),
                effective_revision,
                doc.get("category", ""),
            ),
        )
        cursor.execute(
            """UPDATE category_documents
               SET file_name = ?, approval_status = ?, revision_number = ?
               WHERE file_name = ?""",
            (unique_name, next_status, effective_revision, doc.get("file_name", "")),
        )
        conn.commit()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (int(doc_id),))
        updated = DocumentService._normalize_record(dict(cursor.fetchone()))
        updated["previous_file_name"] = doc.get("file_name", "")
        updated["previous_revision_number"] = doc.get("revision_number", "")
        conn.close()
        return updated, None

    @staticmethod
    def get_versions(doc_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM document_versions WHERE document_id = ? ORDER BY version_number DESC', (int(doc_id),))
        versions = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return versions

    @staticmethod
    def update_approval_status(doc_id, status, rejection_comment="", decided_by="", selected_recipients=""):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE id = ?', (int(doc_id),))
        existing_row = cursor.fetchone()
        if not existing_row:
            conn.close()
            return None, "Document not found."
        existing = dict(existing_row)
        
        normalized_comment = rejection_comment.strip() if status in {"Rejected", "Hold"} else ""
        if status == "Hold" and not normalized_comment:
            conn.close()
            return None, "Please describe the corrections needed before placing the document on hold."
        effective_recipients = selected_recipients.strip() or existing.get("selected_recipients") or ""
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if status == "Hold":
            cursor.execute('''UPDATE documents
                             SET approval_status = ?, approval_updated_at = ?, rejection_comment = ?,
                                 hold_comment = ?, hold_by = ?, held_at = ?,
                                 resubmission_comment = ?, resubmitted_at = ?, decision_by = ?,
                                 selected_recipients = ?
                             WHERE id = ?''',
                (status, updated_at, normalized_comment, normalized_comment, decided_by,
                 updated_at, "", None, decided_by, effective_recipients, int(doc_id))
            )
        elif status == "First Approved":
            cursor.execute('''UPDATE documents
                             SET approval_status = ?, approval_updated_at = ?, rejection_comment = ?,
                                 decision_by = ?, selected_recipients = ?, first_approver = ?,
                                 first_approved_at = ?
                             WHERE id = ?''',
                ("Pending Final Approval", updated_at, "", decided_by, selected_recipients.strip(), decided_by, updated_at, int(doc_id))
            )
        elif status == "Approved" and (
            existing.get("approval_status") == "Pending Final Approval"
            or (
                existing.get("approval_status") == "Hold"
                and existing.get("first_approved_at")
            )
        ):
            cursor.execute('''UPDATE documents
                             SET approval_status = ?, approval_updated_at = ?, rejection_comment = ?,
                                 decision_by = ?, final_approver = ?, final_approved_at = ?
                             WHERE id = ?''',
                (status, updated_at, normalized_comment, decided_by, decided_by, updated_at, int(doc_id))
            )
        else:
            cursor.execute('''UPDATE documents SET approval_status = ?, approval_updated_at = ?, rejection_comment = ?, decision_by = ?
                             WHERE id = ?''',
                (status, updated_at, normalized_comment, decided_by, int(doc_id))
            )
        conn.commit()
        
        cursor.execute('SELECT * FROM documents WHERE id = ?', (int(doc_id),))
        record = DocumentService._normalize_record(dict(cursor.fetchone()))
        cursor.execute(
            'UPDATE category_documents SET approval_status = ? WHERE file_name = ?',
            (record.get("approval_status", status), record.get("file_name", "")),
        )
        conn.commit()
        conn.close()
        return record, None

    @staticmethod
    def bulk_update_approval_status(doc_ids, status, rejection_comment="", decided_by="", selected_recipients=""):
        updated_records = []
        for doc_id in doc_ids:
            updated_record, error = DocumentService.update_approval_status(
                doc_id,
                status,
                rejection_comment=rejection_comment,
                decided_by=decided_by,
                selected_recipients=selected_recipients,
            )
            if error:
                return [], error
            updated_records.append(updated_record)
        return updated_records, None

    @staticmethod
    def generate_review_token(doc_id, secret_key, salt):
        serializer = URLSafeSerializer(secret_key, salt=salt)
        return serializer.dumps({"doc_id": int(doc_id)})

    @staticmethod
    def resolve_review_token(token, secret_key, salt, access_department=""):
        serializer = URLSafeSerializer(secret_key, salt=salt)
        payload = serializer.loads(token)
        return DocumentService.get_document_by_id(payload["doc_id"], access_department=access_department)

    @staticmethod
    def get_file_path(record, upload_folder):
        return os.path.join(upload_folder, record["file_name"])

    @staticmethod
    def get_preview_file_path(record, upload_folder):
        """Return the converted viewing copy when available, then the source file."""
        candidate_names = [
            record.get("pdf_file_name"),
            record.get("file_name"),
        ]

        for file_name in candidate_names:
            if not file_name:
                continue
            file_path = os.path.join(upload_folder, file_name)
            if os.path.isfile(file_path):
                return file_path

        fallback_name = next((name for name in candidate_names if name), "")
        return os.path.join(upload_folder, fallback_name)

    @staticmethod
    def delete_archived_record(archive_index):
        """Permanently delete an archived record from the archive."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM archive')
        records = cursor.fetchall()
        
        try:
            record = records[int(archive_index)]
            cursor.execute('DELETE FROM archive WHERE id = ?', (record['id'],))
            conn.commit()
            conn.close()
            return dict(record), None
        except (IndexError, ValueError):
            conn.close()
            return None, "Archive record not found."

    @staticmethod
    def get_all_archived_records():
        """Get all archived records."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM archive ORDER BY timestamp DESC')
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return records
