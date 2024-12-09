from socket import *
import threading
import hashlib
import json

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
    try:
        if not available_images:
            server.sendto("No images available.".encode(), client_address)
            return

        for addr, images in available_images.items():
            tcp_port = online_clients.get(addr, {}).get('port', 'Unknown')

            for image_info in images:
                message = f"Client: {addr}, TCP Port: {tcp_port}, MD5: {image_info['md5']}, Name: {image_info['name']}"
                server.sendto(message.encode(), client_address)

        server.sendto("↑ Available images ↑".encode(), client_address)
        server.sendto("END".encode(), client_address)

    except Exception as e:
        print(f"Erro ao enviar a lista de imagens: {e}")


def handle_end(message, client_address, server):
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
