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
    try:
        json_object = json.loads(myjson)
    except ValueError:
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
            lista_usuarios = recv_json(tcp)

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

        print("Status do jogador destino: ", mensagem)

        print("Porta do jogador destino: ", user_b_port_response)
        if mensagem == "ATIVO":
            print(f"O usuário {user_b} não pode jogar no momento!")
        elif mensagem == "INATIVO":
            # Estabelece a conexão P2P com o usuário B
            user_a_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # gere uma porta aleatória para o usuário A se conectar
            user_a_socket.bind(("localhost", 0))
            # registre a porta aleatória gerada
            user_a_port = user_a_socket.getsockname()[1]
            user_b_port = int(user_b_port_response)
            print("Porta do usuário B:", user_b_port)
            user_b_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            user_b_socket.bind(("localhost", user_b_port))

            print(f"Tentando estabelecer conexão com {user_b}")

            print(user_a_socket)
            print(user_b_socket)
            # Envia uma mensagem para o usuário B perguntando se ele aceita ou não o convite para o jogo
            # antes de solicitar o input verifique se esta no terminal do usuario b
            # se sim, solicite o input do usuario b e envie para o usuario a
            if user_b_socket.getsockname()[1] == int(user_b_port_response):
                convite_user_b = input("Digite GAME_ACK ou GAME_NEG:")
                user_a_socket.sendto(
                    convite_user_b.encode(), ("localhost", user_b_port)
                )
            else:
                print("Aguardando resposta do usuário B...")
                while True:
                    try:
                        convite, _ = user_b_socket.recvfrom(
                            1024
                        )  # Recebe a mensagem e ignora o endereço do remetente
                        mensagem = (
                            convite.decode()
                        )  # Decodifica a mensagem de bytes para string
                        print(
                            f"Mensagem recebida do usuário B: {mensagem}"
                        )  # Imprime a mensagem recebida no terminal do usuário A
                        break
                    except Exception as e:
                        print(f"Erro ao receber mensagem: {e}")
                        break

                # Envia a resposta do usuário B para o usuário A
                user_a_socket.sendto(convite, ("localhost", user_b_port))

            # usuario b recebe a mensagem
            while True:
                try:
                    convite, _ = user_b_socket.recvfrom(
                        1024
                    )  # Recebe a mensagem e ignora o endereço do remetente
                    mensagem = (
                        convite.decode()
                    )  # Decodifica a mensagem de bytes para string
                    print(
                        f"Mensagem recebida do usuário B: {mensagem}"
                    )  # Imprime a mensagem recebida no terminal do usuário A
                    break
                except Exception as e:
                    print(f"Erro ao receber mensagem: {e}")
                    break

            # Recebe a resposta do usuário B
            # Se o usuário B aceitar o convite, inicie o jogo
            if convite.decode() == "GAME_ACK":
                print("Jogo iniciado!")
                # Inicia o jogo
                # game(user_b_socket)
            elif convite:
                print("O usuário B não aceitou o convite para o jogo!")
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

    # Verifica se o usuário já existe no arquivo credentials.json
    for key, value in credential.items():
        if value["user"] == user:
            print("Nome de usuário já está cadastrado!")
            return

    newUser = {"name": name, "user": user, "password": password, "logged": False}
    credential[len(credential.items())] = newUser

    with open("credentials.json", "w") as content:
        json.dump(credential, content, indent=4)
    print("Usuário cadastrado com sucesso!")


def login_request():
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
            and credential["logged"] == False
        ):
            credential["logged"] = True
            print("| Usuário autenticado com sucesso!      |")
            print("-----------------------------------------\n")

            return True, user

    print("Usuário não encontrado!\n")
    response = input("Deseja cadastrar-se? [S] SIM or [N] NÃO: ").strip().upper()
    if response == "S":
        create_user()
        return False, None  # Adicionado retorno após a criação do usuário
    elif response == "N":
        print("\n")
        return False, None
    else:
        print("Comando inválido!")
        return False, None  # Adicionado retorno para o caso de comando inválido


# Login do usuário. Login_request() retorna
# True para result e o usuário para user, caso o login tenha sido efetuado com sucesso.
# Caso contrário, retorna False para result e None para user.
print("------------------PORTA------------------")
print("| Porta recebida pelo servidor:", PORT, "  |")
print("-----------------------------------------\n")
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
˜˜`