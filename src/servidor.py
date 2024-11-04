from socket import *
import threading

clients = {}



def main():
    server_port = 13377
    server = socket(AF_INET, SOCK_DGRAM)
    server.bind(('', server_port))
    print('Server is up on port {server_port}...')

    while True:
        message, client_address = server.recvfrom(2048)
        thread = threading.Thread(target=test, args=(server, message.decode(), client_address))
        thread.start()
        
def test(server, message, client_address):
    msg = "Olá"
    server.sendto(msg.encode(), client_address)


if __name__ == '__main__':
    main()