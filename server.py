import pickle
import socket
import threading
import uuid


class ChatClient:
    def __init__(self, tcp_socket: socket, clt_id: str, address: str, port: int):
        self.clt_id = clt_id
        self.address = address
        self.port = port
        self.tcp_socket = tcp_socket

    def send(self, message: str) -> None:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(message.encode('utf-8'), (self.address, self.port))
        udp_socket.close()


class ChatRoom:
    def __init__(self, name: str, max_clients: int):
        self.name = name
        self.max_clients = max_clients
        self.clients = {}

    def is_full(self) -> bool:
        return len(self.clients) >= self.max_clients

    def add_client(self, clt_id: str, client: ChatClient) -> None:
        self.clients[clt_id] = client

    def remove_client(self, clt_id: str) -> None:
        self.clients.pop(clt_id)

    def send_to_all(self, from_id: str, message: str) -> None:
        for clt_id, client in self.clients.items():
            if clt_id == from_id:
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
            clt_id = uuid.uuid4()
            client = ChatClient(conn, str(clt_id), clt_address, clt_port)
            conn.send(f'{clt_address}:{clt_port}:{clt_id}'.encode('utf-8'))
            print(f'Client {client.clt_id} connected')

            thread = threading.Thread(target=self.establish_chat, args=(client,))
            thread.start()

    def establish_chat(self, client: ChatClient) -> None:
        self.notify_available_rooms(client)
        room_name = self.create_room(client)

        while True:
            data, _ = self.udp_socket.recvfrom(1024)
            data_str = data.decode()
            from_id = data_str[0:data_str.find(':')]
            msg = f'> {data_str}'
            self.chat_rooms[room_name].send_to_all(from_id, msg)
            print(msg)
            if data is None:
                break

        client.tcp_socket.close()

    def create_room(self, client: ChatClient) -> str:
        data = client.tcp_socket.recv(self.buffer_size)
        data_str = data.decode('utf-8')

        room_name, cnf = data_str.split(':', 1)
        if cnf == "join":
            self.chat_rooms[room_name].add_client(client.clt_id, client)
        else:
            new_room = ChatRoom(room_name, int(cnf))
            self.chat_rooms[room_name] = new_room
            self.chat_rooms[room_name].add_client(client.clt_id, client)

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
