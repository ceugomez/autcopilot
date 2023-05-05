import time
import threading
from pymavlink import mavutil

# Set up the Mavlink connection
master = mavutil.mavlink_connection('udp:127.0.0.1:14551')

# Set up initial position
initial_position = None

# Set up the user input thread
def user_input():
    global initial_position
    while True:
        command = input().lower()
        if command == "report battery status":
            battery_status = master.messages['BATTERY_STATUS']
            print(f"Battery voltage: {battery_status.voltages[0] / 1000}V")
        elif command == "report location":
            if initial_position is None:
                print("Initial position has not been set yet.")
            else:
                try:
                    location = master.messages['GLOBAL_POSITION_INT']
                    dx = location.lat - initial_position[0]
                    dy = location.lon - initial_position[1]
                    dz = location.alt - initial_position[2]
                    print(f"Location relative to initial position: ({dx}m, {dy}m, {dz}m)")
                except KeyError:
                    print("GLOBAL_POSITION_INT message not received yet.")
        elif command == "report orientation":
            attitude = master.messages['ATTITUDE']
            print(f"Roll: {attitude.roll}, Pitch: {attitude.pitch}, Yaw: {attitude.yaw}")
        elif command == "mode change auto":
            master.mav.set_mode_send(
                master.target_system,
                mavutil.mavlink.MAV_MODE_AUTO_ARMED)
            print("Changed mode to auto.")
        elif command == "mode change manual":
            master.mav.set_mode_send(
                master.target_system,
                mavutil.mavlink.MAV_MODE_MANUAL_ARMED)
            print("Changed mode to manual.")
        else:
            print("Invalid command.")

# Set up the main thread
def main():
    global initial_position
    while True:
        # Wait for Mavlink connection
        while not master:
            print("GS: waiting for heartbeat")
            time.sleep(1)
        print("GS: Connection Established")
        
        # Get initial position
        try:
            initial_position = (
                master.messages['GLOBAL_POSITION_INT'].lat,
                master.messages['GLOBAL_POSITION_INT'].lon,
                master.messages['GLOBAL_POSITION_INT'].alt)
        except KeyError:
            print("GLOBAL_POSITION_INT message not received yet.")
        
        # Print airspeed, altitude, and heading every 3 seconds
        while True:
            time.sleep(3)
            if threading.active_count() == 1:
                try:
                    airspeed = master.messages['VFR_HUD'].airspeed
                    altitude = master.messages['VFR_HUD'].altitude
                    heading = master.messages['VFR_HUD'].heading
                    print(f"Airspeed: {airspeed}, Altitude: {altitude}, Heading: {heading}")
                except KeyError:
                    print("VFR_HUD message not received yet.")

if __name__ == "__main__":
    threading.Thread(target=user_input).start()
    main()
