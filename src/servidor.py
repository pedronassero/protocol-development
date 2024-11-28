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
    else:
        client_password = values[1]
        client_port = values[2]
        client_images = values[3]

    hashed_pass = hashlib.sha256(client_password.encode()).hexdigest()
    stored_pass = online_clients.get(client_address, {}).get('password')

    if hashed_pass != stored_pass:
        response = '\033[31mERR IP_REGISTERED_WITH_DIFFERENT_PASSWORD\033[0m'
        server.sendto(response.encode(), client_address)
    else:
        """
        Após verificar a senha, o código recupera as imagens existentes do cliente usando available_images.get(client_address, [])
        e processa as novas imagens enviadas. As novas imagens são extraídas da string, validadas e armazenadas em new_images. 
        Em seguida, as novas imagens são adicionadas às imagens existentes com existing_images.extend(new_images). 
        O dicionário available_images é então atualizado para refletir a lista combinada de imagens.
        """
        existing_images = available_images.get(client_address, [])

        splitted_images = client_images.split(';')
        new_images = []

        for images_info in splitted_images:
            try:
                image_md5, image_name = images_info.split(',')
                new_images.append({'md5': image_md5, 'name': image_name})
            except ValueError:
                response = '\033[31mERR INVALID_MESSAGE_FORMAT\033[0m'
                server.sendto(response.encode(), client_address)
                return

        existing_images.extend(new_images)

        available_images[client_address] = existing_images

        num_images = len(existing_images)
        response = f'\033[32mOK {num_images}_REGISTERED_FILES\033[0m'

        for client, info in online_clients.items():
            print(f"Client: {client}, TCP Port: {info['port']}, PASS: {info['password']}")

        server.sendto(response.encode(), client_address)
        server.sendto("END".encode(), client_address)

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
    else:
        client_password = values[1]
        client_port = values[2]

    hashed_pass = hashlib.sha256(client_password.encode()).hexdigest()
    stored_pass = online_clients.get(client_address, {}).get('password')

    if hashed_pass != stored_pass:
        response = '\033[31mERR IP_REGISTERED_WITH_DIFFERENT_PASSWORD\033[0m'
        server.sendto(response.encode(), client_address)
    else:
        del online_clients[client_address]
        del available_images[client_address]

        response = '\033[32mOK CLIENT_FINISHED\033[0m'
        server.sendto(response.encode(), client_address)
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
    server.bind(('', server_port))
    print(f'Server is listening on port {server_port}...')

    while True:
        message, client_address = server.recvfrom(2048)
        thread = threading.Thread(target=handle_command, args=(server, message.decode(), client_address))
        thread.start()


if __name__ == '__main__':
    main()
