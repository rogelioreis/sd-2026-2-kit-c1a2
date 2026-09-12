# Sistema de Inferência de Sentimento Distribuído

Este repositório contém a implementação do trabalho prático de Sistemas Distribuídos, oferecendo análise de sentimento via API REST e gRPC, além de processamento assíncrono utilizando filas no Redis.

---

## Arquitetura do Sistema

O sistema é dividido em três partes principais:

1. **API REST (FastAPI):**
   - `POST /predict-sync`: Processa a inferência de forma síncrona.
   - `POST /predict`: Recebe o texto, enfileira a tarefa no Redis e retorna HTTP 202 com o `job_id`.
   - `GET /resultado/{job_id}`: Consulta o estado/resultado do processamento (retorna HTTP 404 caso o ID não exista ou ainda esteja processando).

2. **Worker da Fila (Redis):**
   - Consome as tarefas pendentes na fila `tarefas` do Redis.
   - Processa a inferência chamando o modelo de linguagem local.
   - Conta com lógica de até 3 retentativas em caso de erro; se falhar em todas, move a tarefa para a fila de descarte (`tarefas_dlq`).
   - Salva o resultado final no Redis para consulta rápida.

3. **Servidor gRPC:**
   - Comunicação binária via Protobuf na porta `50051`.
   - `Prever`: Inferência para uma única frase.
   - `PreverLote`: Inferência em lote para múltiplas frases de uma só vez.

---

## Como Executar

### 1. Pré-requisitos e Ambiente Virtual
Garantir que o serviço do Redis está em execução (`redis-server`) e ativar o ambiente virtual do projeto:

```bash
source .venv/bin/activate
