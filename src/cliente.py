from socket import *


"""UDP connection with Server"""
server = 'localhost'
server_port = 13377
udp_client = socket(AF_INET, SOCK_DGRAM)

message = input("Message: ").encode()
udp_client.sendto(message, (server, server_port))

try:
    response, server_address = udp_client.recvfrom(2048)
    print("Response:", response.decode())
except ConnectionResetError as e:
    print("Connection was reset by the server:", e)

udp_client.close()