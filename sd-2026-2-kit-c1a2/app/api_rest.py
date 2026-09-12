import logging
import time
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from app import fila, modelo

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(title="Serviço de Inferência de Sentimento")

# Carrega o modelo de IA uma única vez na inicialização
modelo_instancia = modelo.carregar_modelo()

class PredictRequest(BaseModel):
    texto: str

@app.post("/predict-sync")
def predict_sincrono(req: PredictRequest):
    inicio = time.perf_counter()
    res = modelo_instancia.prever(req.texto)
    tempo_ms = (time.perf_counter() - inicio) * 1000
    logging.info(f"[REST Sync] tamanho={len(req.texto)} chars | tempo={tempo_ms:.2f}ms")
    return res

@app.post("/predict", status_code=status.HTTP_202_ACCEPTED)
def predict_assincrono(req: PredictRequest):
    inicio = time.perf_counter()
    job_id = fila.enfileirar(req.texto)
    tempo_ms = (time.perf_counter() - inicio) * 1000
    logging.info(f"[REST Async POST] id={job_id} | tamanho={len(req.texto)} chars | tempo={tempo_ms:.2f}ms")
    return {"id": job_id, "status": "enfileirado"}

@app.get("/resultado/{job_id}")
def obter_resultado(job_id: str):
    inicio = time.perf_counter()
    resultado = fila.buscar_resultado(job_id)
    tempo_ms = (time.perf_counter() - inicio) * 1000
    if resultado is None:
        logging.info(f"[REST Async GET] id={job_id} | status=NAO_ENCONTRADO | tempo={tempo_ms:.2f}ms")
        raise HTTPException(status_code=404, detail="Resultado não encontrado ou ainda em processamento")
    
    logging.info(f"[REST Async GET] id={job_id} | status=SUCESSO | tempo={tempo_ms:.2f}ms")
    return resultado
