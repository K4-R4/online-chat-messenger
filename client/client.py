import json
import socket
import sys

class Client:
    stream_rate = 4096
    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = input("Type in the server's address to connect to: ")
        self.server_port = input("Type in server's port to connect to: ")
        print('Connecting to {}'.format(self.server_address, self.server_port))

    def connetct(self):
        try:
            self.socket.connect((self.server_address, int(self.server_port)))
        except socket.error as e:
            print(e)
            sys.exit(1)

    def send_data(self, room_config: str):
        self.socket.send(room_config.encode())
        print("server response: {}".format(self.receive_response()))

    def receive_response(self) -> str:
        return self.socket.recv(self.stream_rate).decode()

def main():
    argc = len(sys.argv)
    if argc != 3:
        print('Usage: python3 client.py {title} {max participants}')
        exit(1)
    room_config = {"title": sys.argv[1], "max_participants": sys.argv[2]}
    client = Client()
    client.connetct()
    client.send_data(json.dumps(room_config))

if __name__ == "__main__":
	main()