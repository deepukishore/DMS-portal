from data.departments import normalize_department
from data.mock_data import DEPARTMENTS, MASTER_RECORD_PLANTS, PLANT_ASSETS
from database import get_connection


class PlantAssetService:
    """Provides read-only access to plant asset documents."""

    @staticmethod
    def get_all_plants():
        return list(MASTER_RECORD_PLANTS)

    @staticmethod
    def get_departments_for_plant(plant_label, access_department=""):
        if access_department:
            return [normalize_department(access_department)]
        return list(DEPARTMENTS)

    @staticmethod
    def get_files_for_plant_department(plant_label, department, access_department=""):
        department = normalize_department(department)
        access_department = normalize_department(access_department) if access_department else access_department
        if access_department and department and department != access_department:
            return []
        effective_department = access_department or department
        # Handle P2&3 grouping: query both P2 and P3 plants
        if plant_label == "P2&3 - Guduvachery Plants":
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT file_name FROM documents 
                WHERE plant IN ('P2 - Guduvachery Plant', 'P3 - Guduvachery Plant') 
                AND department = ? 
                ORDER BY uploaded_at DESC
            ''', (effective_department,))
            db_files = [row['file_name'] for row in cursor.fetchall()]
            conn.close()
        else:
            # Get files from database documents
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT file_name FROM documents WHERE plant = ? AND department = ? ORDER BY uploaded_at DESC', 
                          (plant_label, effective_department))
            db_files = [row['file_name'] for row in cursor.fetchall()]
            conn.close()
        
        # Fallback to mock data if no database records
        if not db_files:
            if plant_label == "P2&3 - Guduvachery Plants":
                return []
            return PLANT_ASSETS.get(plant_label, {}).get(effective_department, [])
        return db_files

    @staticmethod
    def plant_exists(plant_label):
        return plant_label in [p['label'] for p in MASTER_RECORD_PLANTS]

    @staticmethod
    def get_dept_label(dept_code):
        """Get full department name from CQA code."""
        return normalize_department(dept_code)
