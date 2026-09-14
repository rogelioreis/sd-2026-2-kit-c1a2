import sys
import os

# Adiciona o diretório raiz ao path para importar inferencia_pb2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import grpc
import inferencia_pb2
import inferencia_pb2_grpc

def executar():
    texto = sys.argv[1] if len(sys.argv) > 1 else "O atendimento foi excelente"
    
    canal = grpc.insecure_channel("localhost:50051")
    stub = inferencia_pb2_grpc.InferenciaServiceStub(canal)
    
    print("--- Testando gRPC (Prever) ---")
    req = inferencia_pb2.RequisicaoInferencia(texto=texto)
    res = stub.Prever(req)
    print(f"Texto: '{texto}'")
    print(f"Resultado: sentimento={res.sentimento}, confianca={res.confianca:.4f}\n")
    
    print("--- Testando gRPC (PreverLote) ---")
    textos_lote = [texto, "produto horrivel e quebrado", "entrega dentro do prazo"]
    req_lote = inferencia_pb2.RequisicaoLote(textos=textos_lote)
    res_lote = stub.PreverLote(req_lote)
    
    for t, r in zip(textos_lote, res_lote.resultados):
        print(f"-> '{t}' => sentimento={r.sentimento}, confianca={r.confianca:.4f}")

if __name__ == "__main__":
    executar()
