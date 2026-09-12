import json
import logging
import time
from app import fila, modelo

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MAX_RETENTATIVAS = 3
FILA_DLQ = "tarefas_dlq"

def reenfileirar_tarefa(tarefa: dict):
    cliente = fila.cliente()
    cliente.rpush(fila.FILA_TAREFAS, json.dumps(tarefa))

def enviar_dead_letter(tarefa: dict, erro: str):
    cliente = fila.cliente()
    tarefa["erro"] = erro
    cliente.rpush(FILA_DLQ, json.dumps(tarefa))

def processar_tarefas():
    logging.info("[Worker] Carregando modelo de sentimento...")
    modelo_instancia = modelo.carregar_modelo()
    logging.info("[Worker] Aguardando tarefas na fila Redis...")
    
    while True:
        tarefa = fila.proxima_tarefa(timeout=5)
        if not tarefa:
            continue
            
        job_id = tarefa.get("id")
        texto = tarefa.get("texto")
        tentativas = tarefa.get("tentativas", 0)
        
        inicio = time.perf_counter()
        
        try:
            logging.info(f"[Worker] Processando job_id={job_id} (tentativa {tentativas + 1}/{MAX_RETENTATIVAS})")
            res = modelo_instancia.prever(texto)
            
            res_com_status = dict(res)
            res_com_status["status"] = "pronto"
                
            fila.guardar_resultado(job_id, res_com_status)
            
            tempo_ms = (time.perf_counter() - inicio) * 1000
            logging.info(f"[Worker] Concluído job_id={job_id} | tempo={tempo_ms:.2f}ms")
            
        except Exception as err:
            tentativas += 1
            tempo_ms = (time.perf_counter() - inicio) * 1000
            logging.error(f"[Worker] Erro no job_id={job_id}: {err} | tempo={tempo_ms:.2f}ms")
            
            if tentativas < MAX_RETENTATIVAS:
                tarefa["tentativas"] = tentativas
                reenfileirar_tarefa(tarefa)
                logging.warning(f"[Worker] Reenfileirado job_id={job_id} para nova tentativa.")
            else:
                enviar_dead_letter(tarefa, str(err))
                logging.error(f"[Worker] job_id={job_id} atingiu limite de tentativas e foi enviado para a Dead-Letter Queue (DLQ).")

if __name__ == "__main__":
    processar_tarefas()
