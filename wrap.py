from pymavlink import mavutil
import argparse
import time

# Set up the MAVLink connection
connection_string = 'udp:127.0.0.1:5760'  # Replace with your connection string

# Wait for a connection to be established
while True:
    try:
        mav = mavutil.mavlink_connection(connection_string)
        mav.wait_heartbeat()
        break
    except:
        print("Waiting for connection...")
        time.sleep(1)

# Get autopilot version and hardware IDs
version = mav.mav.version
vendor_id = mav.mav.v2extension_1
product_id = mav.mav.v2extension_2
print(f"Autopilot version: {version}, Vendor ID: {vendor_id}, Product ID: {product_id}")

# Command line argument parsing
parser = argparse.ArgumentParser(description="MAVLink interpreter")
parser.add_argument("command", nargs="?", default=None, help="Command to execute")
args = parser.parse_args()

# Main loop to read and process MAVLink messages
while True:
    # Wait for a message and get its type
    msg = mav.recv_match()
    msg_type = msg.get_type()

    # Check if the vehicle is in AUTO mode
    if msg_type == 'SYS_STATUS' and msg.mode == mavutil.mavlink.MAV_MODE_AUTO:
        print("Vehicle is in AUTO mode")

    # Check if the message contains GPS information
    if msg_type == 'GLOBAL_POSITION_INT':
        # Extract latitude and longitude from the message
        lat = msg.lat / 1e7
        lon = msg.lon / 1e7

        # Print latitude and longitude if vehicle is in AUTO mode
        if msg_type == 'SYS_STATUS' and msg.mode == mavutil.mavlink.MAV_MODE_AUTO:
            print(f"Latitude: {lat}, Longitude: {lon}")

    # Check if the user entered a command
    if args.command is not None:
        # Check if the command is to report battery state
        if args.command == 'report state battery':
            # Send a request for battery status
            mav.mav.command_long_send(
                mav.target_system, mav.target_component,
                mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
                0, mavutil.mavlink.MAVLINK_MSG_ID_BATTERY_STATUS,
                0, 0, 0, 0, 0, 0
            )

            # Wait for the battery status message
            battery_msg = mav.recv_match(type='BATTERY_STATUS', blocking=True, timeout=5.0)
            if battery_msg is None:
                print("Timed out waiting for battery status")
            else:
                print(f"Battery voltage: {battery_msg.voltage} V")

        # Check if the command is to start state callouts
        elif args.command == 'state callouts':
            # Print the current airspeed and altitude every 15 seconds until disarmed
            while mav.recv_match(type='HEARTBEAT').system_status == mavutil.mavlink.MAV_STATE_ACTIVE:
                airspeed_msg = mav.recv_match(type='VFR_HUD', blocking=True, timeout=5.0)
                altitude_msg = mav.recv_match(type='ALTITUDE', blocking=True, timeout=5.0)

                if airspeed_msg is not None:
                    print(f"Airspeed: {airspeed_msg.airspeed} m/s")

                if altitude_msg is not None:
                    print(f"Altitude: {altitude_msg.altitude} m")

                time.sleep(15)

        #
