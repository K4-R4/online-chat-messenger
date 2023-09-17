import pickle
import socket
import threading


class ChatRoom:
    def __init__(self, title: str, max_clients: int):
        self.title = title
        self.max_clients = max_clients
        self.clients = {}

    def is_full(self) -> bool:
        return len(self.clients) >= self.max_clients

    def add_client(self, client_id: str, client: object) -> None:
        self.clients[client_id] = client

    def remove_client(self, client_id) -> None:
        self.clients.pop(client_id)

    def send_to_all(self, from_id, message: str) -> None:
        for client_id, client in self.clients:
            if client_id == from_id:
                continue
            client.send(message)


class ChatClient:
    def __init__(self, tcp_socket: object, address: str, port: str):
        self.address = address
        self.port = port
        self.tcp_socket = tcp_socket

    def send(self, message: str) -> None:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(message.encode('utf-8'), (self.address, self.port))
        udp_socket.close()


class Server:
    def __init__(self, address: str, port: str):
        self.address = address
        self.port = port
        self.chat_rooms = {}
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.address, self.port))

        self.wait_client_conn()

    def wait_client_conn(self) -> None:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind((self.address, self.port))
        tcp_socket.listen()

        while True:
            conn, client_address = tcp_socket.accept()
            address, port = client_address

            client = ChatClient(address, port)
            conn.send(f'{address}:{port}'.encode('utf-8'))
            threading.Thread(target=self.establish_chat, args=(client,))

    def establish_chat(self, client) -> None:
        available_rooms = self.get_available_rooms()
        # notify a client of available rooms
        keys = pickle.dumps(available_rooms)
        client.tcp_socket.send(keys)
        # todo

    def get_available_rooms(self) -> []:
        available_rooms = []
        for _, chat_room in self.chat_rooms:
            if not chat_room.is_full():
                available_rooms.append(chat_room)
        return available_rooms
