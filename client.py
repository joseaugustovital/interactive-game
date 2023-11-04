import socket
import json
import getpass
import time

with open("port.txt", "r") as f:
    PORT = int(f.read())

HOST = "localhost"  # IP Servidor
# Iniciando a conexão
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


def recv_json(sock):
    data = ""
    while True:
        try:
            data += sock.recv(1024).decode()
            return json.loads(data)
        except json.JSONDecodeError:
            # Ainda não recebemos o JSON completo, continue lendo
            pass


def start_p2p_connection(user_b, user_b_port_recv):
    # Cria um novo socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # O endereço IP e a porta do usuário B precisariam ser conhecidos de antemão
    # Aqui, estou apenas usando placeholders
    user_b_ip = "localhost"
    user_b_port = int(user_b_port_recv)

    try:
        # Tenta estabelecer uma conexão com o usuário B
        s.connect((user_b_ip, user_b_port))
        print(f"Conexão P2P com {user_b} iniciada!")
        return s
    except Exception as e:
        print(
            f"start_p2p_connection: Não foi possível iniciar a conexão P2P com {user_b}!"
        )
        print(f"Erro: {e}")
        return None


# Função para listar as funções disponíveis e solicitar
# a execução de uma delas no servidor.
def list_functions():
    # Listando as funções disponíveis
    print("-----------------FUNÇÕES-----------------")
    print("|     [1] - Listar usuários online      |")
    print("|     [2] - Listar usuários jogando     |")
    print("|     [3] - Iniciar um jogo             |")
    print("|     [0] - Sair                        |")
    print("-----------------------------------------")

    # response receebe a opção escolhida pelo usuário
    response = input("Selecione uma opção:")
    # caso Listar usuários online
    # caso Listar usuários online
    if response == "1":
        tcp.send(response.encode())
        time.sleep(0.5)

        # Recebe a lista de usuários conectados
        data = tcp.recv(1024).decode()

        # print(data)

        if is_json(data[1:]):
            lista_usuarios = json.loads(data[1:])
        else:
            print("Received data is not a valid JSON")
            lista_usuarios = []

        # Se a lista de usuários estiver vazia, imprima que não há usuários conectados.
        if not lista_usuarios:
            print("Não há usuários conectados!\n")
        else:
            # Imprime user, status, ip e porta de cada usuário.
            for user in lista_usuarios:
                print(
                    f"{user['user']} - {user['status']} - {user['ip']} - {user['porta']}"
                )

    # caso Listar usuários jogando
    elif response == "2":
        # Envia a opção escolhida para o servidor
        tcp.send(response.encode())

        # Recebe o tamanho da lista de usuários jogando
        tamanho = int(tcp.recv(1024).decode())

        # Se o tamanho da lista for igual a 0, imprima que não há usuários jogando.
        if tamanho == 0:
            print("Não há usuários jogando!\n")

        # Caso contrário, o servidor irá enviar, no formato JSON, a lista de usuários jogando.
        else:
            # O servidor irá enviar, no formato JSON, a lista de usuários conectados.
            lista_usuarios = recv_json(tcp)

            # A lista de usuários jogando está no formato
            # Usuário(IP:PORTA) vs Usuário(IP:PORTA)
            # portanto é necessário percorrer a lista de usuários jogando
            # e imprimir cada usuário.
            for user in lista_usuarios:
                print(user)

    elif response == "3":
        response = "GAME_INI"
        tcp.send(response.encode())
        # O usuário tem acesso a lista de usuários com status
        # "INATIVO" ou "ATIVO" por meio da opção [1] - Listar usuários online.
        # Portanto, aqui só é necessário perguntar ao usuário com quem ele deseja jogar.
        user_b = input("Digite o nome do usuário com quem deseja jogar: ")
        # Envia o nome do usuário para o servidor
        tcp.send(user_b.encode())

        # O servidor, ao receber o nome do usuário, irá verificar se o usuário
        # está com o status "INATIVO" ou "ATIVO". Caso esteja "INATIVO", o servidor
        # irá enviar para o usuário "user_b_INATIVO". Caso esteja "ATIVO", o servidor
        # irá enviar para o usuário "user_b_ATIVO".
        # Se "user_b_ATIVO", imprime mensagem que user_b não pode jogar.
        # Se "user_b_INATIVO", imprime mensagem que user_b será notificado sobre o jogo.

        mensagem_recv = tcp.recv(1024)
        complete_msg = mensagem_recv.decode().split("\n")
        mensagem = complete_msg[0]
        user_b_port_response = complete_msg[1]

        print("Status do jogador destino: ", mensagem)
        print("Porta do jogador destino: ", user_b_port_response)
        if mensagem == "ATIVO":
            print(f"O usuário {user_b} não pode jogar no momento!")
        elif mensagem == "INATIVO":
            print(f"O usuário {user_b} será notificado sobre o jogo!\n")

        else:
            print("usuário não encontrado!")

    elif response == "0":
        print("Saindo...")
        tcp.send(b"EXIT")
        return False

    return True


def get_credentials():
    try:
        with open("credentials.json", "r") as content:
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
        newUser = {"name": name, "user": user, "password": password}
        credential[user] = newUser

        with open("credentials.json", "w") as content:
            json.dump(credential, content, indent=4)
        print("Usuário cadastrado com sucesso!")


def login_request():
    print("------------------PORTA------------------")
    print("| Porta recebida pelo servidor:", PORT, "  |")
    print("-----------------------------------------\n")

    print("------------------LOGIN------------------")
    user = input("| Usuário: ")
    password = getpass.getpass("| Senha:         ")
    print("-----------------------------------------")
    credentials = get_credentials()

    for key, credential in credentials.items():
        if (
            "user" in credential
            and "password" in credential
            and user == credential["user"]
            and password == credential["password"]
        ):
            print("| Usuário autenticado com sucesso!      |")
            print("-----------------------------------------\n")
            return True, user

    print("Usuário não encontrado!\n")
    response = input("Deseja cadastrar-se? [Y] yes or [N] no: ").strip().upper()
    if response == "Y":
        create_user()
    elif response == "N":
        return False, None
    else:
        print("Comando inválido!")


# Login do usuário. Login_request() retorna
# True para result e o usuário para user, caso o login tenha sido efetuado com sucesso.
# Caso contrário, retorna False para result e None para user.
result, user = login_request()

# Este loop entra em ação caso o login não tenha sido efetuado com sucesso.
# O usuário poderá tentar logar novamente ou cadastrar-se.
while result != True:
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
