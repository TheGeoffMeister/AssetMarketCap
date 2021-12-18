from flask import Flask, render_template
import yfinance as yf
import pandas as pd
import csv
import concurrent

app = Flask(__name__)

# Get list of S&P100 Ticker from wikipedia
table=pd.read_html('https://en.wikipedia.org/wiki/S%26P_100')
df = table[2]
df.to_csv('S&P100-Info.csv')

# Get list of FTSE100 Ticker from wikipedia
table=pd.read_html('https://en.wikipedia.org/wiki/FTSE_100_Index')
df = table[3]

# Swap Company and EPIC/Ticker Columns
cols = list(df.columns)
a, b = cols.index('Company'), cols.index('EPIC')
cols[b], cols[a] = cols[a], cols[b]
df = df[cols]
df['EPIC'] = df['EPIC'].apply(lambda x: x+".L" if x[-1] != "." else x+"L")
df.to_csv('FTSE100-Info.csv')

# Define which assets to work with
cryptos = ["Cryptocurrency", "Cryptos.csv"]
sp500 = ["US Company", "S&P100-Info.csv"]
FTSE100 = ["UK Company", "FTSE100-Info.csv"]
commodities = ["Precious Metal", "Commodities.csv"]
Other_Companies = ["World Company", "BigCompanies.csv"]

assets = [sp500, FTSE100, cryptos, commodities, Other_Companies]
all_assets = []

# Keep track of totals
Precious_Metals_Total = 0
Companies_Total = 0
Crypto_Currencies_Total = 0

def read_asset_lists(input_file):    
    
    asset_type = input_file[0]
    csv_file = input_file[1]    
    
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        assets = list(reader)[1:]
    
    list_of_assets = [[asset_type, i] for i in assets[:5]]

    return list_of_assets


def wrapper(asset):
    
    try:
        return Get_Info(asset)        
    except:
        return None
    
def Get_Broken_Images(ticker):
    
    if ticker == 'GOOGL':
       logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/500px-Google_2015_logo.svg.png"
    
    if ticker == 'BAC':
       logo_url = "https://dwglogo.com/wp-content/uploads/2016/06/1000px-Logo-of-Bank-of-America.png"
        
    if ticker == 'HD':
       logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/TheHomeDepot.svg/360px-TheHomeDepot.svg.png"

    if ticker == 'PG':
       logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Procter_%26_Gamble_logo.svg/300px-Procter_%26_Gamble_logo.svg.png"
     
    if ticker == 'TMUS':
       logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Telekom_Logo_2013.svg/440px-Telekom_Logo_2013.svg.png"

    if ticker == '2222.SR':
       logo_url = "https://www.freelogovectors.net/wp-content/uploads/2021/01/saudiaramcologo-freelogovectors.net_.png"
    
    return logo_url

