# Sistemas Distribuídos (2026/2) - Avaliação C1.A2
**Sistema de Inferência de Sentimentos Assíncrono e Distribuído (REST & gRPC)**

Este repositório contém a implementação de um sistema desacoplado e distribuído para processamento de inferência de sentimentos em texto. O projeto utiliza **FastAPI** para a interface REST, **gRPC** para comunicação de alta performance, **Redis** como broker de mensageria e armazenamento temporário (Key-Value), e **Workers de inferência** desacoplados.

---

## 🏗️ Arquitetura e Decomposição em Serviços

O sistema foi desenhado para separar a camada de recebimento de requisições da camada de processamento intensivo (inferência), garantindo resiliência e escalabilidade horizontal.

```
                      +-------------------+
                      |   Cliente REST    |
                      +---------+---------+
                                |
                   POST /predict| GET /resultado/{id}
                                v
                      +-------------------+
                      |   API REST        |
                      |  (app/api_rest)   |
                      +----+---------+----+
                           |         ^
             RPUSH tarefas |         | GET resultado:<id>
                           v         |
                      +--------------+----+
                      |    Redis      |
                      |  (Fila & KV)  |
                      +------+------------+
                             |
                BLPOP tarefas| RPUSH tarefas_dlq (falhas)
                             v
                      +-------------------+
                      |      Worker       |
                      |   (app/worker)    |
                      +-------------------+

  +-------------------+               +-------------------+
  |   Cliente gRPC    | --(Prever/--> |   Servidor gRPC   |
  | (exemplos/cliente)|   PreverLote) |(app/servidor_grpc)|
  +-------------------+               +-------------------+
```

### Componentes do Sistema:
1. **API REST (`app/api_rest.py`)**: Fornece rotas síncronas (`/predict-sync`) para testes e assíncronas (`POST /predict` e `GET /resultado/{id}`) baseadas em polling.
2. **Broker / Mensageria (`Redis`)**: Armazena as filas de tarefas (`tarefas`), a fila de mensagens mortas (`tarefas_dlq`) e os resultados de inferência (`resultado:<id>`).
3. **Worker de Inferência (`app/worker.py`)**: Processo em segundo plano que consome jobs do Redis via `BLPOP`, executa o modelo de sentimento offline (`app/modelo.py`) e trata retentativas em caso de erro.
4. **Servidor gRPC (`app/servidor_grpc.py`)**: Serviço de alto desempenho que expõe os métodos unicast `Prever` e em lote `PreverLote`.

---

## 🛠️ Guia de Execução Reproduzível

### 1. Clonar o Repositório e Acessar o Diretório
```bash
git clone https://github.com/howardroatti/sd-2026-2-kit-c1a2.git
cd sd-2026-2-kit-c1a2
```

### 2. Configurar o Ambiente Virtual
```bash
python3 -m venv .venv

# Linux / macOS:
source .venv/bin/activate

# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Subir o Serviço de Fila (Redis)
O Redis é gerenciado via Docker Compose:
```bash
docker compose up -d
```
Para testar a conectividade da fila com o Redis via Python:
```bash
python3 -c "import redis; r = redis.Redis(); print(r.ping())"
# Saída esperada: True
```

### 4. Compilação das Stubs gRPC
Gere os arquivos do Protocol Buffers antes de rodar o servidor gRPC:
```bash
python3 -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/inferencia.proto
```

---

## 🚀 Execução dos Serviços

Abra terminais separados com o ambiente virtual ativado (`source .venv/bin/activate`):

* **Terminal 1 - API REST:**
  ```bash
  uvicorn app.api_rest:app --reload --port 8000
  ```
  *(Documentação interativa em http://localhost:8000/docs)*

* **Terminal 2 - Worker de Processamento:**
  ```bash
  python -m app.worker
  ```

* **Terminal 3 - Servidor gRPC:**
  ```bash
  python -m app.servidor_grpc
  ```

---

## 📋 Evidências de Validação e Testes Práticos

### Tarefa 1 & 2: Submissão Assíncrona e Polling de Resultados (REST)

**1. Submissão do Job (`POST /predict`):**
Retorna imediatamente o status HTTP `202 Accepted` e o ID do trabalho gerado.
```bash
curl -i -X POST "http://127.0.0.1:8000/predict"      -H "Content-Type: application/json"      -d '{"texto": "Teste de validacao do job_id no worker"}'
```
*Saída obtida:*
```http
HTTP/1.1 202 Accepted
date: Mon, 14 Sep 2026 17:34:33 GMT
server: uvicorn
content-length: 68
content-type: application/json

{"id":"6fbfa58e-741b-4ba8-ad07-0c49cca1262a","status":"enfileirado"}
```

**2. Consulta de Resultado (`GET /resultado/{id}`):**
Durante o processamento, a rota retorna `404 Not Found`. Após a conclusão do worker, retorna `200 OK` com o payload estruturado.
```bash
curl -i "http://127.0.0.1:8000/resultado/6fbfa58e-741b-4ba8-ad07-0c49cca1262a"
```
*Saída obtida:*
```http
HTTP/1.1 200 OK
date: Mon, 14 Sep 2026 17:35:43 GMT
server: uvicorn
content-length: 93
content-type: application/json

