## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      USB Device Recovery Tool             ##
###############################################

import sys
import time
import os
import subprocess
import platform

def print_header(text):
    print("\n" + "=" * 50)
    print(text)
    print("=" * 50)

def print_section(text):
    print("\n" + "-" * 40)
    print(text)
    print("-" * 40)

def run_command(command):
    """Run a command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout
    except Exception as e:
        return f"Error running command: {e}"

def reset_usb_devices_windows():
    """Reset USB devices on Windows"""
    print_section("RESETTING USB DEVICES")
    
    # First, get a list of all USB devices
    print("Listing USB devices...")
    output = run_command('powershell -Command "Get-PnpDevice | Where-Object {$_.Class -eq \'USB\' -or $_.Class -eq \'Camera\'} | Format-Table -AutoSize"')
    print(output)
    
    # Look specifically for Intel RealSense devices
    print("\nLooking for Intel RealSense devices...")
    output = run_command('powershell -Command "Get-PnpDevice | Where-Object {$_.FriendlyName -like \'*Intel*\' -or $_.FriendlyName -like \'*RealSense*\'} | Format-Table -AutoSize"')
    print(output)
    
    # Try to disable and re-enable the device if found
    print("\nAttempting to reset RealSense devices...")
    
    # This command will disable any device with "RealSense" in the name
    disable_cmd = 'powershell -Command "Get-PnpDevice | Where-Object {$_.FriendlyName -like \'*RealSense*\'} | Disable-PnpDevice -Confirm:$false"'
    print("Disabling RealSense devices...")
    output = run_command(disable_cmd)
    print(output)
    
    # Wait a moment
    print("Waiting 5 seconds...")
    time.sleep(5)
    
    # This command will re-enable any device with "RealSense" in the name
    enable_cmd = 'powershell -Command "Get-PnpDevice | Where-Object {$_.FriendlyName -like \'*RealSense*\'} | Enable-PnpDevice -Confirm:$false"'
    print("Re-enabling RealSense devices...")
    output = run_command(enable_cmd)
    print(output)
    
    print("\nUSB reset procedure completed. Please check if your device is now working.")

def check_driver_status_windows():
    """Check driver status on Windows"""
    print_section("CHECKING DRIVER STATUS")
    
    # Check for Intel RealSense drivers
    print("Looking for Intel RealSense drivers...")
    output = run_command('powershell -Command "Get-WmiObject Win32_PnPSignedDriver | Where-Object {$_.DeviceName -like \'*Intel*\' -or $_.DeviceName -like \'*RealSense*\'} | Select-Object DeviceName, DriverVersion, DriverDate | Format-Table -AutoSize"')
    print(output)
    
    # Check for issues in device manager
    print("\nChecking for device issues...")
    output = run_command('powershell -Command "Get-PnpDevice | Where-Object {$_.Status -ne \'OK\'} | Format-Table -AutoSize"')
    print(output)

def recommend_fixes():
    """Provide recommendations for fixing the connection issues"""
    print_section("RECOMMENDATIONS")
    
    print("Based on common RealSense L515 issues, try these steps:")
    print("\n1. USB Connectivity:")
    print("   - Connect the L515 directly to a USB 3.0 port (blue connector)")
    print("   - Try a different USB 3.0 port")
    print("   - Try a different, high-quality USB cable")
    print("   - Try a powered USB hub")
    
    print("\n2. Driver Issues:")
    print("   - Install the latest Intel RealSense SDK (v2.50+ recommended for L515)")
    print("   - Download from: https://github.com/IntelRealSense/librealsense/releases")
    print("   - After installing, restart your computer")
    
    print("\n3. Power Management:")
    print("   - Open Device Manager > Universal Serial Bus controllers")
    print("   - For each USB Root Hub, open Properties > Power Management")
    print("   - Uncheck 'Allow the computer to turn off this device to save power'")
    
    print("\n4. Test with Intel Tools:")
    print("   - Install and try the Intel RealSense Viewer application")
    print("   - If it works there but not in Python, it's a software configuration issue")
    
    print("\n5. Python Environment:")
    print("   - Make sure you have the correct pyrealsense2 version matching your SDK")
    print("   - Try: pip uninstall pyrealsense2 && pip install pyrealsense2")
    
    print("\n6. For L515 Specifically:")
    print("   - The L515 may need more power than other RealSense cameras")
    print("   - It works best with direct USB 3.1 or powered USB hub connections")
    print("   - Try resetting the device using the reset button (small hole) on the camera")

def main():
    print_header("INTEL REALSENSE USB RECOVERY TOOL")
    print("This tool will help diagnose and attempt to fix USB connection issues")
    print("with your Intel RealSense L515 camera.")
    
    if platform.system() != 'Windows':
        print("This tool currently only supports Windows.")
        return
    
    # Check if running as administrator
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    if not is_admin:
        print("WARNING: This script is not running with administrator privileges.")
        print("Some operations may fail. Consider running as administrator.")
        input("Press Enter to continue anyway or Ctrl+C to exit...")
    
    # Check driver status
    check_driver_status_windows()
    
    # Ask to reset USB devices
    print("\nWould you like to attempt resetting USB devices?")
    print("This will temporarily disconnect ALL USB devices.")
    choice = input("Type 'yes' to continue or anything else to skip: ")
    
    if choice.lower() == 'yes':
        reset_usb_devices_windows()
    else:
        print("Skipping USB reset.")
    
    # Provide recommendations
    recommend_fixes()
    
    print_header("RECOVERY PROCEDURE COMPLETE")
    print("After trying these steps, run the camera_diagnostic.py script again")
    print("to check if your camera is now working.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled error: {str(e)}")
        input("Press Enter to exit...")