# Get basic infomation on asset from API
def Get_Info(asset):
    
    labels = ['Logo', 
              'Name', 
              # 'Ticker', 
              'Asset Type', 
              'Price',                                                                
              '24Hr Change', 
              'Volume 24Hr', 
              'Circulating Supply',
              'Market Cap']
    
    df = pd.DataFrame([["",
                        "",
                        # "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""]], columns=labels)
    
    # Get asset infomation from yfinance API
    asset_type = asset[0]
    ticker = asset[1][1]
    Name = asset[1][2]
    data = yf.Ticker(ticker)                
    hist = data.history(period="5d", interval = "5m")        
    Price = float(hist.iloc[-2 : -1]['Open'])
    currency = data.info['currency']
    previous_close = data.info['previousClose']
    logo_url = data.info['logo_url']
    change24hr = ((Price - previous_close) / previous_close) *100
    
    if data.info['volume24Hr'] is not None:
        volume24hr = float(data.info['volume24Hr'])
    else:
        volume24hr = 0.0
    
    # Apply exchange rate for non USD assets
    if currency != 'USD':
        curr_data = yf.Ticker('USD'+currency+'=X')        
        exch_rate = curr_data.history(period="5d", interval = "5m")
        exch_rate = float(exch_rate.iloc[-2 : -1]['Open'])
    else:
        exch_rate = 1.0
        
    Price /= exch_rate
        
    
    # Create Circulating supply for precious metals
    if ticker == "GC=F":        
        Circulating_Supply = 201296000000/28.34952
        Marketcap = Circulating_Supply*Price
        
    elif ticker == "SI=F":        
         Circulating_Supply = 1751000000000/28.34952
         Marketcap = Circulating_Supply*Price
            
    elif ticker == "PL=F":        
         Circulating_Supply = 10000000000/28.34952
         Marketcap = Circulating_Supply*Price
         
    elif ticker == "PA=F":        
         Circulating_Supply = 20000000
         Marketcap = Circulating_Supply*Price
         
    else:    
        if data.info['marketCap'] is not None:
            Marketcap = float(data.info['marketCap']) / exch_rate
        else:
            Marketcap = 0.0
    
   
    Circulating_Supply = Marketcap / Price
    
    
    # Find missing logo images
    if ticker in ['GOOGL','BAC','HD','PG','TMUS','2222.SR']:    
        logo_url = Get_Broken_Images(ticker)    

    if len(logo_url) < 1:        
        if "=" in ticker:
            logo_url= 'static/icons/'+ticker.lower()+'.png'                
        else:
            logo_url= 'static/icons/'+ticker[:-4].lower()+'.png'
            
    logo_html = '<img src='+logo_url+' width="40" height="40">'
    
    
    # Reduce height of some images    
    if ticker in ['GOOGL', 'MA', 'PYPL', 'ADBE', 'BARC.L', 'AV.L', 'ANTO.L',
                  'IAG.L', 'CCH.L']:
        logo_html = '<img src='+logo_url+' width="40" height="20">'
    
    # colour the 24hr price change red or green
    if change24hr >= 0:
        change24hr = '{:.2f}%'.format(change24hr)    
        change24Hr_html = '<p style="color: green; "> '+change24hr+ ' </p>'
    else:
        change24hr = '{:.2f}%'.format(change24hr)
        change24Hr_html = '<p style="color: red; "> '+change24hr+ ' </p>'
    
    # Create dataframe of asset
    dataframe1 = pd.DataFrame([[logo_html,
                                Name,
                                # ticker,                                  
                                asset_type,
                                Price,
                                change24Hr_html,
                                volume24hr,
                                Circulating_Supply,
                                Marketcap]], columns=labels)
    
    # Append to the main dataframe
    df = df.append(dataframe1, ignore_index=True)    
    df = df.iloc[1:]
    
    return df


# Collate assets   
for asset in assets:
    a = read_asset_lists(asset)
    for i in a:
        all_assets.append(i)

df = pd.DataFrame()

# Multithread each request
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = [executor.submit(wrapper, all_assets[i]) for i in range(len(all_assets))]
    
    for f in concurrent.futures.as_completed(results):
        if f.result() is not None:
            df = df.append(f.result())

# Sort table by market cap    
df = df.sort_values('Market Cap', ascending=False)

# Format numbers in table
format_mapping={'Price': '${:,.2f}',
                'Volume 24Hr': '${:,.0f}',
                'Circulating Supply': '{:,.0f}',
                'Market Cap': '${:,.0f}'}

# Apply formatting
for key, value in format_mapping.items():
    df[key] = df[key].apply(value.format)

# Remove duplicate entry    
df = df[~df['Name'].isin(['Alphabet Inc. (Class C)'])]

#Insert ranking column
df.insert(0, "Rank", range(1, len(df) + 1))

# Output to HTML   
html_table = df.to_html(index=False, render_links=True,escape=False)


@app.route("/")
def shows_tables():
    return render_template('index.html',table=html_table)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)