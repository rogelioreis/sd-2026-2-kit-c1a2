import concurrent.futures
import logging
import time
import grpc

import inferencia_pb2
import inferencia_pb2_grpc
from app import modelo

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class InferenciaServicer(inferencia_pb2_grpc.InferenciaServiceServicer):
    def __init__(self):
        self.modelo_instancia = modelo.carregar_modelo()

    def Prever(self, request, context):
        inicio = time.perf_counter()
        res = self.modelo_instancia.prever(request.texto)
        tempo_ms = (time.perf_counter() - inicio) * 1000
        logging.info(f"[gRPC Prever] tamanho={len(request.texto)} chars | tempo={tempo_ms:.2f}ms")
        
        return inferencia_pb2.RespostaInferencia(
            sentimento=res.get("sentimento", "neutro"),
            confianca=float(res.get("confianca", 0.0))
        )

    def PreverLote(self, request, context):
        inicio = time.perf_counter()
        respostas = []
        for texto in request.textos:
            res = self.modelo_instancia.prever(texto)
            respostas.append(
                inferencia_pb2.RespostaInferencia(
                    sentimento=res.get("sentimento", "neutro"),
                    confianca=float(res.get("confianca", 0.0))
                )
            )
        tempo_ms = (time.perf_counter() - inicio) * 1000
        logging.info(f"[gRPC PreverLote] total_itens={len(request.textos)} | tempo={tempo_ms:.2f}ms")
        
        return inferencia_pb2.RespostaLote(resultados=respostas)

def servir():
    servidor = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    inferencia_pb2_grpc.add_InferenciaServiceServicer_to_server(InferenciaServicer(), servidor)
    servidor.add_insecure_port("[::]:50051")
    servidor.start()
    logging.info("[gRPC] Servidor escutando na porta 50051...")
    servidor.wait_for_termination()

if __name__ == "__main__":
    servir()
