from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
from dateutil import tz
from getpass import getpass

import time
import json, requests
import logging
import configparser
import sys
import os

logging.disable(level=(logging.DEBUG))

def Martingale(valor):
    valorGale = float(config['valorGale'])
    lucro_esperado = float(valor) * valorGale

    return float(lucro_esperado)


def Payout(par, timeframe):
    API.subscribe_strike_list(par, timeframe)
    while True:
        d = API.get_digital_current_profit(par, timeframe)
        if d > 0:
            break
        time.sleep(1)
    API.unsubscribe_strike_list(par, timeframe)
    return float(d / 100)


def banca():
    return API.get_balance()


def configuracao():
    arquivo = configparser.RawConfigParser()
    arquivo.read('config.txt')

    return {'entrada': arquivo.get('GERAL', 'entrada'), 'conta': arquivo.get('GERAL', 'conta'), 'stop_win': arquivo.get('GERAL', 'stop_win'), 'stop_loss': arquivo.get('GERAL', 'stop_loss'), 'payout': 0, 'banca_inicial': banca(), 'martingale': arquivo.get('GERAL', 'martingale'), 'valorGale': arquivo.get('GERAL', 'valorGale'), 'sorosgale': arquivo.get('GERAL', 'sorosgale'), 'niveis': arquivo.get('GERAL', 'niveis'), 'analisarTendencia': arquivo.get('GERAL', 'analisarTendencia'), 'noticias': arquivo.get('GERAL', 'noticias'), 'telegram_token': arquivo.get('telegram', 'telegram_token'), 'telegram_id': arquivo.get('telegram', 'telegram_id'), 'usar_bot': arquivo.get('telegram', 'usar_bot')}


def carregaSinais():
    x = open('sinais.txt')
    y = []
    for i in x.readlines():
        y.append(i)
    x.close
    return y


def entradas(par, entrada, direcao, config, opcao, timeframe):
    if opcao == 'digital':
        status, id = API.buy_digital_spot(par, entrada, direcao, timeframe)
        if status:
            # STOP WIN/STP LOSS

            banca_att = banca()
            stop_loss = False
            stop_win = False

            if round((banca_att - float(config['banca_inicial'])), 2) <= (abs(float(config['stop_loss'])) * -1.0):
                stop_loss = True

            if round((banca_att - float(config['banca_inicial'])), 2) >= abs(float(config['stop_win'])):
                stop_win = True

            while True:
                status, lucro = API.check_win_digital_v2(id)
                #print(API.check_win_digital_v2(id))

                if status:
                    if lucro > 0:
                        return 'win', round(lucro, 2), stop_win
                    elif lucro == 0.0:
                        return 'doji', 0, False
                    else:
                        return 'loss', round(lucro, 2), stop_loss
                    break
        else:
            return 'error', 0, False

    elif opcao == 'binaria':
        status, id = API.buy(entrada, par, direcao, timeframe)

        if status:
            resultado, lucro = API.check_win_v3(id)
            #print(API.check_win_v3(id))

            banca_att = banca()
            stop_loss = False
            stop_win = False

            if round((banca_att - float(config['banca_inicial'])), 2) <= (abs(float(config['stop_loss'])) * -1.0):
                stop_loss = True

            if round((banca_att - float(config['banca_inicial'])), 2) >= abs(float(config['stop_win'])):
                stop_win = True

            if resultado:
                if resultado == 'win':
                    return resultado, round(lucro, 2), stop_win
                elif resultado == 'equal':
                    return 'doji', 0, False
                elif resultado == 'loose':
                    return 'loss', round(lucro, 2), stop_loss
        else:
            return 'error', 0, False
    else:
        return 'opcao errado', 0, False


def timestamp_converter():
    hora = datetime.now()
    tm = tz.gettz('America/Sao Paulo')
    hora_atual = hora.astimezone(tm)
    return hora_atual.strftime('%H:%M:%S')

def Timeframe(timeframe):

    if timeframe == 'M1':
        return 1

    elif timeframe == 'M5':
        return 5

    elif timeframe == 'M15':
        return 15

    elif timeframe == 'M30':
        return 30

    elif timeframe == 'H1':
        return 60
    else:
        return 'erro'


