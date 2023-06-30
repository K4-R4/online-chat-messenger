import json
import socket
import sys
import time

class Client:
    def __init__(self, buffer:int=4096) -> None:
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = input("Type in the server's address to connect to: ")
        self.server_port = input("Type in server's port to connect to: ")
        print('Connecting to {}'.format(self.server_address, self.server_port))

    def connetct(self):
        try:
            self.socket.connect((self.server_address, int(self.server_port)))
        except socket.error as e:
            print('Error: {}', e)
            sys.exit(1)

    def send_data(self, room_config: dict):
        self.socket.send(json.dumps(room_config).encode())
        response = self.receive_response()
        if response["success"]:
            print("Chat room was created")
            self.start_chat(response)
        else:
            print("Failed in creating chat room")
            exit(1)

    def receive_response(self) -> dict:
        time.sleep(2)
        return json.loads(self.socket.recv(self.buffer).decode())

    def start_chat(response):
        ChatClient((response["address"], response["port"]))

class ChatClient:
    def __init__(self, address:tuple, buffer:int=4096) -> None:
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        (self.server_address, self.server_port) = address
        print('Starting chat')
        self.send_data()

    def send_data(self):
        while True:
            try:
                print('Input any messages')
                message = input()
                self.socket.sendto(message.encode(), (self.server_address, self.server_port))
            except Exception as e:
                self.socket.close()
                print('Error: {}'.format(str(e)))
                exit(1)

def main():
    argc = len(sys.argv)
    if argc != 3:
        print('Usage: python3 client.py {title} {size}')
        exit(1)
    room_config = {"title": sys.argv[1], "size": sys.argv[2]}
    client = Client()
    client.connetct()
    client.send_data(room_config)

if __name__ == "__main__":
	main()