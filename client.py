import socket
import json
import getpass

HOST = 'localhost'      # IP Servidor
PORT = 5000             # Porta Servidor

# Iniciando a conexão
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)





# Função para listar as funções disponíveis e solicitar 
# a execução de uma delas no servidor.
def list_functions():
    
    # Listando as funções disponíveis
    print("Lista de funções disponíveis:")
    print("\t[1] - Listar usuários online")
    print("\t[2] - Listar usuários jogando")
    print("\t[3] - Iniciar um jogo")
    print("\t[0] - Sair")

    # response receebe a opção escolhida pelo usuário
    response = input("\n")


    # caso Listar usuários online
    if(response == "1"):
        tcp.send(response.encode())
        
        # Recebe o tamanho da lista de usuários conectados
        tamanho =int(tcp.recv(1024).decode())

        # Se o tamanho da lista for igual a 0, imprima que não há usuários conectados.
        if(tamanho == 0):
            print("Não há usuários conectados!")
        else:
            # O servidor irá enviar, no formato JSON, a lista de usuários conectados.
            lista_usuarios = json.loads(tcp.recv(1024).decode())

            # Imprime somente o campo "user" e "status" de cada usuário.
            for user in lista_usuarios:
                print(f"{user['user']} - {user['status']}")

        
    
    # caso Listar usuários jogando
    elif response == "2" :

        # Envia a opção escolhida para o servidor
        tcp.send(response.encode())

        # Recebe o tamanho da lista de usuários jogando
        tamanho =int(tcp.recv(1024).decode())

        # Se o tamanho da lista for igual a 0, imprima que não há usuários jogando.
        if(tamanho == 0):
            print("Não há usuários jogando!")
        
        # Caso contrário, o servidor irá enviar, no formato JSON, a lista de usuários jogando.
        else:
            # O servidor irá enviar, no formato JSON, a lista de usuários conectados.
            lista_usuarios = json.loads(tcp.recv(1024).decode())

            # Imprime somente o campo "user" e "status" de cada usuário.
            for user in lista_usuarios:
                print(f"{user['user']} - {user['status']}")

                

    elif(response == "3"):
        tcp.send(b"LIST_USERS_ONLINE")
        lista_usuarios = tcp.recv(1024).decode().split(',')
        for i, user in enumerate(lista_usuarios):
            print(f"{i+1}. {user}")
        user_b_index = int(input("Selecione o índice do usuário com quem deseja iniciar o jogo: ")) - 1
        user_b = lista_usuarios[user_b_index]
        tcp.send(f"GAME_INI:{user_b}".encode())
        resposta = tcp.recv(1024).decode()
        if resposta == "GAME_ACK":
            print("Solicitação de jogo aceita!")
            # Aqui você pode adicionar o código para iniciar o jogo
            while True:
                message = input("Digite sua mensagem: ")
                tcp.send(message.encode())
                if message == "GAME_OVER":
                    break
        elif resposta == "GAME_NEG":
            print("Solicitação de jogo recusada!")
    
    elif(response == "0"):
        print("Saindo...")
        tcp.send(b"EXIT")
        return False

    return True





def get_credentials():
    try:
        with open('credentials.json', 'r') as content:
            credenciais = json.load(content)

            # se o arquivo estiver vazio, inicialize com um dicionário vazio
            if not credenciais:
                credenciais = {}
            


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


def login_request():
    user = input("Digite o seu usuário: ")
    password = getpass.getpass("Digite a sua senha: ")
    print("\n")
    credentials = get_credentials()

    for key, credential in credentials.items():
        if("user" in credential and "password" in credential and user == credential["user"] and password  == credential["password"]):
            print("Usuário autenticado com sucesso!")
            return True, user

    print("Usuário não encontrado!\n")
    response = input("Deseja cadastrar-se? [Y] yes or [N] no: ").strip().upper()    
    if(response == 'Y'):
        create_user()
    elif(response == 'N'):
        return False, None
    else:
        print("Comando inválido!")





# Login do usuário. Login_request() retorna
# True para result e o usuário para user, caso o login tenha sido efetuado com sucesso.
# Caso contrário, retorna False para result e None para user.
result, user = login_request()

# Este loop entra em ação caso o login não tenha sido efetuado com sucesso.
# O usuário poderá tentar logar novamente ou cadastrar-se.
while(result != True):
    result, user = login_request()
destino = (HOST, PORT)
tcp.connect(destino)

# envia o nome do usuário para o servidor
tcp.send(user.encode())

retorno = True
while retorno != False:
    retorno = list_functions()

# Fechando o Socket
tcp.close()
