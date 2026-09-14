import json
import logging
import time
import redis
from app.modelo import carregar_modelo

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Worker] %(message)s")
logger = logging.getLogger(__name__)

def iniciar_worker():
    r = redis.Redis(host='localhost', port=6379, db=0)
    logger.info("Carregando modelo de sentimento...")
    modelo = carregar_modelo()
    logger.info("Aguardando tarefas na fila Redis...")

    while True:
        item = r.blpop("tarefas", timeout=0)
        if not item:
            continue

        _, conteudo_raw = item
        inicio = time.time()
        
        try:
            tarefa = json.loads(conteudo_raw.decode('utf-8'))
        except Exception as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            continue

        job_id = tarefa.get("job_id", "desconhecido")
        tentativas = tarefa.get("tentativas", 0) + 1
        texto = tarefa.get("texto")

        logger.info(f"Processando job_id={job_id} (tentativa {tentativas}/3)")

        try:
            if texto is None:
                raise ValueError("'NoneType' object has no attribute 'lower'")

            # Processamento normal
            resultado = modelo.prever(texto)
            r.set(f"resultado:{job_id}", json.dumps(resultado))
            tempo_ms = (time.time() - inicio) * 1000
            logger.info(f"Concluído job_id={job_id} | tempo={tempo_ms:.2f}ms")

        except Exception as e:
            tempo_ms = (time.time() - inicio) * 1000
            logger.error(f"Erro no job_id={job_id}: {e} | tempo={tempo_ms:.2f}ms")

            tarefa["tentativas"] = tentativas
            tarefa["erro"] = str(e)

            if tentativas < 3:
                logger.warning(f"Reenfileirado job_id={job_id} para nova tentativa.")
                r.rpush("tarefas", json.dumps(tarefa))
            else:
                logger.error(f"job_id={job_id} atingiu limite de tentativas e foi enviado para a Dead-Letter Queue (DLQ).")
                r.rpush("tarefas_dlq", json.dumps(tarefa))

if __name__ == "__main__":
    iniciar_worker()
