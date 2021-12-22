from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

#  df = pd.read_pickle('database.pkl') # to run locally
df = pd.read_pickle('/var/www/webApp/webApp/database.pkl') # to run on server



df = pd.DataFrame(df, columns=['Rank',
                               'Logo', 
              'Name', 
              'Asset Type', 
              'Price',                                                                
              '24Hr Change', 
              'Volume 24Hr', 
              'Circulating Supply',
              'Market Cap'])

df_commodities = df[df['Asset Type'].isin(['Commodity'])]
df_stocks = df[df['Asset Type'].str.contains('Stock', case=False)]
df_currencies = df[df['Asset Type'].isin(['Currency'])]
df_cryptocurrencies = df[df['Asset Type'].isin(['Cryptocurrency'])]

dataFrames = [df,
              df_commodities,
              df_stocks,
              df_currencies,
              df_cryptocurrencies]


marketCapValues =  ['${:,.2f}T'.format(i.loc[:, ['Market Cap']].sum()[0] / 1e12) for i in dataFrames]
marketCapNames = ['All', 'Comms', 'Stocks', 'Currs', 'Cryptos']
marketCaps = {k: v for k, v in zip(marketCapNames, marketCapValues)}

# Format numbers in table
format_mapping={'Price': '${:,.2f}',
                'Volume 24Hr': '${:,.0f}',
                'Circulating Supply': '{:,.0f}',
                'Market Cap': '${:,.0f}'}




# Apply formatting
for i, dataFrame in enumerate(dataFrames):
    print (dataFrame)
    for key,value in dataFrame.items():
        if None in value:
            print(dataFrame.key)
    for key, value in format_mapping.items():
        print(dataFrame[key])
        
        dataFrame[key] = dataFrame[key].apply(value.format)

html_tables = []

for i, dataFrame in enumerate(dataFrames):
    html_table = dataFrame.to_html(index=False, render_links=True,escape=False, table_id='table', classes='row-border hover')
    html_tables.append(html_table)



@app.route("/")
def shows_tables():
    return render_template('index.html',table=html_tables[0], marketCaps = marketCaps)

@app.route("/commodities")
def shows_commodities():
    return render_template('index.html',table=html_tables[1], marketCaps = marketCaps)

@app.route("/stocks")
def shows_stocks():
    return render_template('index.html',table=html_tables[2], marketCaps = marketCaps)

@app.route("/currencies")
def shows_currencies():
    return render_template('index.html',table=html_tables[3], marketCaps = marketCaps)

@app.route("/cryptocurrencies")
def shows_cryptocurrencies():
    return render_template('index.html',table=html_tables[4], marketCaps = marketCaps)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)