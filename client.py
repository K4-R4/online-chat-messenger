import pickle
import socket
import sys
import threading


class Client:
    def __init__(self, svr_address: str, svr_port: int):
        self.clt_id = ""
        self.svr_address = svr_address
        self.svr_port = svr_port
        self.room_name = ""
        self.room_address = ""
        self. room_port = -1
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.connect_server()
        self.join_room()
        thread = threading.Thread(target=self.receive)
        thread.start()
        self.send()

    def connect_server(self):
        try:
            self.tcp_socket.connect((self.svr_address, self.svr_port))
        except socket.error as err:
            print(err)
            sys.exit(1)

    def join_room(self):
        # todo
        data = self.tcp_socket.recv(1024)
        data_str = data.decode('utf-8')
        self.room_address, self.room_port, self.clt_id = data_str.split(":", 2)

        data = self.tcp_socket.recv(1024)
        available_room = pickle.loads(data)
        print(available_room)
        room_name = input('Select room or Input new room: ')
        self.room_name = room_name
        if room_name in available_room:
            room_cnf = f'{room_name}:join'
            self.tcp_socket.send(room_cnf.encode('utf-8'))
        else:
            max_clients = input('Input max clients: ')
            room_cnf = f'{room_name}:{max_clients}'
            self.tcp_socket.send(room_cnf.encode('utf-8'))

    def receive(self):
        self.udp_socket.bind((self.room_address, int(self.room_port)))
        while True:
            try:
                data, address = self.udp_socket.recvfrom(1024)
                if data:
                    data_str = data.decode('utf-8')
                    print(f'\n{data_str}')
                else:
                    break
            except ConnectionResetError:
                break

    def send(self):
        while True:
            msg = input('Enter a message (or "quit" to exit): ')
            if msg == 'quit':
                break
            formatted_msg = f'{self.clt_id}:{self.room_name}:{len(msg)}:{msg}'
            self.udp_socket.sendto(formatted_msg.encode("utf-8"), (self.svr_address, int(self.svr_port)))

        self.tcp_socket.close()
        self.udp_socket.close()
        print('Disconnected from the server.')


def main():
    svr_address = "localhost"
    svr_port = 50000
    Client(svr_address, svr_port)


if __name__ == '__main__':
    main()
