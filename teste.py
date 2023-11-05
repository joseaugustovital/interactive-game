import socket
import threading


class Server:
    def __init__(self, host="127.0.0.1", port=55553):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()

    def start(self):
        while True:
            client, address = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()

    def handle_client(self, client):
        while True:
            msg = client.recv(1024).decode("ascii")
            if msg:
                print(msg)


class Client:
    def __init__(self, server_host="127.0.0.1", server_port=55553):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((server_host, server_port))

    def send_msg(self, msg):
        self.client.send(msg.encode("utf-8"))


# Inicie o servidor em um thread separado
server = Server()
threading.Thread(target=server.start).start()

# Crie dois clientes e permita que eles se comuniquem entre si (P2P)
client1 = Client()
client2 = Client()

client1.send_msg("Ola do Cliente 1!")
client2.send_msg("Ola do Cliente 2!")
