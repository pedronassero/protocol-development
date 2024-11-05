from socket import *
import time
import os


def initializing():
    os.system('cls')
    print("\033[33mInicializing\033[0m", end='')
    
    for _ in range(3):
        print("\033[33m.\033[0m", end='', flush=True)
        time.sleep(1)
    
    os.system('cls')


def find_available_port():
    temp_socket = socket(AF_INET, SOCK_STREAM)
    temp_socket.bind(('', 0))
    available_port = temp_socket.getsockname()[1]
    temp_socket.close()

    return available_port


"""UDP connection with Server"""
def udp_server():
    server = 'localhost'
    server_port = 13377
    udp_client = socket(AF_INET, SOCK_DGRAM)

    message = input("\033[36mMessage: \033[0m").encode()
    udp_client.sendto(message, (server, server_port))

    try:
        response, server_address = udp_client.recvfrom(2048)
        print("\033[36mResponse:\033[0m", response.decode())
    except ConnectionResetError as e:
        print("Connection was reset by the server:", e)

    udp_client.close()


def main():
    initializing()
    print("\033[34mBefore connecting to the server, take note of your available port:\033[0m", end='')
    print(f"\033[32m {find_available_port()}\033[0m")
    udp_server()


"""TCP connection with Peer"""


if __name__ == '__main__':
    main()