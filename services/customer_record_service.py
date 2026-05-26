from data.customers import OFFICIAL_CUSTOMERS, normalize_customer
from data.mock_data import CUSTOMER_RECORDS
from database import get_connection


class CustomerRecordService:
    """Provides read-only access to customer document records."""

    @staticmethod
    def get_all_customers(access_department=""):
        if not access_department:
            return list(OFFICIAL_CUSTOMERS)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT DISTINCT customer FROM documents WHERE department = ? ORDER BY customer ASC',
            (access_department,),
        )
        customers = [normalize_customer(row['customer']) for row in cursor.fetchall() if row['customer']]
        conn.close()
        return customers or list(OFFICIAL_CUSTOMERS)

    @staticmethod
    def get_departments_for_customer(customer_name):
        return []

    @staticmethod
    def get_files_for_customer(customer_name, access_department=""):
        customer_name = normalize_customer(customer_name)
        conn = get_connection()
        cursor = conn.cursor()
        if access_department:
            cursor.execute(
                'SELECT file_name FROM documents WHERE customer = ? AND department = ? ORDER BY uploaded_at DESC',
                (customer_name, access_department),
            )
        else:
            cursor.execute(
                'SELECT file_name FROM documents WHERE customer = ? ORDER BY uploaded_at DESC',
                (customer_name,),
            )
        db_files = [row['file_name'] for row in cursor.fetchall()]
        conn.close()

        if not db_files:
            return CUSTOMER_RECORDS.get(customer_name, [])
        return db_files

    @staticmethod
    def customer_exists(customer_name, access_department=""):
        customer_name = normalize_customer(customer_name)
        conn = get_connection()
        cursor = conn.cursor()
        if access_department:
            cursor.execute('SELECT COUNT(*) as count FROM documents WHERE customer = ? AND department = ?', (customer_name, access_department))
        else:
            cursor.execute('SELECT COUNT(*) as count FROM documents WHERE customer = ?', (customer_name,))
        count = cursor.fetchone()['count']
        conn.close()
        
        # Check database first, then fallback to mock data
        return count > 0 or customer_name in OFFICIAL_CUSTOMERS or customer_name in CUSTOMER_RECORDS
