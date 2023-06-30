import json
import socket

class Server:
    def __init__(self, address: tuple, buffer:int=4096) -> None:
        (self.server_address, self.server_port) = address
        self.buffer = buffer
        self.rooms = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(address)
        print('Starting up on {} port {}'.format(self.server_address, self.server_port))
        self.accept()

    def accept(self):
        self.socket.listen(1)
        while True:
            connection, address = self.socket.accept()
            try:
                print('Connection from {}'.format(address))
                data  = connection.recv(self.buffer)
                print('Received data: {}', data.decode())
                is_success = self.create_chat_room(address, json.loads(data.decode()))
                self.send_response(is_success, connection)
            except Exception as e:
                print('Error: {}'.format(str(e)))
            finally:
                print("Closing current connection")
                connection.close()

    def send_response(self, is_success, connection: object) -> None:
        if is_success:
            connection.send(json.dumps({"success": True, "address": "127.0.0.1", "port": 9002}).encode())
        else:
            connection.send(json.dumps({"success": False}).encode())

    def create_chat_room(self, address: tuple, room_config: dict) -> bool:
        # try:
            print('Creating chat room...')
            (client_address, client_port) = address
            host = ChatUser(client_address, client_port)
            ChatRoom(room_config, host, (self.server_address, 9002))
            return True
        # except Exception as e:
        #     print("Failed in creating chat room")
        #     print('Error: {}'.format(str(e)))
        #     return False

class ChatRoom:
    def __init__(self, room_config:dict, host: object, address: tuple, buffer:int=4096) -> None:
        self.title = room_config["title"]
        self.size = room_config["size"]
        self.host = host
        self.participants = {host.get_key(): host}
        (self.server_address, self.server_port) = address
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(address)
        self.accept()

    def accept(self):
        while True:
            try:
                data, address  = self.socket.recvfrom(self.buffer)
                print('Connection from {}'.format(address))
                print('Received data {} from {}', data.decode(), address)
            except Exception as e:
                print('Error: {}'.format(str(e)))
            finally:
                print("Closing current connection")

    # Accept a user unless ChatRoom size is capable and the user is not yet joined
    def join(self, key, chat_client) -> bool:
        if len(self.participants) >= self.size or key in self.participants.keys:
            return False
        self.participants[key] = chat_client
        return True

class ChatUser:
    def __init__(self, address, port) -> None:
        self.address = address
        self.port = port

    def get_key(self) -> str:
        return self.address + ":" + str(self.port)

def main():
    server = Server(("127.0.0.1", 9001))

if __name__ == '__main__':
    main()