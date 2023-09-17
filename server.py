import pickle
import socket
import sys
import threading


class ChatClient:
    def __init__(self, tcp_socket: socket, address: str, port: int):
        self.address = address
        self.port = port
        self.tcp_socket = tcp_socket

    def send(self, message: str) -> None:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(message.encode('utf-8'), (self.address, self.port))
        udp_socket.close()

    def get_id(self) -> str:
        return f'{self.address}:{self.port}'


class ChatRoom:
    def __init__(self, name: str, max_clients: int):
        self.name = name
        self.max_clients = max_clients
        self.clients = {}

    def is_full(self) -> bool:
        return len(self.clients) >= self.max_clients

    def add_client(self, client_id: str, client: ChatClient) -> None:
        self.clients[client_id] = client

    def remove_client(self, client_id) -> None:
        self.clients.pop(client_id)

    def send_to_all(self, from_id, message: str) -> None:
        for client_id, client in self.clients:
            if client_id == from_id:
                continue
            client.send(message)


class Server:
    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port
        self.chat_rooms = {}
        self.buffer_size = 1024
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.address, int(self.port)))

        thread = threading.Thread(target=self.wait_client_conn)
        thread.start()

    def wait_client_conn(self) -> None:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind((self.address, self.port))
        tcp_socket.listen()

        while True:
            conn, client_info = tcp_socket.accept()
            clt_address, clt_port = client_info
            client = ChatClient(conn, clt_address, clt_port)
            conn.send(f'{clt_address}:{clt_port}'.encode('utf-8'))

            thread = threading.Thread(target=self.establish_chat, args=(client,))
            thread.start()

    def establish_chat(self, client: ChatClient) -> None:
        self.notify_available_rooms(client)
        room_name = self.establish_room(client)

        while True:
            data, _ = self.udp_socket.recvfrom(1024)
            client_id = client.get_id()
            msg = f'{client_id}> {data.decode()}'
            self.chat_rooms[room_name].broadcast(client_id, msg)
            print(msg)
            if data is None:
                break

        client.tcp_socket.close()

    def establish_room(self, client: ChatClient) -> str:
        data = client.tcp_socket.recv(self.buffer_size)
        data_str = data.decode('utf-8')

        room_name, cnf = data_str.split(':', 1)
        if cnf == "join":
            self.chat_rooms[room_name].add_client(client.get_id(), client)
        else:
            new_room = ChatRoom(room_name, int(cnf))
            self.chat_rooms[room_name] = new_room
            self.chat_rooms[room_name].add_client(client.get_id(), client)

        return room_name

    def get_available_rooms(self) -> []:
        available_rooms = []
        for room_name, chat_room in self.chat_rooms.items():
            if not chat_room.is_full():
                available_rooms.append(room_name)
        return available_rooms

    def notify_available_rooms(self, client: ChatClient):
        available_rooms = self.get_available_rooms()
        keys = pickle.dumps(available_rooms)
        client.tcp_socket.send(keys)


def main():
    address = "localhost"
    port = 50000
    Server(address, port)


if __name__ == '__main__':
    main()
