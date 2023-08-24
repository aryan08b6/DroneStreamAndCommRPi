import cv2
import socket
import pickle
import struct
from dronekit import connect, VehicleMode, LocationGlobalRelative
import multiprocessing


def capture_frames(connection):
    # Set up camera
    camera = cv2.VideoCapture(0)  # Use the appropriate camera index

    while True:
        # Capture frame from camera
        ret, frame = camera.read()

        # Serialize frame and send it over the network
        data = pickle.dumps(frame)
        size = struct.pack('!I', len(data))
        connection.sendall(size)
        connection.sendall(data)


def receive_commands(connection):
    while True:
        # Receive command from the laptop
        command = connection.recv(1024).decode()

        # Print the received command
        print("Received command:", command)

        # Perform actions based on the received command
        if command == "Takeoff":
            print("Taking off...")
            vehicle.mode = VehicleMode("GUIDED")
            vehicle.armed = True
            vehicle.simple_takeoff(2)  # Replace 10 with your desired altitude in meters

        elif command == "Land":
            print("Landing...")
            vehicle.mode = VehicleMode("LAND")

        elif command == "Forward":
            print("Moving forward...")
            vehicle.simple_goto(LocationGlobalRelative(vehicle.location.global_frame.lat + 0.0001,
                                                       vehicle.location.global_frame.lon,
                                                       vehicle.location.global_frame.alt))

        elif command == "Backward":
            print("Moving backward...")
            vehicle.simple_goto(LocationGlobalRelative(vehicle.location.global_frame.lat - 0.0001,
                                                       vehicle.location.global_frame.lon,
                                                       vehicle.location.global_frame.alt))

        elif command == "Left":
            print("Moving left...")
            vehicle.simple_goto(LocationGlobalRelative(vehicle.location.global_frame.lat,
                                                       vehicle.location.global_frame.lon - 0.0001,
                                                       vehicle.location.global_frame.alt))

        elif command == "Right":
            print("Moving right...")
            vehicle.simple_goto(LocationGlobalRelative(vehicle.location.global_frame.lat,
                                                       vehicle.location.global_frame.lon + 0.0001,
                                                       vehicle.location.global_frame.alt))

        elif command == "Stop":
            print("Stopping...")
            vehicle.mode = VehicleMode("LOITER")

        elif command == "END":
            print("Landing...")
            vehicle.mode = VehicleMode("LAND")
            break

        # Add additional commands as needed

    connection.close()


# Set up socket connection
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''  # Use an empty string to accept connections on all available interfaces
port = 8888
server_socket.bind((host, port))
server_socket.listen(5)
connection, address = server_socket.accept()

# Connect to the APM 2.8 drone
vehicle = connect('/dev/ttyACM0', baud=57600, wait_ready=True)  # Adjust the port according to your setup

# Create processes for capturing frames and receiving commands
capture_process = multiprocessing.Process(target=capture_frames, args=(connection,))
receive_process = multiprocessing.Process(target=receive_commands, args=(connection,))

# Start the processes
capture_process.start()
receive_process.start()

# Wait for both processes to finish
capture_process.join()
receive_process.join()

connection.close()
server_socket.close()
