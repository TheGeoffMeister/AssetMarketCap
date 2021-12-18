from flask import Flask, render_template,jsonify
import yfinance as yf
import pandas as pd
# import numpy as np

app = Flask(__name__)

# dataframe = pd.DataFrame()
tickers = ("BTC-USD", "AAPL")
prices = []
marketcaps = []

dataframe_main = pd.DataFrame([["-", "($)","($)"]], columns=['Name', 'Price', 'Market Cap'])

main_table = []

for ticker in tickers:    
    data = yf.Ticker(ticker)
    marketcap = data.info['marketCap']
    marketcaps.append(marketcap)
    hist = data.history(period="1d", interval = "5m")
    price = (float(hist.iloc[-2 : -1]['Open']))
    prices.append(price)
    dataframe1 = pd.DataFrame([[ticker, price, marketcap]], columns=['Name', 'Price', 'Market Cap'])
    dict1 = dict(name= ticker, price= price, marketcap= marketcap)
    main_table.append(dict1)
    # print(dataframe1)
    dataframe_main = dataframe_main.append(dataframe1, ignore_index=True)
    # print(dataframe)
    html = dataframe_main.to_html()
    # html = "<html>"+html+"</html>"
    
    # main.append(ticker)
    # main.append(price)
    # main.append(marketcap)
    

# @app.route('/update_decimal', methods=['POST'])
# def updatedecimal():
#     # random_decimal = np.random.rand()
#     # print(dataframe_main)
#     return jsonify('', render_template('random_decimal.html', x=main))


from flask_table import Table, Col

# Declare your table
class ItemTable(Table):
    name = Col('Name')
    price = Col('Price')
    marketcap = Col('Market Cap')
    
    main_table = main_table

# items = [dict(name='Name1', description='Description1'),
#          dict(name='Name2', description='Description2'),
#          dict(name='Name3', description='Description3')]

# Populate the table
table = ItemTable(main_table)

# Print the html
print(table.__html__())
# or just {{ table }} from within a Jinja template



@app.route('/')
def index():
    # print(dataframe_main)
    return render_template('index.html', x = table)
        

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    print(dataframe_main)

    