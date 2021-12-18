from flask import Flask, render_template,jsonify
import yfinance as yf
from flask_table import Table, Col
import csv

app = Flask(__name__)

tickers = ("BTC-USD", "AAPL")
SP500_Tickers = csv.reader("SP500_Tickers.csv")

with open("SP500_Tickers.csv", newline='') as f:
    reader = csv.reader(f)
    companies = list(reader)[1:]


companies = [list(str.split(i[0],",")) for i in companies]

def getData():

    all_data = []
    
    for company in companies[:2]:
        ticker = company[0]
        print(ticker)
        data = yf.Ticker(ticker)
        Marketcap = data.info['marketCap']
        hist = data.history(period="1d", interval = "1m")
        Price = float(hist.iloc[-2 : -1]['Open'])
        Circulating_Supply = int(Marketcap / Price)
        Price_Formatted = '{:.2f}'.format(round(float(Price), 2))
        Circulating_Supply = int(Marketcap / Price)
        logo_url = data.info['logo_url']
        logo_item = '<img src='+logo_url+'>'
        list1 = [logo_item,
                 company[1],
                 Price_Formatted,
                 Marketcap,
                 Circulating_Supply]

        all_data.append(list1)
        
        

    return all_data

all_data = getData()  


@app.route('/update_decimal', methods=['POST'])
def updatedecimal():        
    all_data = getData()    
    return jsonify('', render_template('random_decimal.html', x=all_data))


@app.route('/')
def index():
    return render_template('index.html', x=all_data)
        

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

    