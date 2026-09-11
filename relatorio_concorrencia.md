# Relatório de Carga e Concorrência

## Resultados Medidos (50 clientes simultâneos)

- **Servidor Multicliente (`servidor_multicliente.py`):**
  - Tempo total de execução: **142.26 ms**
  - Tempo médio por cliente: **30.97 ms**
  - Taxa de sucesso: **100% (50/50 clientes atendidos)**

- **Servidor Single-thread (`servidor_eco.py`):**
  - Taxa de falha: **98% de recusa de conexão** (`Connection refused` / `Connection reset by peer`)
  - Apenas 1 cliente conseguiu concluir a troca de mensagens antes da fila de conexões pendentes do socket estourar.

## Análise Técnica

1. **Bloqueio do Modelo Sequencial:** No servidor da Aula 2 (`servidor_eco.py`), funções como `accept()` e `recv()` são bloqueantes. Quando 50 requisições chegam em milissegundos, o socket esgota o buffer de backlog e o sistema operacional rejeita as conexões subsequentes.
2. **Eficiência do Multithreading:** No `servidor_multicliente.py`, o laço principal delega a conexão para uma nova thread imediatamente após o `accept()`. Isso liberou o socket para continuar aceitando novos clientes em paralelo, atingindo 100% de sucesso em apenas ~142 ms.
