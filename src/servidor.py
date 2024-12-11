from socket import *
import threading
import hashlib

online_clients = {}
available_images = {}

def handle_register(message, client_address, server):
    """
    Recebe uma SENHA escolhida pelo cliente, um NÚMERO DE PORTA escolhido para conexões TCP, 
    e uma lista de IMAGENS para que o cliente possa compartilhá-las.
    """
    values = message.split(" ")
    if len(values) < 4:
        response = '\033[31mERR INVALID_MESSAGE_FORMAT\033[0m'
    else:
        client_password = values[1]
        client_port = values[2]
        client_images = values[3]
    
    splitted_images = client_images.split(';')
    images = []

    """
    O loop for itera sobre o dicionário online_clients, onde cada entrada consiste no endereço de um cliente como chave e um 
    dicionário de detalhes do cliente (senha e porta) como valor. Para cada cliente, o loop imprime o endereço do cliente, 
    a porta TCP e a senha hash no terminal ou console do servidor.
    """
    for images_info in splitted_images:
        try:
            image_md5, image_name = images_info.split(',')
            images.append({'md5': image_md5, 'name': image_name})
        except ValueError:
            response = '\033[31mERR INVALID_MESSAGE_FORMAT\033[0m'
            server.sendto(response.encode(), client_address)
            return
    
    hashed_pass = hashlib.sha256(client_password.encode()).hexdigest()
    online_clients[client_address] = {'password': hashed_pass, 'port': client_port}
    available_images[client_address] = images

    num_images = len(images)
    response = f'\033[32mOK {num_images}_REGISTERED_IMAGES\033[0m'
    
    for client, info in online_clients.items():
        print(f"Client: {client}, TCP Port: {info['port']}, PASS: {info['password']}")

    server.sendto(response.encode(), client_address)
    server.sendto("END".encode(), client_address)


def handle_update(message, client_address, server):
    """
    A função recebe uma mensagem do cliente, verifica se o formato é válido e autentica o cliente comparando a senha fornecida 
    com a armazenada para o endereço IP. Em seguida, processa as informações das imagens enviadas, adicionando apenas aquelas que 
    ainda não estão registradas. Se a imagem já existir, informa no console. Por fim, a função 
    envia uma resposta confirmando o número de novas imagens registradas ou avisando que não há novas imagens para adicionar.
    """
    values = message.split(" ")
    if len(values) < 4:
        response = '\033[31mERR INVALID_MESSAGE_FORMAT\033[0m'
        server.sendto(response.encode(), client_address)
        return

    client_password = values[1]
    client_port = values[2]
    client_images = values[3]

    hashed_pass = hashlib.sha256(client_password.encode()).hexdigest()
    stored_pass = online_clients.get(client_address, {}).get('password')

    if hashed_pass != stored_pass:
        response = '\033[31mERR IP_REGISTERED_WITH_DIFFERENT_PASSWORD\033[0m'
        server.sendto(response.encode(), client_address)
        return

    existing_images = available_images.get(client_address, [])

    existing_hashes = {img['md5'] for img in existing_images}

    splitted_images = client_images.split(';')
    new_images = []

    for images_info in splitted_images:
        try:
            image_md5, image_name = images_info.split(',')
            if image_md5 not in existing_hashes:
                new_images.append({'md5': image_md5, 'name': image_name})
            else:
                print(f"Imagem {image_name} já está registrada no servidor.")
        except ValueError:
            response = '\033[31mERR INVALID_MESSAGE_FORMAT\033[0m'
            server.sendto(response.encode(), client_address)
            return

    if new_images:
        existing_images.extend(new_images)
        available_images[client_address] = existing_images

        num_new_images = len(new_images)
        response = f'\033[32mOK {num_new_images}_REGISTERED_FILES\033[0m'
    else:
        response = '\033[33mVocê não tem novas imagens para adicionar.\033[0m'

    for client, info in online_clients.items():
        print(f"Client: {client}, TCP Port: {info['port']}, PASS: {info['password']}")

    server.sendto(response.encode(), client_address)
    server.sendto(b"END", client_address)


