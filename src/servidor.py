from socket import *
import threading
import hashlib

online_clients = {}
available_images = {}

def handle_register(message, client_address, server):
    """
    Recieves a PASSWORD chosen by the client,
    a PORT NUMBER chosen for TCP connections,
    a list of IMAGES so the client can share them
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

    for images_info in splitted_images:
        try:
            md5_hash, name = images_info.split(',')
            images.append((md5_hash, name))
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
    """
    This function gets all the information from the client
    then it saves client information in 'online_clients{}'
    and saves client images in 'shared_images{}'
    """
    server.sendto(response.encode(), client_address)


def handle_command(server, message, client_address):
    print(f"Received message from {client_address}: {message}")
    command = message.split(' ')

    if command[0] == 'REG':
        handle_register(message, client_address, server)
    elif command[0] == 'UPD':
        #handle_update()
        response = 'UPD'
    elif command[0] == 'LST':
        #handle_list()
        response = 'LST'
    elif command[0] == 'END':
        #handle_end()
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
