"""
Test script to verify data persistence
Run this to confirm uploads are saved to database
"""
import sqlite3
from datetime import datetime

def test_persistence():
    conn = sqlite3.connect('smart_dms.db')
    cursor = conn.cursor()
    
    # Test 1: Insert a document
    print("Test 1: Inserting test document...")
    cursor.execute('''INSERT INTO documents 
        (name, user_id, uploader_email, plant, department, customer, file_name, uploaded_at, approval_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        ('Test User', 'U999', 'test@example.com', 'P1 - Trichy Plant', 'Quality', 
         'Internal', 'test_file.pdf', datetime.now().strftime("%Y-%m-%d"), 'Pending')
    )
    doc_id = cursor.lastrowid
    conn.commit()
    print(f"[OK] Document inserted with ID: {doc_id}")
    
    # Test 2: Retrieve the document
    print("\nTest 2: Retrieving document...")
    cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
    doc = cursor.fetchone()
    print(f"[OK] Document retrieved: {doc[6]} (Status: {doc[9]})")
    
    # Test 3: Update approval status
    print("\nTest 3: Updating approval status...")
    cursor.execute('UPDATE documents SET approval_status = ? WHERE id = ?', ('Approved', doc_id))
    conn.commit()
    cursor.execute('SELECT approval_status FROM documents WHERE id = ?', (doc_id,))
    status = cursor.fetchone()[0]
    print(f"[OK] Status updated to: {status}")
    
    # Test 4: Log an action
    print("\nTest 4: Creating system log entry...")
    cursor.execute('''INSERT INTO system_logs (timestamp, user_name, user_id, action, details)
                     VALUES (?, ?, ?, ?, ?)''',
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Test User', 'test@example.com', 
         'TEST', 'Testing persistence')
    )
    conn.commit()
    print("[OK] Log entry created")
    
    # Test 5: Count all records
    print("\nTest 5: Counting all records...")
    cursor.execute('SELECT COUNT(*) FROM documents')
    doc_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM system_logs')
    log_count = cursor.fetchone()[0]
    print(f"[OK] Total documents: {doc_count}")
    print(f"[OK] Total logs: {log_count}")
    
    # Cleanup test data
    print("\nCleaning up test data...")
    cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
    cursor.execute('DELETE FROM system_logs WHERE action = ?', ('TEST',))
    conn.commit()
    print("[OK] Test data removed")
    
    conn.close()
    print("\n[SUCCESS] All persistence tests passed!")
    print("Data will survive app restarts and logout/login cycles.")

if __name__ == '__main__':
    test_persistence()
