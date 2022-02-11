from binance.client import Client


class Connect:
    def make_connection(self):
        #Tutaj jest miejsce do wpisania twoich kluczy API
        api_key = ""
        api_secret = ""

        
        
        return Client(api_key, api_secret)