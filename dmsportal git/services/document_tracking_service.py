from datetime import datetime
from database import get_connection


class DocumentTrackingService:
    """Manages recently viewed documents and bookmarks."""

    @staticmethod
    def track_recently_viewed(user_email, document_id):
        """Log a document view for a user."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Delete oldest entry if user has 10+ viewed documents
            cursor.execute(
                'SELECT COUNT(*) as cnt FROM recently_viewed WHERE user_email = ?',
                (user_email,)
            )
            count = cursor.fetchone()['cnt']
            if count >= 10:
                cursor.execute(
                    '''DELETE FROM recently_viewed WHERE id IN 
                    (SELECT id FROM recently_viewed WHERE user_email = ? ORDER BY viewed_at ASC LIMIT 1)''',
                    (user_email,)
                )
            
            # Remove existing entry for this document if it exists
            cursor.execute(
                'DELETE FROM recently_viewed WHERE user_email = ? AND document_id = ?',
                (user_email, document_id)
            )
            
            # Add new entry
            cursor.execute(
                '''INSERT INTO recently_viewed (user_email, document_id, viewed_at)
                   VALUES (?, ?, ?)''',
                (user_email, document_id, datetime.now().isoformat())
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_recently_viewed(user_email, limit=5, access_department=""):
        """Get recently viewed documents for a user."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            department_clause = ""
            params = [user_email]
            if access_department:
                department_clause = " AND d.department = ?"
                params.append(access_department)
            params.append(limit)
            cursor.execute(
                '''SELECT d.*, rv.viewed_at FROM recently_viewed rv
                   JOIN documents d ON rv.document_id = d.id
                   WHERE rv.user_email = ?''' + department_clause + '''
                   ORDER BY rv.viewed_at DESC
                   LIMIT ?''',
                tuple(params)
            )
            records = [dict(row) for row in cursor.fetchall()]
            return records
        finally:
            conn.close()

    @staticmethod
    def toggle_bookmark(user_email, document_id):
        """Toggle bookmark for a document."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if already bookmarked
            cursor.execute(
                'SELECT id FROM bookmarks WHERE user_email = ? AND document_id = ?',
                (user_email, document_id)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Remove bookmark
                cursor.execute(
                    'DELETE FROM bookmarks WHERE user_email = ? AND document_id = ?',
                    (user_email, document_id)
                )
                is_bookmarked = False
            else:
                # Add bookmark
                cursor.execute(
                    '''INSERT INTO bookmarks (user_email, document_id, bookmarked_at)
                       VALUES (?, ?, ?)''',
                    (user_email, document_id, datetime.now().isoformat())
                )
                is_bookmarked = True
            
            conn.commit()
            return is_bookmarked
        finally:
            conn.close()

    @staticmethod
    def get_bookmarks(user_email, access_department=""):
        """Get all bookmarked documents for a user."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            department_clause = ""
            params = [user_email]
            if access_department:
                department_clause = " AND d.department = ?"
                params.append(access_department)
            cursor.execute(
                '''SELECT d.*, b.bookmarked_at FROM bookmarks b
                   JOIN documents d ON b.document_id = d.id
                   WHERE b.user_email = ?''' + department_clause + '''
                   ORDER BY b.bookmarked_at DESC''',
                tuple(params)
            )
            records = [dict(row) for row in cursor.fetchall()]
            return records
        finally:
            conn.close()

    @staticmethod
    def is_bookmarked(user_email, document_id):
        """Check if a document is bookmarked by a user."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT id FROM bookmarks WHERE user_email = ? AND document_id = ?',
                (user_email, document_id)
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def get_upload_trend_data(days=90, access_department=""):
        """Get upload counts per day for trend chart."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''SELECT DATE(uploaded_at) as date, COUNT(*) as count
                   FROM documents
                   WHERE uploaded_at >= datetime('now', '-' || ? || ' days')'''
            params = [days]
            if access_department:
                query += ' AND department = ?'
                params.append(access_department)
            query += ' GROUP BY DATE(uploaded_at) ORDER BY date ASC'
            cursor.execute(
                query,
                tuple(params)
            )
            trend_data = [dict(row) for row in cursor.fetchall()]
            return trend_data
        finally:
            conn.close()

    @staticmethod
    def get_upload_stats_summary(access_department=""):
        """Get upload statistics for summary cards."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Total documents
            if access_department:
                cursor.execute('SELECT COUNT(*) as total FROM documents WHERE department = ?', (access_department,))
            else:
                cursor.execute('SELECT COUNT(*) as total FROM documents')
            total = cursor.fetchone()['total']
            
            # This month
            month_query = '''SELECT COUNT(*) as this_month FROM documents 
                   WHERE strftime('%Y-%m', uploaded_at) = strftime('%Y-%m', 'now')'''
            month_params = []
            if access_department:
                month_query += ' AND department = ?'
                month_params.append(access_department)
            cursor.execute(month_query, tuple(month_params))
            this_month = cursor.fetchone()['this_month']
            
            # This week
            week_query = '''SELECT COUNT(*) as this_week FROM documents 
                   WHERE uploaded_at >= datetime('now', '-7 days')'''
            week_params = []
            if access_department:
                week_query += ' AND department = ?'
                week_params.append(access_department)
            cursor.execute(week_query, tuple(week_params))
            this_week = cursor.fetchone()['this_week']
            
            return {
                'total': total,
                'this_month': this_month,
                'this_week': this_week
            }
        finally:
            conn.close()