{"texto":"Teste de validacao do job_id no worker","sentimento":"negativo","confianca":0.5242}
```

---

### Tarefa 4: Comunicação gRPC (`Prever` e `PreverLote`)

Execução do cliente de exemplo para validação das rotas gRPC:
```bash
python3 exemplos/cliente_grpc.py
```
*Saída obtida:*
```text
--- Testando gRPC (Prever) ---
Texto: 'O atendimento foi excelente'
Resultado: sentimento=positivo, confianca=0.5688

--- Testando gRPC (PreverLote) ---
-> 'O atendimento foi excelente' => sentimento=positivo, confianca=0.5688
-> 'produto horrivel e quebrado' => sentimento=positivo, confianca=0.5054
-> 'entrega dentro do prazo' => sentimento=positivo, confianca=0.5417
```

---

### Tarefa 5: Resiliência, Retentativas e Dead-Letter Queue (DLQ)

O Worker foi construído para suportar falhas transitórias. Ao receber uma mensagem malformada (`texto: null`), o worker realiza até **3 tentativas de processamento**. Caso o erro persista, o job é movido para a fila de descarte `tarefas_dlq`.

**Simulação de Falha no Terminal:**
```bash
python3 -c "import redis, json; r = redis.Redis(); r.rpush('tarefas', json.dumps({'job_id': 'teste-dlq-123', 'texto': None}))"
```

**Log Sequencial do Worker (Tentativas e DLQ):**
```text
2026-09-14 14:38:39,569 [INFO] [Worker] Processando job_id=teste-dlq-123 (tentativa 1/3)
2026-09-14 14:38:39,570 [ERROR] [Worker] Erro no job_id=teste-dlq-123: 'NoneType' object has no attribute 'lower' | tempo=0.37ms
2026-09-14 14:38:39,570 [WARNING] [Worker] Reenfileirado job_id=teste-dlq-123 para nova tentativa.
2026-09-14 14:38:40,100 [INFO] [Worker] Processando job_id=teste-dlq-123 (tentativa 2/3)
2026-09-14 14:38:40,101 [ERROR] [Worker] Erro no job_id=teste-dlq-123: 'NoneType' object has no attribute 'lower' | tempo=0.42ms
2026-09-14 14:38:40,102 [WARNING] [Worker] Reenfileirado job_id=teste-dlq-123 para nova tentativa.
2026-09-14 14:38:41,200 [INFO] [Worker] Processando job_id=teste-dlq-123 (tentativa 3/3)
2026-09-14 14:38:41,201 [ERROR] [Worker] Erro no job_id=teste-dlq-123: 'NoneType' object has no attribute 'lower' | tempo=0.22ms
2026-09-14 14:38:41,202 [ERROR] [Worker] job_id=teste-dlq-123 atingiu limite de tentativas e foi enviado para a Dead-Letter Queue (DLQ).
```

**Conferência da DLQ no Redis:**
```bash
python3 -c "import redis; r = redis.Redis(); print(r.lrange('tarefas_dlq', 0, -1))"
```
*Saída:*
```text
[b'{"job_id": "teste-dlq-123", "texto": null, "tentativas": 3, "erro": "'NoneType' object has no attribute 'lower'"}']
```

---

### Tarefa 6: Observabilidade e Métrica de Tempo de Execução

Todos os microsserviços foram instrumentados com registros de log detalhados e medição do tempo de processamento em milissegundos (`ms`).

* **Logs da API REST:**
  ```text
  2026-09-14 14:34:34,008 [INFO] [REST Async POST] id=6fbfa58e-741b-4ba8-ad07-0c49cca1262a | tamanho=41 chars | tempo=12.10ms
  2026-09-14 14:35:45,640 [INFO] [REST Async GET] id=6fbfa58e-741b-4ba8-ad07-0c49cca1262a | status=SUCESSO | tempo=4.75ms
  ```

* **Logs do Worker:**
  ```text
  2026-09-14 14:34:35,389 [INFO] [Worker] Processando job_id=6fbfa58e-741b-4ba8-ad07-0c49cca1262a (tentativa 1/3)
  2026-09-14 14:34:35,393 [INFO] [Worker] Concluído job_id=6fbfa58e-741b-4ba8-ad07-0c49cca1262a | tempo=4.31ms
  ```

* **Logs do Servidor gRPC:**
  ```text
  2026-09-14 14:25:17,417 [INFO] [gRPC Prever] tamanho=27 chars | tempo=4.94ms
  2026-09-14 14:25:17,422 [INFO] [gRPC PreverLote] total_itens=3 | tempo=1.55ms
  ```
