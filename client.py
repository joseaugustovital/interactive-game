import socket
import json
import getpass
import time


with open("port.txt", "r") as f:
    PORT = int(f.read())

HOST = "localhost"  # IP Servidor
# Iniciando a conexão
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def list_user_online():
    """
    Lista os usuários online.
    """
    response = "1"
    tcp.send(response.encode())
    time.sleep(0.5)

    # Recebe a lista de usuários conectados
    data = tcp.recv(1024).decode()

    # print(data)

    if is_json(data[1:]):
        lista_usuarios = json.loads(data[1:])
    else:
        lista_usuarios = []

    # Se a lista de usuários estiver vazia, imprima que não há usuários conectados.
    if not lista_usuarios:
        print("\nNão há usuários conectados!\n")
    else:
        max_len_user = len("User")
        max_len_status = len("Status")
        max_len_ip = len("IP")
        max_len_porta = len("Porta")

        for user in lista_usuarios:
            max_len_user = max(max_len_user, len(user["user"]))
            max_len_status = max(max_len_status, len(user["status"]))
            max_len_ip = max(max_len_ip, len(user["ip"]))
            max_len_porta = max(max_len_porta, len(str(user["porta"])))

        total_len = max_len_user + max_len_status + max_len_ip + max_len_porta + 13

        print("\n")
        print("{:-^{}}".format(" USUÁRIOS-ONLINE ", total_len))
        print(
            "| {:^{}} | {:^{}} | {:^{}} | {:^{}} |".format(
                "User",
                max_len_user,
                "Status",
                max_len_status,
                "IP",
                max_len_ip,
                "Porta",
                max_len_porta,
            )
        )
        print("{:-^{}}".format("", total_len))
        for user in lista_usuarios:
            print(
                "| {:^{}} | {:^{}} | {:^{}} | {:^{}} |".format(
                    user["user"],
                    max_len_user,
                    user["status"],
                    max_len_status,
                    user["ip"],
                    max_len_ip,
                    user["porta"],
                    max_len_porta,
                )
            )
        print("{:-^{}}\n".format("", total_len))


def is_json(myjson):
    """
    Verifica se uma string é um objeto JSON válido.
    """
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


def recv_json(sock):
    """
    Recebe um objeto JSON de um socket.
    """
    data = ""
    while True:
        try:
            data += sock.recv(1024).decode()
            return json.loads(data)
        except json.JSONDecodeError:
            # Ainda não recebemos o JSON completo, continue lendo
            pass


def receive_messages():
    """
    Recebe mensagens do servidor.
    """
    while True:
        try:
            data = tcp.recv(1024)
            if not data:
                break
            print(data.decode())
        except:
            break


def list_functions():
    """
    Lista as funções disponíveis e solicita a execução de uma delas no servidor.
    """
    # Listando as funções disponíveis
    print("-----------------FUNÇÕES-----------------")
    print("|     [1] - Listar usuários online      |")
    print("|     [2] - Listar usuários jogando     |")
    print("|     [3] - Iniciar um jogo             |")
    print("|     [0] - Sair                        |")
    print("-----------------------------------------")

    # response recebe a opção escolhida pelo usuário
    response = input("Selecione uma opção:")
    # caso Listar usuários online
    if response == "1":
        list_user_online()

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
            lista_usuarios = json.loads(tcp.recv(1024).decode())

            # A lista de usuários jogando está no formato
            # Usuário(IP:PORTA) vs Usuário(IP:PORTA)
            # portanto é necessário percorrer a lista de usuários jogando
            # e imprimir cada usuário.
            for user in lista_usuarios:
                print(user)

    elif response == "3":
        list_user_online()
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
        list_connected_users = complete_msg[2]

        print(f"Status do jogador destino: {mensagem}")

        if mensagem == "ATIVO":
            print(f"O usuário {user_b} não pode jogar no momento!")
        elif mensagem == "INATIVO":
            # porta do usuário A que é a porta deste cliente
            user_a_port = int(tcp.getsockname()[1])
            # porta do usuário B
            user_b_port = int(user_b_port_response)

            # printe as portas
            print(f"Porta do usuário A: {user_a_port}")
            print(f"Porta do usuário B: {user_b_port}")

    elif response == "0":
        print("Saindo...")
        tcp.send(b"EXIT")
        return False

    return True


def get_credentials():
    """
    Obtém as credenciais do usuário a partir do arquivo credentials.json.
    """
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
    """
    Cria um novo usuário.
    """
    credential = get_credentials()
    name = input("Digite o seu nome: ")
    user = input("Digite o seu usuário: ")
    password = getpass.getpass("Digite a sua senha: ")
    print("\n")

    # Verifica se o usuário já existe no arquivo credentials.json
    for _, value in credential.items():
        if "user" in value and value["user"] == user:
            print("Nome de usuário já está cadastrado!")
            return

    newUser = {"name": name, "user": user, "password": password}
    credential[len(credential)] = newUser

    with open("credentials.json", "w") as content:
        json.dump(credential, content, indent=4)
    print("Usuário cadastrado com sucesso!")


def login_request():
    """
    Realiza o login do usuário.
    """
    print("------------------LOGIN------------------")
    user = input("| Usuário: ")
    password = getpass.getpass("| Senha:         ")
    print("-----------------------------------------")
    credentials = get_credentials()

    for _, credential in credentials.items():
        if (
            "user" in credential
            and "password" in credential
            and user == credential["user"]
            and password == credential["password"]
            # and not credential["logged"]
        ):
            print("| Usuário autenticado com sucesso!      |")
            print("-----------------------------------------\n")
            # Atualiza o arquivo credentials.json com o usuário logado (logged = True)
            # credential["logged"] = True
            # with open("credentials.json", "w") as content:
            #     json.dump(credentials, content, indent=4)

            return True, user

    print("Usuário não encontrado!\n")
    response = input("Deseja cadastrar-se? [S] SIM or [N] NÃO: ").strip().upper()
    if response == "S":
        create_user()
        return False, None
    elif response == "N":
        print("\n")
        return False, None
    else:
        print("Comando inválido!")
        return False, None


print("------------------PORTA------------------")
print(f"| Porta recebida pelo servidor: {PORT}  |")
print("-----------------------------------------\n")
result, user = login_request()

# Este loop entra em ação caso o login não tenha sido efetuado com sucesso.
# O usuário poderá tentar logar novamente ou cadastrar-se.
while not result:
    result, user = login_request()

destino = (HOST, PORT)
tcp.connect(destino)

# envia o nome do usuário para o servidor
tcp.send(user.encode())

retorno = True

while retorno:
    retorno = list_functions()

# Fechando o Socket
tcp.close()
