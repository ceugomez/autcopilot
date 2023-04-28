from pymavlink import mavutil
import time

# Set up the MAVLink connection
connection_string = 'udp:127.0.0.1:5761'  # Replace with your connection string

# Wait for a connection to be established
print("Waiting for connection...")
while True:
    try:
        mav = mavutil.mavlink_connection(connection_string)
        mav.wait_heartbeat()
        break
    except:
        pass
    time.sleep(1)
print("Connection established!")

# Main loop to read and print MAVLink messages
while True:
    # Wait for a message and print its type
    msg = mav.recv_match()
    if msg == None:
        #print(f"MSG: None")
        continue
    else:
        msg_type = msg.get_type()
        print(f"Received message of type: {msg_type}")

    