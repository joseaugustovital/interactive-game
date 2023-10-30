import socket
import json
import getpass
import logging

# Configurando o logging
logging.basicConfig(filename='game.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

HOST = 'localhost'      # IP Servidor
PORT = 5000             # Porta Servidor

# Iniciando a conexão
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def list_functions():
    print("Lista de funções disponíveis:")
    print("\t[1] - Listar usuários online")
    print("\t[2] - Listar usuários jogando")
    print("\t[3] - Iniciar um jogo")
    response = input("\n")

    if(response == "1"):
        tcp.send(b"LIST_USERS_ONLINE")
        lista_usuarios = tcp.recv(1024).decode()
        print("Usuários conectados:\n", lista_usuarios)
    elif(response == "2"):
        tcp.send(b"LIST_USERS_PLAYING")
        lista_usuarios = tcp.recv(1024).decode()
        print("Usuários jogando:\n", lista_usuarios)
    elif(response == "3"):
        tcp.send(b"LIST_USERS_ONLINE")
        lista_usuarios = tcp.recv(1024).decode().split(',')
        print("Usuários conectados:")
        for i, user in enumerate(lista_usuarios):
            print(f"{i+1}. {user.split(':')[0]}", end=" ")
        print()
        user_b_index = int(input("Selecione o índice do usuário com quem deseja iniciar o jogo: ")) - 1
        user_b = lista_usuarios[user_b_index].split(':')[0]
        tcp.send(f"GAME_INI:{user_b}".encode())
        resposta = tcp.recv(1024).decode()
        if resposta == "GAME_ACK":
            print("Solicitação de jogo aceita!")
            logging.info(f'Usuário {result} tornou-se ATIVO\n')
            logging.info(f'Usuários {result} e {user_b}: PLAYING\n')
            # Aqui você pode adicionar o código para iniciar o jogo
            while True:
                message = input("Digite sua mensagem: ")
                tcp.send(message.encode())
                if message == "GAME_OVER":
                    logging.info(f'Usuário {result} tornou-se INATIVO\n')
                    break
        elif resposta == "GAME_NEG":
            print("Solicitação de jogo recusada!")
            logging.info(f'Usuário {result} tornou-se INATIVO\n')

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
        credential[user] = newUser

        with open('credentials.json','w') as content:
            json.dump(credential, content, indent=4)
        print("Usuário cadastrado com sucesso!")
        logging.info(f'Usuário {user} realizou cadastro\n')

def login_request():
    user = input("Digite o seu usuário: ")
    password = getpass.getpass("Digite a sua senha: ")
    print("\n")
    credentials = get_credentials()

    for key, credential in credentials.items():
        if("user" in credential and "password" in credential and user == credential["user"] and password  == credential["password"]):
            print("Usuário autenticado com sucesso!")
            logging.info(f'Usuário {user} conectou-se\n')
            return user  # Retornando o nome de usuário

    print("Usuário não encontrado!\n")
    response = input("Deseja cadastrar-se? [Y] yes or [N] no: ").strip().upper()    
    if(response == 'Y'):
        create_user()
    elif(response == 'N'):
        return False
    else:
        print("Comando inválido!")

result = login_request()
while not isinstance(result, str): 
    result = login_request()

destino = (HOST, PORT)
tcp.connect(destino)

tcp.send(result.encode())  # Envie o nome de usuário logo após a conexão ser estabelecida

list_functions()

# Fechando o Socket
tcp.close()
logging.info(f'Usuário {result} desconectou-se da rede\n')
