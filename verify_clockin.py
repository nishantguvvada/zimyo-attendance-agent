#!/usr/bin/env python3
"""
Ad-hoc verification script for Zimyo clock-in fix.
Tests that clock-in operation no longer returns HTTP 422.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_clock_in_fix():
    """Test that clock-in works (no more 422 errors)."""
    try:
        from zimyo_attendance.tools.zimyo_client import create_zimyo_client
        
        print("=== Ad-hoc Verification: Zimyo Clock-in Fix ===")
        
        # Create client
        client = create_zimyo_client()
        
        # Test login
        print("1. Testing login...")
        if not client.login():
            print("   ❌ LOGIN FAILED")
            return False
        print("   ✅ Login successful")
        
        # Test clock-in
        print("2. Testing clock-in...")
        result = client.clock_in()
        if result:
            print("   ✅ Clock-in SUCCESSFUL (no 422 error)")
            return True
        else:
            print("   ❌ Clock-in FAILED")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_clock_in_fix()
    print(f"\n=== RESULT: {'PASS' if success else 'FAIL'} ===")
    sys.exit(0 if success else 1)