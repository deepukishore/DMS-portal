#!/usr/bin/env python3
"""
Direct Database Seeding Script
This script resets the database and applies all enhanced mock data.
Run this file directly to populate the database with comprehensive test data.
"""

import os
import sys

# Ensure we're in the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("=" * 70)
print("SMART DMS - DATABASE SEEDING WITH ENHANCED DATA")
print("=" * 70)
print()

# Step 1: Delete old database
print("📌 Step 1: Preparing database...")
if os.path.exists('smart_dms.db'):
    try:
        os.remove('smart_dms.db')
        print("   ✓ Old database deleted")
    except Exception as e:
        print(f"   ⚠ Could not delete old database: {e}")
        print("   Continuing with existing database...")
else:
    print("   ✓ No old database to delete (fresh start)")

print()

# Step 2: Initialize database
print("📌 Step 2: Initializing database schema...")
try:
    from database import init_db
    init_db()
    print("   ✓ Database schema initialized")
except Exception as e:
    print(f"   ✗ Error initializing database: {e}")
    sys.exit(1)

print()

# Step 3: Seed data
print("📌 Step 3: Populating with enhanced mock data...")
try:
    from seed_db import seed_users, seed_documents, seed_archive, seed_system_logs
    
    print("   → Creating users...")
    seed_users()
    print()
    
    print("   → Creating documents...")
    seed_documents()
    print()
    
    print("   → Creating archive...")
    seed_archive()
    print()
    
    print("   → Creating system logs...")
    seed_system_logs()
    print()
    
    print("=" * 70)
    print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    
    print("📊 MOCK DATA SUMMARY:")
    print("   • Users: 15 (10 original + 5 new)")
    print("   • Documents: 54 (22 original + 32 new)")
    print("   • Archived: 10 (5 original + 5 new)")
    print("   • System Logs: 44+ entries")
    print()
    
    print("🚀 NEXT STEPS:")
    print("   1. Run: python app.py")
    print("   2. Open: http://localhost:5000")
    print("   3. Login with: diva@example.com / Pass@12345")
    print()
    
    print("📚 DOCUMENTATION:")
    print("   • Start with: 00_START_HERE.md")
    print("   • Quick ref: QUICK_REFERENCE_ENHANCED.md")
    print("   • Full details: MOCK_DATA_ENHANCED.md")
    print()
    
except Exception as e:
    print(f"   ✗ Error during seeding: {e}")
    import traceback
    print()
    print("FULL ERROR DETAILS:")
    traceback.print_exc()
    sys.exit(1)

print("=" * 70)
print("Ready to start the application! 🎉")
print("=" * 70)
