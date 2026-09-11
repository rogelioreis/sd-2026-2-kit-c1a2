# Comparacao TCP x UDP

## Resultados
- TCP: ~3.5ms (100 msgs)
- UDP: ~1.2ms (100 msgs)

## Comparacao
1. O UDP foi bem mais rapido que o TCP enviando as 100 mensagens.
2. Isso acontece porque o UDP nao precisa ficar esperando ACK nem confirmando conexao pra cada pacote.
3. O TCP garante a entrega e a ordem dos dados, mas cobra isso em tempo de controle.
4. Se o sistema nao pode perder nenhum dado (tipo banco ou chat), tem que usar TCP.
5. Se a prioridade for velocidade e latencia baixa (jogos, voz, streaming), o UDP e melhor.
