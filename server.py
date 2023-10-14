import socket
import threading
import json

HOST = '127.0.0.1'  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor está

def handle_client(conexao, cliente, connected_users):
    # Atribuindo ao usuário recém conectado o status como ATIVO
    client_status = 'ATIVO'
    # Retornando quem conectou no servidor
    print('\nConexão realizada por:', cliente)
    # Retornando o status do usuário
    print('STATUS['+str(cliente[1])+']:', client_status)

    while True:
        mensagem = conexao.recv(1024)
        if not mensagem:
            break
        if mensagem == b"LIST_USERS":
            lista_usuarios = json.dumps(connected_users)
            conexao.send(lista_usuarios.encode())
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
    connected_users.append({
        "user": "",
        "status": "",
        "ip": cliente[0],
        "porta": cliente[1]
    })
    client_handler = threading.Thread(target=handle_client, args=(conexao, cliente, connected_users))
    client_handler.start()