def handle_list(client_address, server):
    """
    A função envia uma lista das imagens disponíveis para transferência para o cliente que fez a requisição. 
    Percorre todas as imagens disponíveis associadas aos endereços IP dos clientes e monta uma lista de respostas no formato `MD5,NOME,IP:PORTA`. 
    Se uma imagem já estiver na lista de resposta, adiciona o cliente associado à imagem existente. Por fim, concatena todas as entradas em uma única string,
    envia a mensagem ao cliente.
    """
    try:
        if not available_images:
            server.sendto("No images available.".encode(), client_address)
            return

        response_list = []

        for addr, images in available_images.items():
            tcp_port = online_clients.get(addr, {}).get('port', 'Unknown')
            client_info = f"{addr[0]}:{tcp_port}"

            for image_info in images:
                md5 = image_info['md5']
                name = image_info['name']

                existing_entry = next((entry for entry in response_list if entry.startswith(f"{md5},{name}")), None)

                if existing_entry:
                    updated_entry = f"{existing_entry},{client_info}"
                    response_list[response_list.index(existing_entry)] = updated_entry
                else:
                    response_list.append(f"{md5},{name},{client_info}")

        response_message = ";".join(response_list)

        server.sendto(response_message.encode(), client_address)
        server.sendto("END".encode(), client_address)

    except Exception as e:
        print(f"Erro ao enviar a lista de imagens: {e}")


def handle_end(message, client_address, server):
    """
    A função trata a finalização da conexão de um cliente com o servidor. Autentica o cliente comparando a senha fornecida 
    com a senha armazenada para o endereço IP do cliente. Se a senha não corresponder, retorna um erro de autenticação. Se a autenticação 
    for bem-sucedida, remove o cliente das listas `online_clients` e `available_images`, indicando que o cliente foi desconectado e suas 
    imagens não estão mais disponíveis.
    """
    values = message.split(" ")
    if len(values) < 3: 
        response = '\033[31mERR INVALID_MESSAGE_FORMAT\033[0m'
        server.sendto(response.encode(), client_address)
        return 

    client_password = values[1]
    client_port = values[2]

    hashed_pass = hashlib.sha256(client_password.encode()).hexdigest()
    stored_pass = online_clients.get(client_address, {}).get('password')

    if hashed_pass != stored_pass:
        response = '\033[31mERR IP_REGISTERED_WITH_DIFFERENT_PASSWORD\033[0m'
        server.sendto(response.encode(), client_address)
    else:
        online_clients.pop(client_address, None)
        available_images.pop(client_address, None)

        response = '\033[32mOK CLIENT_FINISHED\033[0m'
        server.sendto(response.encode(), client_address)
        server.sendto("END".encode(), client_address)
        print(f"Client {client_address} has disconnected.")
        

def handle_command(server, message, client_address):
    print(f"Received message from {client_address}: {message}")
    command = message.split(' ')

    if command[0] == 'REG':
        handle_register(message, client_address, server)
    elif command[0] == 'UPD':
        handle_update(message, client_address, server)
    elif command[0] == 'LST':
        handle_list(client_address, server)
    elif command[0] == 'END':
        handle_end(message, client_address, server)
        response = 'END'
    else:
        response = '\033[31mERR INVALID_MESSAGE_FORMAT\033[0m'
        server.sendto(response.encode(), client_address)
        

def main():
    server_port = 13377
    server = socket(AF_INET, SOCK_DGRAM)
    server.bind(('0.0.0.0', server_port))
    local_ip = gethostbyname(getfqdn())

    print(f"Server IP {local_ip} is listening on port {server_port}...")

    while True:
        message, client_address = server.recvfrom(2048)
        thread = threading.Thread(target=handle_command, args=(server, message.decode(), client_address))
        thread.start()


if __name__ == '__main__':
    main()