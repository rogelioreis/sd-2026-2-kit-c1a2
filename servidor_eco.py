import socket

HOST, PORT = "127.0.0.1", 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen()
print(f"[servidor] ouvindo em {HOST}:{PORT}", flush=True)

conexao, endereco = s.accept()
print(f"[servidor] cliente conectado: {endereco}", flush=True)

while True:
    dado = conexao.recv(1024)
    if not dado:
        break
    print(f"[servidor] recebi: {dado.decode()}", flush=True)
    conexao.sendall(dado)

conexao.close()
s.close()