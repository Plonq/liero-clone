import socket
from _thread import start_new_thread
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "localhost"
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")

nextClientId = 0
pos = {
    "0": "50,50",
    "1": "100,100",
}


def threaded_client(conn):
    global nextClientId, pos
    conn.send(str.encode(str(nextClientId)))
    nextClientId += 1
    while True:
        try:
            data = conn.recv(2048)
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                reply = data.decode("utf-8")
                id, position = reply.split(":")
                pos[id] = position
                print("Recieved: " + position, "from", id)

                other_id = int(id) * -1 + 1
            send_data = f"{other_id}:{pos[str(other_id)]}"
            print("Sending: ", send_data, "to", other_id)
            conn.sendall(str.encode(send_data))
        except Exception as e:
            print("Error:", e)
            break

    print("Connection Closed")
    nextClientId -= 1
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))
