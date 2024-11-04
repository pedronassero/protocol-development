from socket import *
import threading

online_clients = {}
shared_images = {}


def handle_command(message, client_address):
        command = message.split()

        if command[0] == 'REG':
            #handle_register()
            print('REG')
        elif command[0] == 'UPD':
            #handle_update()
            print('UPD')
        elif command[0] == 'LST':
            #handle_list()
            print('LST')
        elif command[0] == 'END':
            #handle_end()
            print('END')
        else:
            message.sendto(b'ERR INVALID_MESSAGE_FORMAT', client_address)
        

def main():
    server_port = 13377
    server = socket(AF_INET, SOCK_DGRAM)
    server.bind(('', server_port))
    print(f'Server is listening on port {server_port}...')

    while True:
        message, client_address = server.recvfrom(2048)
        thread = threading.Thread(target=handle_command, args=(message.decode(), client_address))
        thread.start()



if __name__ == '__main__':
    main()