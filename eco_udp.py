import socket
HOST, PORT = "127.0.0.1", 5001
def rodar_servidor():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    print(f"[servidor udp] ouvindo em {HOST}:{PORT}")
    while True:
        dado, endereco = s.recvfrom(1024)
        if not dado or dado.decode().strip() == "sair":
            break
        s.sendto(dado, endereco)
    s.close()
if __name__ == "__main__":
    rodar_servidor()
