import socket
import threading
import json

HOST = '127.0.0.1'  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor está

def handle_client(conexao, cliente, connected_users):
    # Atribuindo ao usuário recém conectado o status como ATIVO
    for user in connected_users:
        if user["ip"] == cliente[0] and user["porta"] == cliente[1]:
            user["status"] = "ATIVO"
    
    # Retornando quem conectou no servidor
    print('\nConexão realizada por:', cliente)
 
    while True:
        mensagem = conexao.recv(1024)
        if not mensagem:
            break
        if mensagem == b"LIST_USERS_ONLINE":
            lista_usuarios = [user for user in connected_users if user["status"] == "ATIVO"]
            conexao.send(json.dumps(lista_usuarios).encode())
        elif mensagem == b"LIST_USERS_PLAYING":
            lista_usuarios = [user for user in connected_users if user["status"] == "JOGANDO"]
            conexao.send(json.dumps(lista_usuarios).encode())
        elif mensagem == b"GAME_INI":
            # Aqui você pode adicionar a lógica para aceitar ou recusar a solicitação de jogo.
            # Por exemplo, se o usuário já estiver jogando, você pode recusar a solicitação.
            conexao.send(b"GAME_ACK")  # Ou b"GAME_NEG"
        print('\nCliente..:', cliente)
        print('Mensagem.:', mensagem.decode())
    print('Finalizando conexão do cliente', cliente)
    conexao.close()


tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
origem = (HOST, PORT)

tcp.bind(origem)
tcp.listen(5)

connected_users = []
print('\nServidor TCP iniciado no IP', HOST, 'na porta', PORT, "\n")

while True:
    conexao, cliente = tcp.accept()
    print("client", conexao)
    connected_users.append({
        "user": "",
        "status": "ATIVO",  # Atribuir o status como "ATIVO" quando um cliente se conecta
        "ip": cliente[0],
        "porta": cliente[1],
    })
    client_handler = threading.Thread(target=handle_client, args=(conexao, cliente, connected_users))
    client_handler.start()
