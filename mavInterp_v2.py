from pymavlink import mavutil, mavwp
import time
import threading
import tty
import sys
import termios

# Raw TTY for user input trigger
orig_settings = termios.tcgetattr(sys.stdin)
# Set up the MAVLink connection
connection_string = 'udp:127.0.0.1:14551'  # Replace with your connection string

# Wait for a connection to be established
print(f"GS: Waiting for connection on {connection_string}")
while True:
    try:
        mav = mavutil.mavlink_connection(connection_string)
        mav.wait_heartbeat()
        break
    except:
        pass
    time.sleep(1)
print("GS: Connection established!")


# Set up initial variables
print('Initializing')


# shared vars
global user_typing 
global msg
user_typing = False
user_input = None 
msg = None

# Function to start user init
def readInput():
    global user_typing
    global user_input
    user_typing = False
    while True:
        tty.setcbreak(sys.stdin)
        x=sys.stdin.read(1)[0]
        if x == 'q':
            user_typing = True
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
            user_input = input("OP: ")
        if x == '\n':
            user_typing = False
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
        handle_input(user_input)
        
def handle_input(user_input):
        global msg
        if user_input == "add wp":
            print('added wp 1')
            
        elif user_input == "report battery status":
            battery_msg = mav.recv_match(type='SYS_STATUS', blocking=True)
            battery_voltage = battery_msg.voltage_battery / 1000.0
            print(f"SYS: Battery voltage: {battery_voltage:.2f} V")
        elif user_input == "report location status":
            location_msg = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            latitude = location_msg.lat / 1e7
            longitude = location_msg.lon / 1e7
            print(f"SYS: Latitude: {latitude:.6f}, Longitude: {longitude:.6f}")
        elif user_input == "report orientation status":
            attitude_msg = mav.recv_match(type='ATTITUDE', blocking=True)
            roll = attitude_msg.roll
            pitch = attitude_msg.pitch
            yaw = attitude_msg.yaw
            print(f"SYS: Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")
        elif user_input == "set mode manual":
            mav.set_mode_FBWA()
            print("SYS: mode set manual")
        elif user_input == "set mode auto":
            mav.set_mode_auto()
            print("SYS: mode set auto")
        elif user_input == "set mode loiter":
            mav.set_mode_loiter()
            print("SYS: mode set loiter")
        else:
            print("SYS: unknown command")

def state_callout():
    global user_typing
    while True:
        if user_typing == False:
            airspeed_msg = mav.recv_match(type='VFR_HUD', blocking=True)
            altitude_msg = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            airspeed = airspeed_msg.airspeed
            altitude = altitude_msg.alt / 1e3
            print(f"SYS: Airspeed: {airspeed:.2f} m/s,  Altitude: {altitude:.2f} m")
            time.sleep(1)

# Start the threads
readInput_thread = threading.Thread(target=readInput)
readInput_thread.start()

msg_thread = threading.Thread(target=state_callout)
msg_thread.start()



# Wait for the threads to finish
msg_thread.join()
keypoll_thread.join()
