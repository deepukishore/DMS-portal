import os
import re
from datetime import datetime

from itsdangerous import URLSafeSerializer
from werkzeug.utils import secure_filename

from data.customers import normalize_customer
from data.departments import normalize_department
from database import get_connection
from services.pdf_conversion_service import convert_to_pdf, is_allowed_file


class DocumentService:
    """Manages document records used across dashboard and approvals."""

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
            query += ' AND customer = ?'
            params.append(customer)
        
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
            current_version=?, approval_status=?, approval_updated_at=NULL, revision_number=?, rejection_comment=?, decision_by=? WHERE id=?''',
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
        
        normalized_comment = rejection_comment.strip() if status == "Rejected" else ""
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if status == "First Approved":
            cursor.execute('''UPDATE documents
                             SET approval_status = ?, approval_updated_at = ?, rejection_comment = ?,
                                 decision_by = ?, selected_recipients = ?, first_approver = ?,
                                 first_approved_at = ?
                             WHERE id = ?''',
                ("Pending Final Approval", updated_at, "", decided_by, selected_recipients.strip(), decided_by, updated_at, int(doc_id))
            )
        elif status == "Approved" and existing.get("approval_status") == "Pending Final Approval":
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
