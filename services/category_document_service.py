from database import get_connection
from datetime import datetime
from data.departments import normalize_department


class CategoryDocumentService:
    """Provides access to documents organized by category and sub-category."""

    @staticmethod
    def _plant_filter(query, params, plant):
        if plant == "P2&3 - Guduvachery Plants":
            query += " AND cd.plant IN (?, ?)"
            params.extend(["P2 - Guduvachery Plant", "P3 - Guduvachery Plant"])
        elif plant:
            query += " AND cd.plant = ?"
            params.append(plant)
        return query

    @staticmethod
    def get_plants_for_category(category, sub_type=''):
        conn = get_connection()
        cursor = conn.cursor()
        query = 'SELECT DISTINCT plant FROM category_documents WHERE category = ?'
        params = [category]
        if sub_type:
            query += ' AND sub_category = ?'
            params.append(sub_type)
        query += ' ORDER BY plant'
        rows = [row['plant'] for row in cursor.execute(query, params).fetchall()]
        conn.close()
        from data.mock_data import PLANTS
        result = [p for p in PLANTS if p['label'] in rows]
        return result if result else list(PLANTS)

    @staticmethod
    def get_departments_for_category(category, plant='', sub_type=''):
        conn = get_connection()
        cursor = conn.cursor()
        query = 'SELECT DISTINCT department FROM category_documents WHERE category = ?'
        params = [category]
        if plant:
            query += ' AND plant = ?'
            params.append(plant)
        if sub_type:
            query += ' AND sub_category = ?'
            params.append(sub_type)
        query += ' ORDER BY department'
        rows = [row['department'] for row in cursor.execute(query, params).fetchall()]
        conn.close()
        return sorted({normalize_department(row) for row in rows})

    @staticmethod
    def get_files_for_category(category, plant='', department='', sub_type='', sub_category='', approved_only=True):
        sub_type = sub_type or sub_category
        department = normalize_department(department) if department else department
        conn = get_connection()
        cursor = conn.cursor()
        query = '''
            SELECT DISTINCT cd.file_name
            FROM category_documents cd
            LEFT JOIN documents d ON d.file_name = cd.file_name
            WHERE cd.category = ?
        '''
        params = [category]
        query = CategoryDocumentService._plant_filter(query, params, plant)
        if department:
            query += ' AND cd.department = ?'
            params.append(department)
        if sub_type:
            query += ' AND cd.sub_category = ?'
            params.append(sub_type)
        if approved_only:
            query += " AND COALESCE(d.approval_status, cd.approval_status) = 'Approved'"
        query += ' ORDER BY cd.uploaded_at DESC'
        rows = [row['file_name'] for row in cursor.execute(query, params).fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_file_records_for_category(category, department='', approved_only=True):
        department = normalize_department(department) if department else department
        conn = get_connection()
        cursor = conn.cursor()
        query = '''
            SELECT DISTINCT cd.category, cd.sub_category, cd.plant, cd.department, cd.file_name, cd.uploaded_at
            FROM category_documents cd
            LEFT JOIN documents d ON d.file_name = cd.file_name
            WHERE cd.category = ?
        '''
        params = [category]
        if department:
            query += ' AND cd.department = ?'
            params.append(department)
        if approved_only:
            query += " AND COALESCE(d.approval_status, cd.approval_status) = 'Approved'"
        query += ' ORDER BY cd.uploaded_at DESC'
        rows = [dict(row) for row in cursor.execute(query, params).fetchall()]
        conn.close()
        return rows

    @staticmethod
    def sync_status_for_file(file_name, approval_status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE category_documents SET approval_status = ? WHERE file_name = ?',
            (approval_status, file_name),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def save_category_document(category, plant, department, file_name, uploaded_by, user_id,
                                sub_category=None, revision_number='Rev.00'):
        department = normalize_department(department)
        conn = get_connection()
        cursor = conn.cursor()
        uploaded_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO category_documents (
                category, sub_category, plant, department, file_name,
                uploaded_by, user_id, uploaded_at, approval_status, revision_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            category, sub_category, plant, department, file_name,
            uploaded_by, user_id, uploaded_at, 'Pending', revision_number
        ))
        conn.commit()
        doc_id = cursor.lastrowid
        conn.close()
        return doc_id

    @staticmethod
    def get_all_files_for_category(category):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM category_documents WHERE category = ? ORDER BY uploaded_at DESC', (category,))
        files = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return files
