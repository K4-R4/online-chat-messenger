import json
import socket

class Server:
    stream_rate = 4096
    def __init__(self, server_address: str, server_port: int) -> None:
        self.rooms = {}
        self.server_address = server_address
        self.port = server_port
        print('Starting up on {} port {}'.format(server_address, server_port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((server_address, server_port))

    def listen(self):
        self.socket.listen(1)
        while True:
            connection, client_info = self.socket.accept()
            try:
                print('Connection from {}'.format(client_info))
                data  = connection.recvfrom(self.stream_rate)
                print('Received data: {}', data.decode())
                is_success = self.create_chat_room(client_info, json.loads(data.decode()))
                self.send_response(is_success, connection)
            except Exception as e:
                print('Error: {}'.format(str(e)))
            finally:
                print("Closing current connection")
                connection.close()

    def send_response(self, is_success, connection: object) -> None:
        if is_success:
            connection.send(json.dumps({"success": True}).encode())
        else:
            connection.send(json.dumps({"success": False}).encode())

    def create_chat_room(self, client_info: tuple, room_config: dict) -> bool:
        try:
            (client_address, client_port) = client_info
            host = ChatClient(client_address, client_port)
            ChatRoom(room_config, host, self.server_address)
            return True
        except:
            return False

class ChatRoom:
    def __init__(self, room_config:dict, host: object, server_address: str, server_port: int) -> None:
        self.server_address = server_address
        self.port = server_port
        self.title = room_config["title"]
        self.size = room_config["size"]
        self.host = host
        self.participants = {host.get_key(): host}

    # Accept a user unless ChatRoom size is capable and the user is not yet joined
    def join(self, key, chat_client) -> bool:
        if len(self.participants) >= self.size or key in self.participants.keys:
            return False
        self.participants[key] = chat_client
        return True

class ChatClient:
    def __init__(self, address, port) -> None:
        self.address = address
        self.port = port

    def get_key(self) -> str:
        return self.address + ":" + self.port

def main():
    server = Server("127.0.0.1", 9001)
    server.listen()

if __name__ == '__main__':
    main()