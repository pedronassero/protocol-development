# Projeto de Redes P2P com Protocolo IDP2PI

## Descrição do Projeto

Este projeto implementa um protocolo simplificado de compartilhamento de imagens chamado **IDP2PI**. Ele permite que clientes se registrem em um servidor central, compartilhem imagens com outros clientes e realizem operações como atualização, listagem e download de imagens em uma rede P2P.

## Estrutura do Projeto

- **`servidor.py`**: Script que implementa o servidor, responsável por gerenciar os clientes e imagens compartilhadas.
- **`cliente.py`**: Script que implementa o cliente, permitindo o registro, atualização de imagens, listagem das imagens disponíveis e download das mesmas.
- **Diretório de imagens**: Pasta onde ficam armazenadas as imagens compartilhadas pelos clientes.

## Funcionalidades

### Servidor

O servidor responde aos seguintes comandos via protocolo **UDP** na porta **13377**:

1. **REG (Registro)**  
   Registra um novo cliente.  
   Formato: `REG <SENHA> <PORTA> <IMAGENS>`  
   Resposta: `OK <N>_REGISTERED_IMAGES`

2. **UPD (Atualização)**  
   Atualiza a lista de imagens de um cliente registrado.  
   Formato: `UPD <SENHA> <PORTA> <IMAGENS>`  
   Resposta: `OK <N>_REGISTERED_FILES` ou `ERR IP_REGISTERED_WITH_DIFFERENT_PASSWORD`

3. **LST (Listagem)**  
   Lista todas as imagens compartilhadas na rede.  
   Formato: `LST`  
   Resposta: Lista de imagens disponíveis e seus respectivos clientes.

4. **END (Desconexão)**  
   Desconecta um cliente da rede.  
   Formato: `END <SENHA> <PORTA>`  
   Resposta: `OK CLIENT_FINISHED` ou `ERR IP_REGISTERED_WITH_DIFFERENT_PASSWORD`

### Cliente

O cliente executa as seguintes operações:

- **Registro no servidor**
- **Atualização de imagens**
- **Listagem de imagens compartilhadas**
- **Download de imagens** via protocolo **TCP**
- **Desconexão da rede**

## Como Executar

### 1. Executar o Servidor

Abra o terminal e entre na pasta 'src'

```bash
cd src
```

Abra o terminal e execute o servidor com:

```bash
python3 servidor.py
```

O servidor ficará ouvindo na porta **13377** para conexões **UDP**.

### 2. Executar o Cliente

Abra o terminal e entre na pasta 'src'

```bash
cd src
```

No terminal, execute o cliente passando o endereço IP do servidor e o diretório de imagens:

```bash
python3 cliente.py <IP_DO_SERVIDOR> <DIRETORIO_DE_IMAGENS>
```

**Exemplo:**

```bash
python3 cliente.py 192.168.1.10 "../imagens"
```

### 3. Interagir com a Rede

Após iniciar o cliente, você pode enviar os seguintes comandos no terminal do cliente:

1. **Registrar no Servidor**  
   - **Comando:** `1`  
   - Permite registrar o cliente no servidor com senha, porta e lista de imagens.

2. **Listar Imagens**  
   - **Comando:** `2`  
   - Lista todas as imagens disponíveis registradas no servidor e os clientes associados a cada imagem.

3. **Baixar Imagem**  
   - **Comando:** `3`  
   - Baixa uma imagem específica disponível.

4. **Atualizar Registro**  
   - **Comando:** `4`  
   - Atualiza o registro do cliente no servidor com novas imagens que ainda não foram cadastradas.

5. **Remover Registro do Servidor**  
   - **Comando:** `5`  
   - Desconecta o cliente do servidor e remove seus registros e imagens associadas.

6. **Sair**  
   - **Comando:** `6`  
   - Encerra o cliente e finaliza a execução.

## Estrutura de Pastas

```
📦 protocol-development
├── imagens
├── src
   ├── cliente.py
   ├── servidor.py
```