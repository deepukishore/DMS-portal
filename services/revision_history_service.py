from database import get_connection
from datetime import datetime


class RevisionHistoryService:
    """Manages document revision history tracking."""

    @staticmethod
    def _version_rows(plant=None, department=None, document_id=None, file_name=None):
        conn = get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT
                v.id,
                v.document_id,
                v.version_number,
                v.file_name,
                v.original_file_name,
                v.uploaded_by,
                v.user_id,
                v.uploaded_at,
                v.change_summary,
                v.revision_number,
                d.plant,
                d.department
            FROM document_versions v
            LEFT JOIN documents d ON d.id = v.document_id
            WHERE 1=1
        '''
        params = []
        if plant:
            query += ' AND d.plant = ?'
            params.append(plant)
        if department:
            query += ' AND d.department = ?'
            params.append(department)
        if document_id:
            query += ' AND v.document_id = ?'
            params.append(int(document_id))
        if file_name:
            query += ' AND (v.file_name = ? OR v.original_file_name = ?)'
            params.extend([file_name, file_name])
        query += ' ORDER BY v.document_id ASC, v.version_number ASC, v.uploaded_at ASC'

        rows = [dict(row) for row in cursor.execute(query, params).fetchall()]
        conn.close()

        previous_by_doc = {}
        revisions = []
        for row in rows:
            previous_file_name = previous_by_doc.get(row.get("document_id"))
            previous_by_doc[row.get("document_id")] = row.get("file_name")
            if (row.get("version_number") or 1) <= 1:
                continue

            revision_number = row.get("revision_number") or f'v{row.get("version_number", "")}'
            revisions.append({
                "id": f'version-{row["id"]}',
                "document_id": row.get("document_id"),
                "file_name": row.get("file_name"),
                "revision_number": revision_number,
                "revised_by": row.get("uploaded_by") or "Unknown",
                "user_id": row.get("user_id") or "",
                "plant": row.get("plant"),
                "department": row.get("department"),
                "revision_date": row.get("uploaded_at"),
                "change_summary": row.get("change_summary") or f'Version {row.get("version_number")} uploaded',
                "previous_file_name": previous_file_name,
                "source": "document_versions",
            })
        return revisions

    @staticmethod
    def add_revision(file_name, revision_number, revised_by, user_id, plant=None, department=None, change_summary=None, previous_file_name=None, document_id=None):
        """
        Add a new revision entry.
        
        Args:
            file_name: Name of the current file
            revision_number: Version number (e.g., Rev.01)
            revised_by: Name of person who revised
            user_id: User ID of reviser
            plant: Optional plant name
            department: Optional department name
            change_summary: Optional summary of changes
            previous_file_name: Optional name of file being superseded
            document_id: Optional ID of original document
        
        Returns:
            The inserted revision ID
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        revision_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO revision_history (
                document_id, file_name, revision_number, revised_by, user_id,
                plant, department, revision_date, change_summary, previous_file_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            document_id, file_name, revision_number, revised_by, user_id,
            plant, department, revision_date, change_summary, previous_file_name
        ))
        
        conn.commit()
        revision_id = cursor.lastrowid
        conn.close()
        
        return revision_id

    @staticmethod
    def get_all_revisions(plant=None, department=None):
        """
        Get all revisions with optional filters.
        
        Args:
            plant: Optional plant filter
            department: Optional department filter
        
        Returns:
            List of revision records ordered by date (newest first)
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM revision_history
            WHERE previous_file_name IS NOT NULL
              AND TRIM(previous_file_name) != ''
        '''
        params = []
        
        if plant:
            query += ' AND plant = ?'
            params.append(plant)
        if department:
            query += ' AND department = ?'
            params.append(department)
        
        query += ' ORDER BY revision_date DESC'
        
        cursor.execute(query, params)
        revisions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        for revision in revisions:
            revision["source"] = "revision_history"

        existing_keys = {
            (
                revision.get("document_id"),
                revision.get("file_name"),
                revision.get("revision_number"),
            )
            for revision in revisions
        }
        for version_revision in RevisionHistoryService._version_rows(plant=plant, department=department):
            key = (
                version_revision.get("document_id"),
                version_revision.get("file_name"),
                version_revision.get("revision_number"),
            )
            if key not in existing_keys:
                revisions.append(version_revision)

        return sorted(
            revisions,
            key=lambda revision: (revision.get("revision_date") or "", str(revision.get("id") or "")),
            reverse=True,
        )

    @staticmethod
    def get_revisions_for_document(file_name):
        """
        Get all revisions for a specific document by file name.
        
        Args:
            file_name: Name of the document file
        
        Returns:
            List of revision records ordered by date (newest first)
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT DISTINCT document_id
            FROM document_versions
            WHERE file_name = ? OR original_file_name = ?
            ''',
            (file_name, file_name),
        )
        doc_ids = [row["document_id"] for row in cursor.fetchall()]

        cursor.execute(
            '''
            SELECT * FROM revision_history
            WHERE (file_name = ? OR previous_file_name = ?)
              AND previous_file_name IS NOT NULL
              AND TRIM(previous_file_name) != ''
            ORDER BY revision_date DESC
            ''',
            (file_name, file_name),
        )
        revisions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        for revision in revisions:
            revision["source"] = "revision_history"

        existing_keys = {
            (
                revision.get("document_id"),
                revision.get("file_name"),
                revision.get("revision_number"),
            )
            for revision in revisions
        }
        for doc_id in doc_ids:
            for version_revision in RevisionHistoryService._version_rows(document_id=doc_id):
                key = (
                    version_revision.get("document_id"),
                    version_revision.get("file_name"),
                    version_revision.get("revision_number"),
                )
                if key not in existing_keys:
                    revisions.append(version_revision)

        return sorted(
            revisions,
            key=lambda revision: (revision.get("revision_date") or "", str(revision.get("id") or "")),
            reverse=True,
        )

    @staticmethod
    def get_latest_revision_for_file(file_name):
        """Get the most recent revision for a file."""
        revisions = RevisionHistoryService.get_revisions_for_document(file_name)
        return revisions[0] if revisions else None
