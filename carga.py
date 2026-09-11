import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 5000
N_CLIENTES = 50
MENSAGENS_POR_CLIENTE = 5

tempo_total_clientes = 0
lock_tempo = threading.Lock()

def cliente_worker(id_cliente):
    global tempo_total_clientes
    inicio = time.perf_counter()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        for j in range(MENSAGENS_POR_CLIENTE):
            s.sendall(f"cli {id_cliente} msg {j}".encode())
            _ = s.recv(1024)
        s.close()
        duracao = (time.perf_counter() - inicio) * 1000
        with lock_tempo:
            tempo_total_clientes += duracao
    except Exception as e:
        print(f"Erro no cliente {id_cliente}: {e}")

if __name__ == "__main__":
    inicio_geral = time.perf_counter()
    threads = []
    
    for i in range(N_CLIENTES):
        t = threading.Thread(target=cliente_worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    fim_geral = time.perf_counter()
    tempo_total = (fim_geral - inicio_geral) * 1000
    tempo_medio = tempo_total_clientes / N_CLIENTES if N_CLIENTES > 0 else 0
    
    print(f"--- Resultado do Teste de Carga ({N_CLIENTES} clientes) ---")
    print(f"Tempo total de execucao: {tempo_total:.2f} ms")
    print(f"Tempo medio por cliente: {tempo_medio:.2f} ms")
