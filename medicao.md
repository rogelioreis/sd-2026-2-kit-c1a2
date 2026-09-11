# Comparacao TCP x UDP

Resultados:
- TCP: 19.78 ms
- UDP: 45.25 ms

No teste na VM local, o TCP foi mais rapido que o UDP nas 100 mensagens porque manteve a conexao aberta e reaproveitou o buffer do sistema. Na rede real o UDP costuma ser mais leve por nao ter ACK, mas o TCP garante a entrega e a ordem dos dados.
