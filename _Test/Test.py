from flask import Flask
import yfinance as yf
# from pprint import pprint
app = Flask(__name__)
from time import sleep

@app.route("/")
def home():
    
    tickers = ['AAPL','MSFT', 'BTC-USD']
    
    while True:
        
        sleep(1)
        
        result = []
        
        for t in tickers:
            
            msft = yf.Ticker(t)
            
            # get stock info
            # pprint(msft.info)
            
            # get historical market data
            hist = msft.history(period="1d", interval="1m")
            
            price = (float(hist.iloc[-2 : -1]['Open']))
            
            result.append( (t+": "+str(price)))
            
            print(result)
        
        return """<!DOCTYPE html>
<html>
    <head>
        <title> Plot</title>
        <meta content='5; url=http://127.0.0.1:5000/'>

    </head>
    <body>
        <a>"""\
        +str(result)+\
        """</a>
    </body>
</html>"""


if __name__ == "__main__":
    app.run()


# <meta content='5; url=http://127.0.0.1:5000/' http-equiv='refresh'>
        
    






    