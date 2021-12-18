from flask import Flask, render_template,jsonify
import yfinance as yf
import pandas as pd
import csv


app = Flask(__name__)


table=pd.read_html('https://en.wikipedia.org/wiki/S%26P_100')
df = table[2]
df.to_csv('S&P100-Info.csv')

table=pd.read_html('https://en.wikipedia.org/wiki/FTSE_100_Index')
df = table[3]

# Swap Company and EPIC/Ticker Columns
cols = list(df.columns)
a, b = cols.index('Company'), cols.index('EPIC')
cols[b], cols[a] = cols[a], cols[b]
df = df[cols]

df.to_csv('FTSE100-Info.csv')

cryptos = ["Cryptocurrency", "Cryptos.csv"]
sp500 = ["US Company", "S&P100-Info.csv"]
FTSE100 = ["UK Company", "FTSE100-Info.csv"]
commodities = ["Commodity", "Commodities.csv"]

assets = [sp500, FTSE100, cryptos, commodities]


def read_asset_lists(input_file):
    
    asset_type = input_file[0]
    csv_file = input_file[1]
    
    
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        assets = list(reader)[1:]
    
    # list_of_assets = [list(str.split(i[0],",")) for i in assets]
    
    list_of_assets = assets[:3]
    
    list_of_assets = [[asset_type, i] for i in list_of_assets]


    return list_of_assets
    
all_assets = []
for asset in assets:
    all_assets.append(read_asset_lists(asset))

data = yf.Ticker("USDGBP=X")        
hist = data.history(period="5d", interval = "5m")
USDGBP = float(hist.iloc[-2 : -1]['Open'])

def Get_Info(list_of_assets):
    
    df = pd.DataFrame([["","","","","","",""]], columns=['Logo', 'Name', 'Asset Type', 'Price', 'Volume 24Hr', 'Circulating Supply','Market Cap'])
    
    # asset_type = list_of_assets[0]
    # asset_list = list_of_assets[1]

    for asset in list_of_assets:
        asset_type = asset[0]
        ticker = asset[1][1]
        data = yf.Ticker(ticker)                
        hist = data.history(period="5d", interval = "5m")        
        Price = float(hist.iloc[-2 : -1]['Open'])
        
        if asset_type == "UK Company":
            Price /= USDGBP        
        
        if ticker == "GC=F":
            
            Circulating_Supply = 201296000000/28.34952
            Marketcap = Circulating_Supply*Price
            
        elif ticker == "SI=F":
            
             Circulating_Supply = 1751000000000/28.34952
             Marketcap = Circulating_Supply*Price
             
        else:
        
            if data.info['marketCap'] is not None:
                Marketcap = float(data.info['marketCap'])
            else:
                Marketcap = 0.0        
        
        
        if data.info['volume24Hr'] is not None:
            volume24hr = float(data.info['volume24Hr'])
        else:
            volume24hr = 0.0
        Circulating_Supply = Marketcap / Price
        logo_url = data.info['logo_url']        
        
        if len(logo_url) < 1:
            
            if "=" in ticker:
                logo_url= 'static/icons/'+ticker.lower()+'.png'                
            else:
                logo_url= 'static/icons/'+ticker[:-4].lower()+'.png'
        
        logo_html = '<img src='+logo_url+' width="40" height="40">'
        dataframe1 = pd.DataFrame([[logo_html,
                                    asset[1][2],                                    
                                    asset_type,
                                    Price,
                                    volume24hr,
                                    Circulating_Supply,
                                    Marketcap]], columns=['Logo',
                                                          'Name',                                                           
                                                           'Asset Type',
                                                           'Price',
                                                           'Volume 24Hr',
                                                           'Circulating Supply',
                                                           'Market Cap'])
        df = df.append(dataframe1, ignore_index=True)
        
        # df.index.name = "Rank"
        
    df = df.iloc[1:]
    
        
    return df

df = pd.DataFrame()

for assets in all_assets:
    df = df.append(Get_Info(assets), ignore_index=True)
    
df = df.sort_values('Market Cap', ascending=False)

format_mapping={'Price': '${:,.2f}', 'Volume 24Hr': '${:,.0f}', 'Circulating Supply': '{:,.0f}', 'Market Cap': '${:,.0f}'}

for key, value in format_mapping.items():
    df[key] = df[key].apply(value.format)
    
df.insert(0, "Rank", range(1, len(df) + 1))

    
html_table = df.to_html(index=False, render_links=True,escape=False)



@app.route("/")
def shows_tables():
    return render_template('index.html',table=html_table)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)