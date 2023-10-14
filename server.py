import socket
import json

HOST = '127.0.0.1'      # Endereco IP do Servidor
PORT = 5000             # Porta que o Servidor está

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
origem = (HOST, PORT)

# Colocando um endereço IP e uma porta no Socket
tcp.bind(origem)

# Colocando o Socket em modo passivo
tcp.listen(1)

print('\nServidor TCP iniciado no IP', HOST, 'na porta', PORT,"\n")

def login_request():
    user = input("Digite o seu usuário: ")
    password = input("Digite a sua senha: ")
    print("\n")
    with open("credentials.json","r") as content:
        credentials = json.load(content)

    for key, credential in credentials.items():
        if("user" in credential and "password" in credential and user == credential["user"] and password  == credential["password"]):
            print("Usuário autenticado com sucesso!")
            return True

    print("Usuário não cadatrado! Tente novamente!\n")
    return False

result = login_request()
while(result != True):
    result = login_request()


# Aceitando uma nova conexão


#print("credentials", "\n", credentials)
conexao, cliente = tcp.accept()
print('\nConexão realizada por:', cliente)

while True:
    # Recebendo as mensagens através da conexão
    mensagem = conexao.recv(1024)   
    if not mensagem:
        break

    # Exibindo a mensagem recebida
    print('\nCliente..:', cliente)
    print('Mensagem.:', mensagem.decode())

print('Finalizando conexão do cliente', cliente)

# Fechando a conexão com o Socket
conexao.close()