
from datetime import datetime
import time
import requests


class Bot:
    def __init__(self):
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.params = {
            'start': '1',
            'limit': '100',
            'convert': 'USD'
        }
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': 'a380b07a-f12a-41ee-b156-b2a7bad1ba35',
        }
        self.orders = []

    def fetchCurrenciesData(self):
        r = requests.get(url=self.url, headers=self.headers, params=self.params).json()
        return r['data']

    def canBuy(self):
        # controlla se esistono operazioni di acquisto ancora non chiuse
        for order in self.orders:
            if order['status'] == 'open':
                return False
        return True


impactBot = Bot()

while (1):
    now = datetime.now()
    currencies = impactBot.fetchCurrenciesData()
    print(currencies)
    i = 1  # incremento percentuale
    r = 4  # valore sopra il quale fare partire l'operazione di acquisto
    n = 0  # numero di valute cui prezzo non ha subito un incremento maggiore di i nell'ultima ora
    z = -1  # percentuale sotto la quale vendi la valuta
    bestCurrency = None  # la valuta con la rivalutazione di prezzo maggiore

    # logic
    if impactBot.canBuy():
        print(f'Non ci sono posizioni aperte-Controllo se trovo valute che hanno guadagnato piu di (i)% nella ultima ora')
    # il codice qui dentro viene eseguito solo se non ci sono operazioni aperte

    for currency in currencies:
        if not bestCurrency or currency['quote']['USD']['percent_change_1h'] > bestCurrency['quote']['USD']['percent_change_1h']:
            bestCurrency = currency
        if currency['quote']['USD']['percent_change_1h'] > 1:
            n = n + 1
        if n > 4:
            print('Ho trovato più di quattro valute - creo un nuovo ordine')
            newOrder = {
                'datetime': now,
                'symbol': bestCurrency['symbol'],
                'enterPrice': bestCurrency['quote']['USD']['price'],
                'exitPrice': None,
                'status': 'open'
            }
            impactBot.orders.append(newOrder)
        else:
            print('controllo gli ordini ancora aperti-se si veririca la condizione di svautazione allora vendo')
            for currency in currencies:
                if currency['quote']['USD']['percent_change_1h'] < -1:
                    for order in impactBot.orders:
                        if order['status'] == 'open' and order['symbol'] == currency['symbol']:
                            # vendi
                            order['status'] = 'close'
                            order['exitprice'] = currency['quote']['USD']['price']

    # overview
    initialAmount = 10000
    profit = 0
    for order in impactBot.orders:
        if order['status'] == 'close':
            profit = initialAmount * order['exitPrice'] / order['enterPrice']
    finalAmount = initialAmount + profit
    print(f'Ho realizzato {len(impactBot.orders)} compravendite - sono partito con {initialAmount}€ e adesso ho {finalAmount}€')

    # routine
    minutes = 10
    seconds = minutes * 60
    time.sleep(seconds)
