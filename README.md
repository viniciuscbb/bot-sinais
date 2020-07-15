# bot-sinais
<br>
Bot opera apartir de uma lista de sinais(binaria ou digital) <br>
<br>
Exemplo de sinais:<br>
  <p>M1;eurusd;23:19:00;CALL - timeframe de 1 minuto</p>
  <p>M5;gbpusd;03:54:00;CALL - timeframe de 5 minutos</p>
  <p>M15;eurusd;23:30:00;CALL - timeframe de 15 minutos</p>
  <p>H1;eurusd;00:00:00;CALL - timeframe de 1 hora</p>
<br>
Os sinais deve ser inserido em sinais.txt <br>
<br>
# Configurações
<br>
Em config.txt colocar:
  - entrada (valor da entrada)
  - stop_win e stop_los;
  - tipo de conta;
  - martingale (S ou N)
  - valorGale
  - niveis (quantidade de MT)
  - analisarTendencia (S ou N)
  - noticias (S ou N)
<br> 
Instalar as dependencias necessarias:<br>
<p>pip install -r requirements.txt<p>
<br>
Para executar o robo: <br>
<p> python main.py </p>
<br>
Adicionado bot para Telegram , em que envia mensagem do status de cada operação eo seu resultado.
Removido o delay
Adicionado analisador de noticias (não opera com notícias de 2 ou 3 touros na moeda).
Adicionado analisador de tendência (não opera contra tendência),
<br>
Não me responsabilizo por delays e entradas atrasadas do bot.
Não me responsabilizo com o resultado das operações realizadas pelo bot.

BOT em testes.

"" Usar na conta demo !!""