def Mensagem(mensagem):
    print(mensagem)
    if VERIFICA_BOT == 'S':
        token = config['telegram_token']
        chatID = TELEGRAM_ID
        send = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chatID}&parse_mode=Markdown&text={mensagem}'
        return requests.get(send)

def tendencia(par, timeframe):
    velas = API.get_candles(par, (int(timeframe) * 60), 20,  time.time())
    ultimo = round(velas[0]['close'], 4)
    primeiro = round(velas[-1]['close'], 4)
    diferenca = abs(round(((ultimo - primeiro) / primeiro) * 100, 3))
    tendencia = "call" if ultimo < primeiro and diferenca > 0.01 else "put" if ultimo > primeiro and diferenca > 0.01 else False
    return tendencia

def checkProfit(par, timeframe):
    all_asset = API.get_all_open_time()
    profit = API.get_all_profit()

    digital = 0
    binaria = 0

    if timeframe == 60:
        return 'binaria'

    if all_asset['digital'][par]['open']:
        digital = Payout(par, timeframe)
        digital = round(digital, 2)

    if all_asset['turbo'][par]['open']:
        binaria = round(profit[par]["turbo"], 2)

    if binaria < digital:
        return "digital"

    elif digital < binaria:
        return "binaria"

    elif digital == binaria:
        return "digital"

    else:
        "erro"

def noticas(paridade, minutos_lista):
    objeto = json.loads(texto)

    # Verifica se o status code é 200 de sucesso
    if response.status_code != 200 or objeto['success'] != True:
        print('Erro ao contatar notícias')

    # Pega a data atual
    data = datetime.now()
    tm = tz.gettz('America/Sao Paulo')
    data_atual = data.astimezone(tm)
    data_atual = data_atual.strftime('%Y-%m-%d')

    # Varre todos o result do JSON
    for noticia in objeto['result']:
        # Separa a paridade em duas Ex: AUDUSD separa AUD e USD para comparar os dois
        paridade1 = paridade[0:3]
        paridade2 = paridade[3:6]
        
        # Pega a paridade, impacto e separa a data da hora da API
        moeda = noticia['economy']
        impacto = noticia['impact']
        atual = noticia['data']
        data = atual.split(' ')[0]
        hora = atual.split(' ')[1]
        
        # Verifica se a paridade existe da noticia e se está na data atual
        if moeda == paridade1 or moeda == paridade2 and data == data_atual:
            formato = '%H:%M:%S'
            d1 = datetime.strptime(hora, formato)
            d2 = datetime.strptime(minutos_lista, formato)
            dif = (d1 - d2).total_seconds()
            # Verifica a diferença entre a hora da noticia e a hora da operação
            minutesDiff = dif / 60
        
            # Verifica se a noticia irá acontencer 30 min antes ou depois da operação
            if minutesDiff >= -30 and minutesDiff <= 0 or minutesDiff <= 30 and minutesDiff >= 0:
                return impacto, moeda, hora, True
            else:
                return 0, 0, 0, False
        else:
            return 0, 0, 0, False

print('=========================================\n|   INSIRA E-MAIL E SENHA DA IQOPTION   |\n=========================================')
email = str(input('E-mail: '))
senha = getpass()
API = IQ_Option(email, senha)
API.connect()
config = configuracao()
API.change_balance(config['conta'])  # PRACTICE / REAL

global VERIFICA_BOT, TELEGRAM_ID

config['banca_inicial'] = banca()

VERIFICA_BOT = config['usar_bot']
TELEGRAM_ID = config['telegram_id']
analisarTendencia = config['analisarTendencia']
noticias = config['noticias']

if API.check_connect():
    os.system('cls') 
    print('# Conectado com sucesso!')
    if noticias == 'S':
        response = requests.get("https://botpro.com.br/calendario-economico/")
        texto = response.content
else:
    print(' Erro ao conectar')
    input('\n\n Aperte enter para sair')
    sys.exit()

valor_entrada = config['entrada']
valor_entrada_b = float(valor_entrada)

lucro = 0
lucroTotal = 0

sinais = carregaSinais()

