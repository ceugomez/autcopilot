from pymavlink import mavutil
import time
import threading

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

# Function to print message types
def print_messages():
    while True:
        # Wait for a message and print its type
        msg = mav.recv_match()
        if msg == None:
            continue
        else:
            msg_type = msg.get_type()
            print(f"GS: Received message of type: {msg_type}")
            time.sleep(5)

# Function to handle user input
def handle_input():
    while True:
        # Get user input
        user_input = input("OP: ")

        # Check if the user requested battery status
        if user_input == "report battery status":
            # Get the battery status message
            bat_msg = mav.recv_match(type="SYS_STATUS")

            # Check if the message was received successfully
            if bat_msg is not None:
                # Print the battery status
                bat_voltage = bat_msg.voltage_battery / 1000.0
                print(f"SYS: Battery voltage: {bat_voltage} V")
                bat_remaining = bat_msg.battery_remaining
                print(f"SYS: Battery remaining: {bat_remaining} %")
            else:
                print("GS: Battery status message not received")

        # Check if the user requested location status
        if user_input == "report location status":
            # Get the GPS message
            gps_msg = mav.recv_match(type="GLOBAL_POSITION_INT")
            
            # Check if the message was received successfully
            if gps_msg is not None:
                # Print the latitude and longitude
                lat = gps_msg.lat / 1e7
                lon = gps_msg.lon / 1e7
                print(f"Latitude: {lat}, Longitude: {lon}")
            else:
                print("GPS message not received")    
        
        # Check if the user requested orientation status
        if user_input == "report orientation status":
            # Get the attitude message
            att_msg = mav.recv_match(type="ATTITUDE")
            
            # Check if the message was received successfully
            if att_msg is not None:
                # Print the roll, pitch, and yaw
                roll = att_msg.roll
                pitch = att_msg.pitch
                yaw = att_msg.yaw
                print(f"Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}")
            else:
                print("Attitude message not received")



# Start the threads
msg_thread = threading.Thread(target=print_messages)
msg_thread.start()

input_thread = threading.Thread(target=handle_input)
input_thread.start()

# Wait for the threads to finish
msg_thread.join()
input_thread.join()