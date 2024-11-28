from socket import *
import time
import os
import argparse
import sys

# Making client able to write arguments when initializing the application
def parse_arguments():
    parser = argparse.ArgumentParser(description="Cliente UDP para comunicação com o servidor.")
    
    parser.add_argument("ip", type=str, help="Endereço IP do servidor")
    parser.add_argument("diretorio", type=str, help="Caminho do diretório de imagens")

    args = parser.parse_args()
    
    return args.ip, args.diretorio

# Styling terminal after initializing function
def initializing():
    os.system('cls')
    print("\033[33mInicializing\033[0m", end='')
    
    for _ in range(3):
        print("\033[33m.\033[0m", end='', flush=True)
        time.sleep(1)
    
    os.system('cls')

# Finding an available port on client's system
def find_available_port():
    temp_socket = socket(AF_INET, SOCK_STREAM)
    temp_socket.bind(('', 0))
    available_port = temp_socket.getsockname()[1]
    temp_socket.close()

    return available_port


"""UDP connection with Server"""
def udp_server(server_ip, directory):
    server = server_ip
    server_port = 13377
    udp_client = socket(AF_INET, SOCK_DGRAM)

    while True:
        message = input("\033[33mMessage: \033[0m")
        udp_client.sendto(message.encode(), (server, server_port))

        while True:
            try:
                response, server_address = udp_client.recvfrom(2048)
                response_text = response.decode()

                if response_text == "END":
                    break
                elif "ERR" in response_text or "No images available" in response_text:
                    print(f"\033[31m{response_text}\033[0m")
                    break
                elif "OK CLIENT_FINISHED" in response_text:
                    print("\033[36mResponse:\033[0m", response_text)
                    print("\033[33mShutting down...\033[0m")
                    udp_client.close()
                    sys.exit()

                print("\033[36mResponse:\033[0m", response_text)

            except ConnectionResetError as e:
                print("Connection was reset by the server:", e)
                break



"""TCP connection with Peer"""
#def tcp_peer():


def main():
    server_ip, directory = parse_arguments()
    initializing()
    print("\033[34mBefore connecting to the server, take note of your available port:\033[0m", end='')
    print(f"\033[32m {find_available_port()}\033[0m")
    udp_server(server_ip, directory)


if __name__ == '__main__':
    main()