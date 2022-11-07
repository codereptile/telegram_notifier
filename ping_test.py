import socket
import threading

HOST, PORT = "localhost", 1235


def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        # print(response)
        return response


CLIENTS_PER_SPAMMER = 3
SPAMMER_THREADS = 2000


def client_spammer(spammer_id):
    for i in range(CLIENTS_PER_SPAMMER):
        unique_str = str(spammer_id) + " " + str(i)
        response = client(HOST, PORT, unique_str)
        if response != unique_str:
            print("ERROR")


for i in range(SPAMMER_THREADS):
    thread = threading.Thread(target=client_spammer, args=(i,))
    thread.start()
