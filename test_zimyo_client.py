import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zimyo_attendance.tools.zimyo_client import create_zimyo_client

def main():
    print("Creating Zimyo client...")
    client = create_zimyo_client()
    
    print("Logging in...")
    if not client.login():
        print("Login failed")
        return
    
    print("Login successful")
    
    print("Fetching attendance status...")
    att = client.get_attendance_status()
    if att is None:
        print("Failed to get attendance status")
    else:
        print("Attendance status:")
        print(f"  Date: {att.date}")
        print(f"  Total Punch Time: {att.total_punch_time}")
        print(f"  In/Out Status: {att.in_out_status}")
        print(f"  Shift Name: {att.shift_name}")
        print(f"  Shift Code: {att.shift_code}")
        print(f"  Day Start: {att.day_start_time}")
        print(f"  Day End: {att.day_end_time}")
    
    # Uncomment the following to test clock in/out (use with caution)
    # print("Testing clock in...")
    # if client.clock_in():
    #     print("Clock in successful")
    # else:
    #     print("Clock in failed")
    #
    # print("Testing clock out...")
    # if client.clock_out():
    #     print("Clock out successful")
    # else:
    #     print("Clock out failed")
    
    client.close()
    print("Done.")

if __name__ == "__main__":
    main()
