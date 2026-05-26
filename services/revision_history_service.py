from database import get_connection
from datetime import datetime


class RevisionHistoryService:
    """Manages document revision history tracking."""

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
        
        query = 'SELECT * FROM revision_history WHERE 1=1'
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
        
        return revisions

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
        cursor.execute('SELECT * FROM revision_history WHERE file_name = ? ORDER BY revision_date DESC', (file_name,))
        revisions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return revisions

    @staticmethod
    def get_latest_revision_for_file(file_name):
        """Get the most recent revision for a file."""
        revisions = RevisionHistoryService.get_revisions_for_document(file_name)
        return revisions[0] if revisions else None
