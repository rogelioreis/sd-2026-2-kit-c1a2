import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

def atender(conexao, endereco):
    print(f"[servidor] {endereco} conectou", flush=True)
    while True:
        dado = conexao.recv(1024)
        if not dado:
            break
        conexao.sendall(dado)
    conexao.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen()
print(f"[servidor] ouvindo em {HOST}:{PORT}", flush=True)

while True:
    conexao, endereco = s.accept()
    threading.Thread(target=atender, args=(conexao, endereco), daemon=True).start()
