import threading
import time

total = 0
lock = threading.Lock()

def soma_sem_lock():
    global total
    for _ in range(2000):
        atual = total
        time.sleep(0)  # Força a troca de contexto entre threads
        total = atual + 1

def soma_com_lock():
    global total
    for _ in range(2000):
        with lock:
            atual = total
            time.sleep(0)
            total = atual + 1

print("--- Executando SEM lock ---")
total = 0
ts = [threading.Thread(target=soma_sem_lock) for _ in range(2)]
for t in ts: t.start()
for t in ts: t.join()
print(f"Total sem lock (esperado 4000): {total}")

print("\n--- Executando COM lock ---")
total = 0
ts = [threading.Thread(target=soma_com_lock) for _ in range(2)]
for t in ts: t.start()
for t in ts: t.join()
print(f"Total com lock (esperado 4000): {total}")
