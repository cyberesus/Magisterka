from .config import Connect
from .order import Order
import datetime as dt
import numpy
import talib
import time
import threading

class Main:
    def __init__(self):

        self.client = Connect().make_connection()
        print("Logged")
        self.start_trade()
        threading.Thread.__init__(self)

    def start_trade(self):
        try:
            self.trading = Order()
            print("Starting new trade...")

            while True:
                try:
                    #Zmiana daty i/lub przedziału czasowego dla innych ram czasowych
                    klines = self.client.get_historical_klines("BTCUSDT", self.client.KLINE_INTERVAL_15MINUTE, "1 day ago UTC")
                except: 
                    print('Timeout! Waiting for time binance to respond...')
                    time.sleep(120)
                    print('Trying to connect agian...')
                    klines = self.client.get_historical_klines("BTCUSDT", self.client.KLINE_INTERVAL_15MINUTE, "1 day ago UTC")

                prices_list = []
                for i in klines:
                    prices_list.append(float(i[4]))
            
                #Kalkulacja RSI, zmiana dla różnej strategii lub wskaźnika
                last_RSI = talib.RSI(numpy.asarray(prices_list), 14)[-1]
                if last_RSI > 75:

                    self.order_to_track = self.trading.sell(prices_list[len(prices_list)-1])
                    self.track_trade()

                elif last_RSI < 25:

                    self.order_to_track = self.trading.buy(prices_list[len(prices_list)-1])
                    self.track_trade()
                else:
                    time.sleep(1.5)
                    print('RSI : ', last_RSI)
                    print('No enter points, looking agian...')        
        except Exception as e:
            print(e)

    def track_trade(self):
        #Jak bardzo zmieniła się cena w % w oparciu o cenę bieżącą i cenę zamówienia
        def precent_change(orginal_price, new_price):
                
            orginal_price = float(orginal_price)
            new_price = float(new_price)
            return (orginal_price - new_price)/orginal_price*100  

        while True:
            time.sleep(1.5)
            try:
                self.last_price = self.client.get_recent_trades(symbol='BTCUSDT')[-1]['price']
            except: 
                print('Timeout! Waiting for  binance to respond...')
                time.sleep(120)
                print('Trying to connect agian...')
                self.last_price = self.client.get_recent_trades(symbol='BTCUSDT')[-1]['price']

            change = precent_change(self.order_to_track['fills'][0]['price'], self.last_price)
            if(self.order_to_track['side']=='BUY'):

                change = change*-1
                print(change)
            #Ustalenie cen strategii profit take oraz stop loss
            if change >= 1.5 or change <= -0.5:

                self.end_trade()
                print('Current trade ended with profit  of:', change,'%')
                time.sleep(1.5)

                try:

                    self.start_trade()

                except:
                    print("Can't make new trade, trying agian in 120 sec...")
                    time.sleep(120)
                    self.start_trade()

            else:
                
                print("Current trade profit: ", format(change,'2f'),"%")

    def end_trade(self):
        self.trading.close_order(self.order_to_track['executedQty'], self.order_to_track['side'])
        print('End. Order finished successfully')

Main()
