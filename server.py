import socket
import threading
import json
import datetime
from random_port import result
import json

HOST = "127.0.0.1"  # Endereco IP do Servidor
PORT = result  # Porta que o Servidor está

# Escreve a porta no arquivo
with open("port.txt", "w") as f:
    f.write(str(result))


# crie um metoodo para atribuir como false o campo logged de quem se desconectou
# e o status para INATIVO   para que o usuário não apareça na lista de usuários conectados
# enquanto ele não estiver conectado
def reset_user_info(user, connected_users):
    for element in connected_users:
        if element["user"] == user:
            element["logged"] = False
            element["status"] = "INATIVO"


def send_large_data(conexao, data):
    data = json.dumps(data).encode()
    inicio = 0
    tamanho = len(data)

    while inicio < tamanho:
        # Enviar pedaços de 1024 bytes
        bytes_enviados = conexao.send(data[inicio : inicio + 1024])
        inicio += bytes_enviados


# Esta função log_event é usada para registrar eventos em um arquivo
# de log chamado "game.log". Ela recebe uma mensagem de evento como
# entrada e grava a data e hora atual juntamente com a mensagem no arquivo.
def log_event(event):
    with open("game.log", "a") as log_file:
        log_file.write(f"{datetime.datetime.now()}: {event}\n")


# A função handle_client é chamada para lidar com cada cliente conectado ao servidor.
# Ela recebe a conexão, informações do cliente e a lista de usuários conectados como argumentos.
def handle_client(conexao, cliente, connected_users):
    # Receba o nome de usuário quando um cliente se conectar
    username = conexao.recv(1024).decode()
    print("Usuário conectado:", username)
    # Adicionar o usuário à lista de usuários conectados
    connected_users.append(
        {
            "user": username,
            "status": "INATIVO",  # Atribuir o status como "ATIVO" quando um cliente se conectar
            "ip": cliente[0],
            "porta": cliente[1],
        }
    )

    # Retornando quem conectou no servidor
    print(
        "["
        + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + "]"
        + ": Conexão realizada por",
        username + " na porta",
        cliente[1],
    )

    while True:
        mensagem = conexao.recv(1024)

        if not mensagem:
            break

        # Caso LIST_USERS_ONLINE
        if mensagem.decode() == "1":
            # Busca todos os usuários conectados INATIVOS ou ATIVOS
            # que sejam diferentes do usuário que está solicitando a lista
            # de usuários conectados.
            lista_usuarios = [
                user for user in connected_users if user["user"] != username
            ]
            lista_usuarios_size = str(len(lista_usuarios))
            # Envia o tamanho da lista de usuários conectados
            conexao.send(lista_usuarios_size.encode())

            # Se o tamanho da lista for maior que 0, envie a lista de usuários conectados
            if int(lista_usuarios_size) > 0:
                lista_usuarios_json = json.dumps(lista_usuarios)
                # Envia a lista de usuários conectados
                conexao.send(json.dumps(lista_usuarios).encode())

        # Caso LIST_USERS_PLAYING
        elif mensagem.decode() == "2":
            # Busca todos os usuários conectados com status JOGANDO e diferente do usuário que está solicitando a lista
            # de usuários conectados.
            lista_usuarios = [
                user
                for user in connected_users
                if user["user"] != username and user["status"] == "ATIVO"
            ]

            # Envia o tamanho da lista de usuários conectados
            conexao.send(str(len(lista_usuarios)).encode())

            # Se o tamanho da lista for maior que 0, envie a lista de usuários conectados
            if len(lista_usuarios) > 0:
                # Envia a lista de usuários conectados
                send_large_data(conexao, lista_usuarios)

        elif mensagem.decode() == "GAME_INI":
            user = conexao.recv(1024)
            user_b = user.decode()
            print("\nUsuário destino:", user_b)
            # Encontre o socket do usuário B
            user_b_socket = None
            user_b_status = None
            for user in connected_users:
                if user["user"] == user_b:
                    user_b_socket = user["porta"]
                    user_b_status = user["status"]
                    break
            # Verifique se o usuário B foi encontrado
            if user_b_socket is None:
                print(f"Usuário {user_b} não encontrado.")
                continue
            # Envie uma mensagem para o usuário B perguntando se ele aceita ou não o convite para o jogo
            b_status_port = str(user_b_status) + "\n" + str(user_b_socket)
            conexao.send(b_status_port.encode())

        elif mensagem == b"EXIT":
            conexao.send(b"EXIT")
            break

        print("\nCliente..:", cliente)
        if isinstance(mensagem, str):
            mensagem = mensagem.encode()
        print("Mensagem.:", mensagem.decode())

    print("Finalizando conexão do cliente", cliente)
    # precisamos alterar o "logged": true para "logged": false
    # para que o usuário possa se conectar novamente
    # e também precisamos alterar o status para INATIVO
    # para que o usuário não apareça na lista de usuários conectados
    # enquanto ele não estiver conectado
    # Lê o conteúdo do arquivo "credentials.json" e armazena em uma variável
    with open("credentials.json", "r") as content:
        credentials = json.load(content)

    # Atualiza a propriedade "logged" do usuário para False
    for user in credentials["users"]:
        if user["username"] == username:
            user["logged"] = False

    # Escreve as alterações no arquivo "credentials.json"
    with open("credentials.json", "w") as content:
        if user["username"] == username:
            user["logged"] = False
        json.dump(credentials, content, indent=4)


tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
origem = (HOST, PORT)

tcp.bind(origem)

tcp.listen(5)

connected_users = []
print("---------------------------------------------------")
print("| Porta gerada pelo arquivo random_post.py:", PORT, "|")
print("|-------------------------------------------------|")
print("| Servidor TCP iniciado com sucesso!              |")
print("| [IP]:", HOST, "                                |")
print("| [PORTA]:", PORT, "                                 |")
print("---------------------------------------------------")

running = True


def server_thread():
    while running:
        conexao, cliente = tcp.accept()
        client_handler = threading.Thread(
            target=handle_client, args=(conexao, cliente, connected_users)
        )
        client_handler.start()


server = threading.Thread(target=server_thread)
server.start()

while True:
    command = input()
    if command.lower() == "stop":
        running = False
        tcp.close()
