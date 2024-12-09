#!/usr/bin/python
import time
from _thread import *
from socket import *
import time
import os
import argparse
import sys
import hashlib
import string
import random

porta_tcp = None
ip = None
diretorio = None
senha_escolhida = None
imagens = []

def inicializacao():
    os.system('clear')
    print("\033[33mIniciando\033[0m", end='')
    
    for _ in range(3):
        print("\033[33m.\033[0m", end='', flush=True)
        time.sleep(1)
    
    os.system('clear')

def parse_arguments():
    parser = argparse.ArgumentParser(description="Cliente UDP para comunicação com o servidor.")
    
    parser.add_argument("ip", type=str, help="Endereço IP do servidor")
    parser.add_argument("diretorio", type=str, help="Caminho do diretório de imagens")

    args = parser.parse_args()
    
    return args.ip, args.diretorio

def gerar_senha_aleatoria(tamanho=12):
    caracteres = string.ascii_letters + string.digits
    senha = ''.join(random.choice(caracteres) for i in range(tamanho))
    return senha

def md5_calculator(file):
    md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()

def list_directory_images(directory):
    imagens = []
    for file in os.listdir(directory):
        path = os.path.join(directory, file) 
        if os.path.isfile(path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                hash_md5 = md5_calculator(path)
                imagens.append(f"{hash_md5},{file}")
    return ";".join(imagens)

def configurar_ambiente():
    global diretorio, imagens, senha

    senha = gerar_senha_aleatoria()
    print("\033[33mGerando senha aleatória...\033[0m")
    time.sleep(2)  

    print(f"\033[32mSua senha gerada é: {senha}\033[0m")
    time.sleep(1)

    print("\033[33mImagens no diretório:\033[0m")
    time.sleep(2) 
    imagens = list_directory_images(diretorio)
    
    if imagens:
      for imagem in imagens.split(";"):
        if "," in imagem:
          nome_imagem = imagem.split(",")[1]  
          print(f"\033[32m{nome_imagem}\033[0m") 
    else:
        print("\033[31mNo images found in the directory.\033[0m")


def descobre_porta_disponivel():
    print("\033[33mProcurando porta disponível...\033[0m")
    time.sleep(2)  
    
    temp_socket = socket(AF_INET, SOCK_STREAM)
    temp_socket.bind(('', 0))
    available_port = temp_socket.getsockname()[1]
    temp_socket.close()

    print(f"\033[32mUtilizando porta {available_port} que estava disponível.\033[0m")
    return available_port

def registro_no_servidor(senha, porta, imagens):
  req = f"REG {senha} {porta} {imagens}"
  return req

def atualizar_registro(senha, porta, imagens):
  req = f"UPD {senha} {porta} {imagens}"
  return req

def listar_imagens():
  req = "LST"
  return req

def remover_registro(senha, porta):
  req = f"END {senha} {porta}"
  return req

def baixar_imagem(hash):
  req = f"GET {hash}"
  return req

def baixar_imagem_tcp(hash_imagem, ip_cliente, porta_cliente):
    global diretorio

    try:
        # Inicializa o socket TCP
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        tcp_socket.connect((ip_cliente, porta_cliente))  # Conecta ao cliente
        print(f"\033[34mConectado ao cliente {ip_cliente}:{porta_cliente}\033[0m")

        # Envia a mensagem no formato GET <hash>
        mensagem = f"GET {hash_imagem}"
        tcp_socket.sendall(mensagem.encode())
        print(f"\033[34mSolicitação enviada: {mensagem}\033[0m")

        # Caminho para salvar a imagem
        caminho_imagem = os.path.join(diretorio, f"baixado_{hash_imagem}.jpg")

        # Recebe os dados da imagem e os salva
        with open(caminho_imagem, "wb") as f:
            while True:
                dados = tcp_socket.recv(1024)
                if not dados:
                    break
                f.write(dados)

        print(f"\033[32mImagem baixada com sucesso: {caminho_imagem}\033[0m")

    except Exception as e:
        print(f"\033[31mErro ao baixar a imagem: {e}\033[0m")
    finally:
        tcp_socket.close()
        print("\033[33mConexão TCP encerrada.\033[0m")

# def controle_udp(mensagem):
#     global ip
#     server_port = 13377
#     udp_client = socket(AF_INET, SOCK_DGRAM)

#     if mensagem != '':
#       try:
#         udp_client.sendto(mensagem.encode(), (ip, server_port)) 

#         while True:
#             response, server_address = udp_client.recvfrom(2048)
#             response_text = response.decode()

#             if response_text == "END":
#                 break
#             elif "ERR" in response_text or "No images available" in response_text:
#                 print(f"\033[31m{response_text}\033[0m")
#                 break
#             elif "OK CLIENT_FINISHED" in response_text:
#                 print("\033[36mResponse:\033[0m", response_text)
#                 print("\033[33mShutting down...\033[0m")
#                 udp_client.close()
#                 sys.exit()
#             else:
#                 print("\033[36mResponse:\033[0m", response_text)
#       except ConnectionResetError as e:
#           print("Connection was reset by the server:", e)
#       finally:
#           udp_client.close()

def controle_udp():
    try:
        udp_client = socket(AF_INET, SOCK_DGRAM)
        return udp_client
    except Exception as e:
        print(f"\033[31mErro ao inicializar a conexão UDP: {e}\033[0m")
        sys.exit(1)

def enviar_receber_udp(udp_client, mensagem):
    global ip
    server_port = 13377

    try:
      udp_client.sendto(mensagem.encode(), (ip, server_port)) 

      while True:
        response, server_address = udp_client.recvfrom(2048)
        response_text = response.decode()

        if response_text == "END":
          break
        elif "ERR" in response_text or "No images available" in response_text:
          print(f"\033[31m{response_text}\033[0m")
          break
        else:
          print("\033[36mResponse:\033[0m", response_text)
    except ConnectionResetError as e:
      print("Connection was reset by the server:", e)



def servico_tcp(client):
    global imagens, diretorio

    try:
        # Recebe a solicitação do cliente
        data = client.recv(1024).decode().strip()
        print(f"\033[34mMensagem recebida via TCP: {data}\033[0m")

        if not data.startswith("GET "):
            client.send(b"ERR INVALID_REQUEST_FORMAT\n")
            print("\033[31mFormato inválido de solicitação recebido.\033[0m")
            client.close()
            return

        # Extrai o hash da mensagem
        hash_solicitado = data.split(" ")[1]
        imagem_encontrada = None

        # Procura o hash na variável global `imagens`
        for imagem in imagens.split(";"):
            if "," in imagem:
                hash_atual, nome_imagem = imagem.split(",")
                if hash_solicitado == hash_atual:
                    imagem_encontrada = nome_imagem
                    break

        if imagem_encontrada:
            print(f"\033[32mImagem correspondente encontrada: {imagem_encontrada}\033[0m")
            caminho_imagem = os.path.join(diretorio, imagem_encontrada)

            # Envia o conteúdo da imagem para o cliente
            with open(caminho_imagem, "rb") as f:
                while (chunk := f.read(1024)):
                    client.send(chunk)
            print(f"\033[32mImagem {imagem_encontrada} enviada com sucesso.\033[0m")
        else:
            client.send(b"ERR IMAGE_NOT_FOUND\n")
            print("\033[31mHash não encontrado.\033[0m")

    except Exception as e:
        print(f"\033[31mErro ao processar a solicitação TCP: {e}\033[0m")
    finally:
        client.close()
        print("\033[33mConexão TCP encerrada.\033[0m")


def controle_tcp():
    global porta_tcp
    try:
        _socket = socket(AF_INET, SOCK_STREAM)
        _socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        _socket.bind(('', porta_tcp))
        _socket.listen(4096)
        while True:
            client, addr = _socket.accept()
            print(f"Conexão recebida de {addr}")
            start_new_thread(servico_tcp, (client,))
    except Exception as e:
        print(f"Erro no controle TCP: {e}")


def inicia_controle_tcp():
    controle_tcp()


def inicia_controle_udp():
    controle_udp()

def menu_interativo(udp_client):
    global ip, porta_tcp, imagens, senha_escolhida

    while True:
        print("\n\033[33m--- MENU ---\033[0m")
        print("1. Registrar no Servidor")
        print("2. Listar Imagens")
        print("3. Baixar Imagem")
        print("4. Atualizar Registro")
        print("5. Remover Registro do Servidor")
        print("6. Sair")
        opcao = input("\033[36mEscolha uma opção: \033[0m")

        mensagem = None 

        if opcao == "1": 
            senha = input("\033[36mDigite sua senha: \033[0m")
            senha_escolhida = senha
            mensagem = registro_no_servidor(senha, porta_tcp, imagens)

        elif opcao == "2": 
            mensagem = listar_imagens()

        elif opcao == "3": 
            hash_imagem = input("\033[36mDigite o hash da imagem para baixar: \033[0m")
            ip_cliente = input("\033[36mDigite o IP do cliente: \033[0m")
            porta_cliente = int(input("\033[36mDigite a porta TCP do cliente: \033[0m"))
            baixar_imagem_tcp(hash_imagem, ip_cliente, porta_cliente)

        elif opcao == "4":  
            senha = input("\033[36mDigite sua senha: \033[0m")
            imagens = list_directory_images(diretorio)
            mensagem = atualizar_registro(senha, porta_tcp, imagens)

        elif opcao == "5":  
            senha = input("\033[36mDigite sua senha: \033[0m")
            mensagem = remover_registro(senha, porta_tcp)

        elif opcao == "6":  
            enviar_receber_udp(udp_client, remover_registro(senha_escolhida, porta_tcp))
            print("\033[33mEncerrando o cliente...\033[0m")
            udp_client.close()
            sys.exit()

        else:
            print("\033[31mOpção inválida. Tente novamente.\033[0m")
        
        if mensagem:
            enviar_receber_udp(udp_client, mensagem)


def main():
    global porta_tcp, ip, diretorio

    server_ip, directory = parse_arguments()

    inicializacao()
    ip = server_ip
    diretorio = directory
    porta_tcp = descobre_porta_disponivel()

    configurar_ambiente()

    udp_client = controle_udp()
    start_new_thread(inicia_controle_tcp, ())

    menu_interativo(udp_client)


if __name__ == '__main__':
    main()