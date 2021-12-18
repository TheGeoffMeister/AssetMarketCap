import yfinance as yf
from pprint import pprint

ticker = "BTC-USD"
msft = yf.Ticker(ticker)
pprint(msft.info)
hist = msft.history(period="1d", interval = "1m")
price = (float(hist.iloc[-2 : -1]['Open']))
result = ticker+": "+str(price)

print(result)
        

    