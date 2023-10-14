import socket
import json
import getpass

HOST = 'localhost'      # IP Servidor
PORT = 5000             # Porta Servidor

# Iniciando a conexão
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def get_credentials():
    try:
        with open('credentials.json', 'r') as content:
            credenciais = json.load(content)
    except FileNotFoundError:
        credenciais = {}
    return credenciais

def create_user():
    credential = get_credentials()
    name = input("Digite o seu nome: ")
    user = input("Digite o seu usuário: ")
    password = getpass.getpass("Digite a sua senha: ")
    print("\n")

    if user in credential:
        print("Nome de usuário já está cadastrado!")
    else:
        newUser = {
            "name" : name,
            "user" : user,
            "password" : password
        }
        newIndex = str(len(credential))
        credential[newIndex] = newUser

        with open('credentials.json','w') as content:
            json.dump(credential, content, indent=4)
        print("Usuário cadastrado com sucesso!")
 
def login_request():
    user = input("Digite o seu usuário: ")
    password = getpass.getpass("Digite a sua senha: ")
    print("\n")
    credentials = get_credentials()

    for key, credential in credentials.items():
        if("user" in credential and "password" in credential and user == credential["user"] and password  == credential["password"]):
            print("Usuário autenticado com sucesso!")
            return True

    print("Usuário não encontrado!\n")
    response = input("Deseja cadastrar-se? [Y] yes or [N] no: ").strip().upper()    
    if(response == 'Y'):
        create_user()
    elif(response == 'N'):
        return False
    else:
        print("Comando inválido!")

result = login_request()
while(result != True):
    result = login_request()
destino = (HOST, PORT)
tcp.connect(destino)


print('\nDigite suas mensagens')
print('Para sair use CTRL+X\n')

# Recebendo a mensagem do usuário final pelo teclado
mensagem = input()

# Enviando a mensagem para o Servidor TCP através da conexão
while mensagem != '\x18':
    tcp.send(str(mensagem).encode())
    mensagem = input()

# Fechando o Socket
tcp.close()