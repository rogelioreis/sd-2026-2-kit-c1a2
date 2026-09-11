import socket
import time

HOST = "127.0.0.1"
PORT_TCP = 5000
PORT_UDP = 5001
N_MENSAGENS = 100

def medir_tcp():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT_TCP))
        inicio = time.perf_counter()
        for i in range(N_MENSAGENS):
            msg = f"mensagem {i}".encode()
            s.sendall(msg)
            _ = s.recv(1024)
        fim = time.perf_counter()
        s.close()
        return (fim - inicio) * 1000
    except Exception as e:
        print(f"Erro no teste TCP: {e}")
        return 0

def medir_udp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    inicio = time.perf_counter()
    for i in range(N_MENSAGENS):
        msg = f"mensagem {i}".encode()
        s.sendto(msg, (HOST, PORT_UDP))
        _, _ = s.recvfrom(1024)
    fim = time.perf_counter()
    s.close()
    return (fim - inicio) * 1000

if __name__ == "__main__":
    tempo_tcp = medir_tcp()
    tempo_udp = medir_udp()
    print("Resultado (100 mensagens):")
    print(f"TCP: {tempo_tcp:.2f} ms")
    print(f"UDP: {tempo_udp:.2f} ms")
