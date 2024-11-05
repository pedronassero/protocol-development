from socket import *
import threading

online_clients = {}
shared_images = {}


def handle_command(server, message, client_address):
    print(f"Received message from {client_address}: {message}")
    command = message.split()

    if command[0] == 'REG':
        #handle_register()
        response = 'REG'
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
        response = 'ERR INVALID_MESSAGE_FORMAT'
    
    print(f"Sending response to {client_address}: {response}")
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
