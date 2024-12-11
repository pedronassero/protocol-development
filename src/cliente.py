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
    """
    Exibe uma animação de "Inicializando..." no terminal.
    """
    print("\033[33mIniciando\033[0m", end='')
    
    for _ in range(3):
        print("\033[33m.\033[0m", end='', flush=True)
        time.sleep(1)
    print('')
    

def parse_arguments():
    """
    Analisa os argumentos passados ao script, como IP do servidor e diretório de imagens.
    """
    parser = argparse.ArgumentParser(description="Cliente UDP para comunicação com o servidor.")
    
    parser.add_argument("ip", type=str, help="Endereço IP do servidor")
    parser.add_argument("diretorio", type=str, help="Caminho do diretório de imagens")

    args = parser.parse_args()
    
    return args.ip, args.diretorio

def gerar_senha_aleatoria(tamanho=12):
    """
    Gera uma senha aleatória com letras e números, com o tamanho especificado (padrão: 12).
    """
    caracteres = string.ascii_letters + string.digits
    senha = ''.join(random.choice(caracteres) for i in range(tamanho))
    return senha

def md5_calculator(file):
    """
    Calcula o hash MD5 de um arquivo fornecido e o retorna.
    """
    md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()

def list_directory_images(directory):
    """
    Lista todas as imagens válidas no diretório especificado, retornando hash MD5 e nome do arquivo.
    """
    imagens = []
    for file in os.listdir(directory):
        path = os.path.join(directory, file) 
        if os.path.isfile(path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                hash_md5 = md5_calculator(path)
                imagens.append(f"{hash_md5},{file}")
    return ";".join(imagens)

def configurar_ambiente():
    """
    Configura o ambiente inicial: gera uma senha aleatória, lista as imagens no diretório e as exibe no terminal.
    """
    global diretorio, imagens, senha

    senha = gerar_senha_aleatoria()
    print("\033[33mGerando senha aleatória...\033[0m")
    time.sleep(2)  

    print(f"\033[32mSua sugestão de senha gerada é: {senha}\033[0m")
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
    """
    Encontra e retorna uma porta TCP disponível para uso.
    """
    print("\033[33mProcurando porta disponível...\033[0m")
    time.sleep(2)  
    
    temp_socket = socket(AF_INET, SOCK_STREAM)
    temp_socket.bind(('', 0))
    available_port = temp_socket.getsockname()[1]
    temp_socket.close()

    print(f"\033[32mUtilizando porta {available_port} que estava disponível.\033[0m")
    return available_port

def registro_no_servidor(senha, porta, imagens):
  """
  Cria uma mensagem do tipo REG para registrar o cliente no servidor com senha, porta e lista de imagens.
  """
  req = f"REG {senha} {porta} {imagens}"
  return req

def atualizar_registro(senha, porta, imagens):
  """
  Cria uma mensagem do tipo UPD para atualizar o cliente no servidor com senha, porta e lista de imagens.
  """
  req = f"UPD {senha} {porta} {imagens}"
  return req

def listar_imagens():
  """
  Cria uma mensagem do tipo LST para listar as imagens disponíveis no servidor.
  """
  req = "LST"
  return req

def remover_registro(senha, porta):
  """
  Cria uma mensagem do tipo END para remover o registro do cliente no servidor.
  """
  req = f"END {senha} {porta}"
  return req

def baixar_imagem(hash):
  """
  Cria uma mensagem do tipo GET para para baixar uma imagem de um cliente usando o hash.
  """
  req = f"GET {hash}"
  return req

def baixar_imagem_tcp(hash_imagem, ip_cliente, porta_cliente):
    """
    Conecta a um cliente via TCP, solicita uma imagem usando o hash e salva a imagem recebida no diretório local.
    """
    global diretorio

    try:
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        tcp_socket.connect((ip_cliente, porta_cliente)) 
        print(f"\033[34mConectado ao cliente {ip_cliente}:{porta_cliente}\033[0m")

        mensagem = f"GET {hash_imagem}"
        tcp_socket.sendall(mensagem.encode())
        print(f"\033[34mSolicitação enviada...\033[0m")

        caminho_imagem = os.path.join(diretorio, f"baixado_{hash_imagem}.jpg")

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


def controle_udp():
    """
    Inicializa um socket UDP para comunicação com o servidor.
    """
    try:
        udp_client = socket(AF_INET, SOCK_DGRAM)
        return udp_client
    except Exception as e:
        print(f"\033[31mErro ao inicializar a conexão UDP: {e}\033[0m")
        sys.exit(1)


def enviar_receber_udp(udp_client, mensagem):
    """
    Envia uma mensagem ao servidor via UDP e processa a resposta.
    Para requisições 'LST', exibe as imagens disponíveis e retorna os detalhes em uma lista.
    """
    global ip
    server_port = 13377

    try:
        udp_client.sendto(mensagem.encode(), (ip, server_port))

        imagens_disponiveis = []

        while True:
            response, server_address = udp_client.recvfrom(2048)
            response_text = response.decode()

            if response_text == "END":
                break
            elif "ERR" in response_text or "No images available" in response_text:
                print(f"\033[31m{response_text}\033[0m")
                break
            else:
                if mensagem == "LST":
                    if response_text.strip():
                        imagens = response_text.split(";") 
                        print("\n\033[33m--- Lista de Imagens ---\033[0m")
                        for idx, imagem in enumerate(imagens, start=1):
                            if imagem.strip():
                                md5, nome, *ips_portas = imagem.split(",")
                                ips_portas_str = ", ".join(ips_portas)
                                print(f"{idx} - {nome} - {md5} - [{ips_portas_str}]")

                                imagens_disponiveis.append({
                                    "index": idx,
                                    "md5": md5,
                                    "nome": nome,
                                    "ips_portas": ips_portas
                                })
                else:
                  print("\033[36mResponse:\033[0m", response_text)
        return imagens_disponiveis
    except ConnectionResetError as e:
        print("Connection was reset by the server:", e)


def servico_tcp(client):
    """
    Trata solicitações recebidas de um cliente via TCP.
    Verifica se o cliente solicita uma imagem usando o hash correto e envia a imagem correspondente, 
    caso exista no diretório local. Retorna erro caso o formato ou o hash sejam inválidos.
    """
    global imagens, diretorio

    try:
        data = client.recv(1024).decode().strip()

        if not data.startswith("GET "):
            client.send(b"ERR INVALID_REQUEST_FORMAT\n")
            print("\033[31mFormato inválido de solicitação recebido.\033[0m")
            client.close()
            return

        hash_solicitado = data.split(" ")[1]
        imagem_encontrada = None

        for imagem in imagens.split(";"):
            if "," in imagem:
                hash_atual, nome_imagem = imagem.split(",")
                if hash_solicitado == hash_atual:
                    imagem_encontrada = nome_imagem
                    break

        if imagem_encontrada:
            caminho_imagem = os.path.join(diretorio, imagem_encontrada)

            with open(caminho_imagem, "rb") as f:
                while (chunk := f.read(1024)):
                    client.send(chunk)
        else:
            client.send(b"ERR IMAGE_NOT_FOUND\n")

    except Exception as e:
        print(f"\033[31mErro ao processar a solicitação TCP: {e}\033[0m")
    finally:
        client.close()


def controle_tcp():
    """
    Inicializa um servidor TCP que escuta conexões dos clientes e delega o processamento
    de cada conexão à função `servico_tcp`, criando uma nova thread para cada cliente.
    """
    global porta_tcp
    try:
        _socket = socket(AF_INET, SOCK_STREAM)
        _socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        _socket.bind(('', porta_tcp))
        _socket.listen(4096)
        while True:
            client, addr = _socket.accept()
            start_new_thread(servico_tcp, (client,))
    except Exception as e:
        print(f"Erro no controle TCP: {e}")


def inicia_controle_tcp():
    """
    Função de inicialização que chama o controle do servidor TCP.
    """
    controle_tcp()


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
        imagens = list_directory_images(diretorio)

        if opcao == "1": 
            senha = input("\033[36mDigite sua senha: \033[0m")
            senha_escolhida = senha
            mensagem = registro_no_servidor(senha, porta_tcp, imagens)

        elif opcao == "2": 
            mensagem = listar_imagens()

        elif opcao == "3":
            imagens_disponiveis = enviar_receber_udp(udp_client, listar_imagens())

            if not imagens_disponiveis:
                print("\033[31mNenhuma imagem disponível para baixar.\033[0m")
                continue

            try:
                num_imagem = int(input("\033[36mDigite o número da imagem para baixar: \033[0m"))
            except ValueError:
                print("\033[31mEntrada inválida. Digite um número válido.\033[0m")
                continue

            imagem_selecionada = next((img for img in imagens_disponiveis if img["index"] == num_imagem), None)
            if not imagem_selecionada:
                print("\033[31mNúmero inválido. Tente novamente.\033[0m")
                continue

            hash_imagem = imagem_selecionada["md5"]
            ip_porta = imagem_selecionada["ips_portas"][0]  
            ip_cliente, porta_cliente = ip_porta.split(":")
            porta_cliente = int(porta_cliente)

            baixar_imagem_tcp(hash_imagem, ip_cliente, porta_cliente)

        elif opcao == "4":  
            senha = input("\033[36mDigite sua senha: \033[0m")
            mensagem = atualizar_registro(senha, porta_tcp, imagens)

        elif opcao == "5":  
            senha = input("\033[36mDigite sua senha: \033[0m")
            mensagem = remover_registro(senha, porta_tcp)

        elif opcao == "6":  
            if senha_escolhida:
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

    # Parseia os argumentos fornecidos ao script (IP do servidor e diretório de imagens).
    server_ip, directory = parse_arguments()

    inicializacao()

    ip = server_ip
    diretorio = directory
    porta_tcp = descobre_porta_disponivel()

    configurar_ambiente()

    # Inicializa um socket UDP para comunicação com o servidor e armazena no udp_client.
    udp_client = controle_udp()

    # Inicia o servidor TCP em uma thread separada para lidar com conexões TCP.
    start_new_thread(inicia_controle_tcp, ())

    # Chama o menu para a interaçao com o usuario
    menu_interativo(udp_client)


if __name__ == '__main__':
    main()