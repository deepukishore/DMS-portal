#!/usr/bin/env python
"""
Quick script to reset database and run seeding.
"""
import os
import sys

# Change to script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Remove old database
if os.path.exists('smart_dms.db'):
    try:
        os.remove('smart_dms.db')
        print("✓ Deleted old database")
    except Exception as e:
        print(f"✗ Error deleting database: {e}")
        sys.exit(1)

# Import and run seeding
try:
    from seed_db import main
    main()
except Exception as e:
    print(f"✗ Error during seeding: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ Database reset and seeding complete!")