for x in sinais:
    timeframe_retorno = Timeframe(x.split(';')[0])
    timeframe = 0 if (timeframe_retorno == 'error') else timeframe_retorno
    par = x.split(';')[1].upper()
    minutos_lista = x.split(';')[2]
    direcao = x.split(';')[3].lower().replace('\n', '')
    mensagem_paridade = f'EM ESPERA: {par} | TEMPO: {str(timeframe)}M | HORA: {str(minutos_lista)} | DIREÇÃO: {direcao}'
    Mensagem(mensagem_paridade)
    opcao = 'error'
    # print(par)
    verf = False
    while True:
        t = timestamp_converter()

        if minutos_lista < t:
            break

        s = minutos_lista
        f = '%H:%M:%S'
        dif = abs((datetime.strptime(t, f) - datetime.strptime(s, f)).total_seconds())
        # print('Agora: ',t)
        # print('Falta: ',dif)

        # Verifica se tem noticias 40 seg antes
        if noticias == 'S':
            if dif == 40:
                impacto, moeda, hora, stts = noticas(par,minutos_lista)
                if stts:
                    if impacto > 1:
                        Mensagem(f' NOTÍCIA COM IMPACTO DE {impacto} TOUROS NA MOEDA {moeda} ÀS {hora}!')
                        break

        # Verifica opção binário ou digita quando falta 25 seg
        if dif == 25:
            opcao = checkProfit(par, timeframe)

        # Verifica tendencia quando falta 5 seg
        if analisarTendencia == 'S':
            if dif == 5:
                if verf == False:
                    tend = tendencia(par, timeframe)
                    verf = True
                    if tend == False:
                        Mensagem(f' ATIVO {par} COM TENDÊNCIA DE LATERIZAÇÃO!')
                    else:
                        if tend != direcao:
                            Mensagem(f'\n ATIVO {par} CONTRA TENDÊNCIA\n')
                            break

        #Inicia a operação 2 seg antes
        entrar = True if (dif == 2) else False

        if entrar:
            Mensagem('\n\n INICIANDO OPERAÇÃO..')
            dir = False
            dir = direcao

            if dir:
                mensagem_operacao = f'ATIVO: {par} | OPÇÃO: {opcao} | HORA: {str(minutos_lista)} | DIREÇÃO: {dir}'
                Mensagem(mensagem_operacao)
                valor_entrada = valor_entrada_b
                opcao = 'binaria' if (opcao == 60) else opcao
                resultado, lucro, stop = entradas(par, valor_entrada, dir, config, opcao, timeframe)
                lucroTotal += lucro
                mensagem_resultado = f' RESULTADO ->  {resultado} | R${str(lucro)}\n Lucro: R${str(round(lucroTotal, 2))}\n'
                Mensagem(mensagem_resultado)

                # print(resultado)
                if resultado == 'error':
                    break

                if resultado == 'win' or resultado == 'doji':
                    break

                if stop:
                    mensagem_stop = f'\nStop {resultado.upper()} batido!'
                    Mensagem(mensagem_stop)
                    sys.exit()

                if resultado == 'loss' and config['martingale'] == 'S':
                    valor_entrada = Martingale(float(valor_entrada))
                    for i in range(int(config['niveis']) if int(config['niveis']) > 0 else 1):

                        mensagem_martingale = f' MARTINGALE NIVEL {str(i+1)}..'
                        Mensagem(mensagem_martingale)
                        resultado, lucro, stop = entradas(par, valor_entrada, dir, config, opcao, timeframe)
                        lucroTotal += lucro
                        mensagem_resultado_martingale = f' RESULTADO ->  {resultado} | R${str(lucro)}\n Lucro: R${str(round(lucroTotal, 2))}\n'
                        Mensagem(mensagem_resultado_martingale)

                        if stop:
                            mensagem_stop = f'\nStop {resultado.upper()} batido!'
                            Mensagem(mensagem_stop)
                            sys.exit()

                        if resultado == 'win' or resultado == 'doji':
                            #print('\n')
                            break
                        else:
                            valor_entrada = Martingale(float(valor_entrada))
                    break
                else:
                    break
        time.sleep(0.1)
    # break
Mensagem(' Lista de sinais finalizada!')
banca_att = banca()
Mensagem(f' Banca: R${banca_att}')
Mensagem(f' Lucro: R${str(round(lucroTotal, 2))}')
sys.exit()