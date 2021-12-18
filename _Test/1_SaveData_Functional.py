from flask import Flask
import yfinance as yf
import pandas as pd
import csv
import concurrent.futures

app = Flask(__name__)

# if runing locally no need to include server path, if running on server however full path required
server_path = ''
# server_path = '/var/www/webApp/webApp/' # comment this out if running locally


# Get list of S&P100 Ticker from wikipedia
table=pd.read_html('https://en.wikipedia.org/wiki/S%26P_100')
df = table[2]
df['Symbol'] = df['Symbol'].apply(lambda x: x.replace(".", "-"))
df.to_csv(server_path+'S&P100-Info.csv')


# Get list of FTSE100 Ticker from wikipedia
table=pd.read_html('https://en.wikipedia.org/wiki/FTSE_100_Index')
df = table[3]

# Swap Company and EPIC/Ticker Columns
cols = list(df.columns)
a, b = cols.index('Company'), cols.index('EPIC')
cols[b], cols[a] = cols[a], cols[b]
df = df[cols]
df['EPIC'] = df['EPIC'].apply(lambda x: x+"L" if x[-1] == "." else x)
df['EPIC'] = df['EPIC'].apply(lambda x: x+".L" if "." not in x else x)
df['EPIC'] = df['EPIC'].apply(lambda x: x.replace(".A", ".L"))

df.to_csv(server_path+'FTSE100-Info.csv')

circulating_supplys = {}

# Get list of households from wikipedia
table=pd.read_html('https://en.wikipedia.org/wiki/List_of_countries_by_number_of_households')
df_houses = table[1]
circulating_supplys['Houses'] = df_houses['Households'].sum()

# Get list of oil reserves from wikipedia
table=pd.read_html('https://en.wikipedia.org/wiki/List_of_countries_by_proven_oil_reserves')
df_oil = table[0]
circulating_supplys['CL=F'] = df_oil.iloc[:, [2]].sum()[0] * 1000000000

# Get list of gas reserves from wikipedia
table=pd.read_html('https://en.wikipedia.org/wiki/List_of_countries_by_natural_gas_proven_reserves')
df_gas = table[1]
circulating_supplys['NG=F'] = (df_gas.iloc[:, [2]].sum()[0] * (1000 * 1000 * 1000) * 35.3147) / 1000 # price is per thousand cubic feet

# need to find weblinks to these

troy_oz = 31.1034768

circulating_supplys['GC=F'] = (201296*1000*1000) / troy_oz   # Gold https://www.gold.org/goldhub/data/above-ground-stocks
circulating_supplys["SI=F"] = (1751000*1000*1000) / troy_oz   # Silver
circulating_supplys["PL=F"] = (10000*1000*1000) / troy_oz # Platinum
circulating_supplys["PA=F"] = (20*1000*1000) / troy_oz # Palladium


# # Define which assets to work with
# crypto_file = "Yahoo_Cryptos.csv"

# def delete_empty_rows(file_path, new_file_path):
#     data = pd.read_csv(file_path, skip_blank_lines=True)
#     data.dropna(how="all", inplace=True)
#     data.to_csv(new_file_path, header=True)

# delete_empty_rows(crypto_file, crypto_file[:-4]+"_filtered.csv")

cryptos = ["Cryptocurrency", server_path+"Yahoo_Cryptos_filtered.csv"] # https://finance.yahoo.com/cryptocurrencies/?&offset=0&count=200
sp100 = ["US Stock", server_path+"S&P100-Info.csv"]

NASDAQ = ["US Stock", server_path+"NASDAQ.csv"]
NYSE = ["US Stock", server_path+"NYSE.csv"]

FTSE100 = ["UK Stock", server_path+"FTSE100-Info.csv"]
commodities = ["Commodity", server_path+"Commodities.csv"]
Other_Companies = ["Saudi Stock", server_path+"BigCompanies.csv"]
currencies = ["Currency", server_path+"Currencies.csv"]
 
#  
assets = [currencies, commodities, cryptos, NASDAQ, NYSE, FTSE100, Other_Companies]
all_assets = []

# Keep track of totals
Precious_Metals_Total = 0
Companies_Total = 0
Crypto_Currencies_Total = 0    


def get_currency_supplies(area_code):
    
    m2_m3 = "m2"
    
    # australia has no m2 so using m3
    if area_code == "australia":
        m2_m3 = "m3"
    
    for i in range(1,4):
        try:
            print ("Getting Circulating Supply of %s, Attempt: %s" %(area_code, i))
            tables = table=pd.read_html('https://tradingeconomics.com/%s/money-supply-%s' %(area_code,m2_m3))
            break
        except:            
            continue
    else:
        return 0.0
    
    for table in tables:
        
        if 'Last' in table:
            df = table
            filter_m2 = df.apply(lambda row: row.astype(str).str.contains('M2').any(), axis=1)
            df = df.loc[filter_m2]
            m2_supply = float(df['Last'])
            m2_unit = str(df['Unit'])
            break

        elif 'Actual' in table:
            df = table
            m2_supply = float(df['Actual'])
            m2_unit = str(df['Unit'])
            break
        
        else:
            m2_supply = 0.0
            
                
    if 'Million' in m2_unit:
        m2_supply*= 1e6
    elif 'Billion' in m2_unit:
        m2_supply*= 1e9
                    
    return m2_supply

def read_asset_lists(input_file):    
    
    asset_type = input_file[0]
    csv_file = input_file[1]    
    
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        assets = list(reader)[1:]
    
    list_of_assets = [[asset_type, i] for i in assets[:]]

    return list_of_assets


def wrapper(asset):
    
    try:
        return Get_Info(asset)        
    except:
        return None
    
def Get_Broken_Images(ticker):
    if ticker == 'GOOGL':
       logo_url = "static/icons/google.png"
    
    if ticker == 'FB':
       logo_url = "/static/icons/facebook.png"
        
    if ticker == 'BAC':
       logo_url = "/static/icons/Bank-of-America.png"
        
    if ticker == 'HD':
       logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/TheHomeDepot.svg/360px-TheHomeDepot.svg.png"

    if ticker == 'PG':
       logo_url = "/static/icons/Procter_Gamble.png"
     
    if ticker == 'TMUS':
       logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Telekom_Logo_2013.svg/440px-Telekom_Logo_2013.svg.png"

    if ticker == '2222.SR':
       logo_url = "/static/icons/saudi_aramco.png"

    if ticker == 'BABA':
       logo_url = "/static/icons/Alibaba-Group.png"

    if ticker == 'BRK-A':
       logo_url = "/static/icons/brk-a.png"
    
    return logo_url

def format_price_change(change24hr):
    # colour the 24hr price change red or green
    if change24hr >= 0:
        change24hr = '{:.2f}%'.format(change24hr)    
        change24Hr_html = '<p style="color: green; text-align:center;"> '+change24hr+ ' </p>'
    else:
        change24hr = '{:.2f}%'.format(change24hr)
        change24Hr_html = '<p style="color: red; text-align:center;"> '+change24hr+ ' </p>'
        
    return change24Hr_html

# Get basic infomation on asset from API

def commodity_info(ticker, data, Price):
    Circulating_Supply = circulating_supplys[ticker]
    if 'previousClose' in data.info:
        previous_close = data.info['previousClose']
    else:
        previous_close = Price
    change24hr = ((Price - previous_close) / previous_close) *100
    Marketcap = Price * Circulating_Supply
    logo_url = 'static/icons/'+ticker.lower()+'.png'
    logo_html = '<img src='+logo_url+' width="40" height="40">'
    volume24hr = 0.0
    
    return (Price, change24hr, Marketcap, logo_url, logo_html, volume24hr)

def currency_info(ticker, data, price):
    Circulating_Supply = circulating_supplys[ticker[:3]]    
    exch_rate = price
    exch_rate = float(price)
    Price = exch_rate
    if 'previousClose' in data.info:
        previous_close = data.info['previousClose']
    else:
        previous_close = Price
    change24hr = ((Price - previous_close) / previous_close) *100
    Marketcap = Circulating_Supply / (1/Price)
    logo_url = 'static/icons/flags/'+ticker[:2].lower()+'.png'
    logo_html = '<img src='+logo_url+' width="40" height="30">'
    volume24hr = 0.0
    
    return (Price, change24hr, Marketcap, logo_url, logo_html, volume24hr)

def get_asset_info(ticker):
    
    for i in range(1,4):
        print('%s Attempt A: %s'%(ticker, i))
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="5d", interval = "5m")
            Price = float(hist.iloc[-2 : -1]['Open'])
            return data, Price
        except:
            continue
 
    else:
        for j in range(1,4):
            print('%s Attempt B: %s'%(ticker, j))
            try:
                data = yf.Ticker(ticker)                
                Price = data.info['regularMarketPrice']
                if Price is None:
                    continue
                return data, Price
            except:
                continue
        else:
            return None, None
                
def real_estate():
        
        # 2017 value + 5% inflation https://www.savills.com/blog/article/216300/residential-property/how-much-is-the-world-worth.aspx
        today = pd.Timestamp.today().date()
        old_date = pd.Timestamp('2017/04/10').date()
        price_old_date = 282000000000000.0 
        days_lapsed = today - old_date
        days_lapsed = days_lapsed.total_seconds() / (24*60*60)
        inflation_per_day = 1.05**(1/365.25)
        mulitplier = inflation_per_day**days_lapsed # consider 5% inflation
        
        Circulating_Supply = circulating_supplys['Houses']
        Marketcap = price_old_date * mulitplier 
        Price = Marketcap / Circulating_Supply
        change24hr = (inflation_per_day - 1.0) * 100.0
        logo_url = 'static/icons/real-est.png'
        logo_html = '<img src='+logo_url+' width="40" height="40">'
        volume24hr = 0.0
        
        return (Price, change24hr, Marketcap, logo_url, logo_html, volume24hr)

def Get_Info(asset):
    
    # Get asset infomation from yfinance API
    index = all_assets.index(asset)
    asset_type = asset[0]
    ticker = asset[1][1]
    Name = asset[1][2]
    
    labels = ['index',
              'Logo', 
              'Name', 
              'Ticker', 
              'Asset Type', 
              'Price',                                                                
              '24Hr Change', 
              'Volume 24Hr', 
              'Circulating Supply',
              'Market Cap']
    
    df1 = pd.DataFrame([["",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""]], columns=labels)
    
    
    if ticker != 'Real-Est':
        data, Price = get_asset_info(ticker)
        if data is None:
            return None
        

    
    if asset_type == 'Currency' and ticker !='USD':
        Price, change24hr, Marketcap, logo_url, logo_html, volume24hr = \
            currency_info(ticker, data, Price)
            
    elif asset_type == 'Currency' and ticker =='USD':
        Circulating_Supply = circulating_supplys['USD']
        Marketcap = Circulating_Supply
        Price = 1.0
        change24hr = 0.0
        logo_url = 'static/icons/usd.png'
        logo_html = '<img src='+logo_url+' width="40" height="40">'
        volume24hr = 0.0
            
    
    elif asset_type == 'Commodity':
        if ticker != "Real-Est":
            Price, change24hr, Marketcap, logo_url, logo_html, volume24hr = \
                        commodity_info(ticker, data, Price)
            
        else:
            Price, change24hr, Marketcap, logo_url, logo_html, volume24hr =\
                                                            real_estate()
                            
    else:
        
        if asset_type == 'Cryptocurrency':
            currency = 'USD'
        else:
            while True:
                if 'currency' in data.info and data.info['currency'] is not None:
                    currency = data.info['currency']
                    break
                elif 'toCurrency' in data.info and data.info['toCurrency'] is not None:
                    currency = data.info['toCurrency']
                    break
                elif 'financialCurrency' in data.info and data.info['financialCurrency'] is not None:
                    currency = data.info['financialCurrency']
                    break
                else:
                    print('Couldnt find currency or toCurrency')
                    return None
            
        if 'previousClose' in data.info and data.info['previousClose'] is not None:
            previous_close = data.info['previousClose']
        elif 'regularMarketPreviousClose' in data.info and data.info['regularMarketPreviousClose'] is not None:
            previous_close = data.info['regularMarketPreviousClose']
        else:
            previous_close = Price
            
        change24hr = ((Price - previous_close) / previous_close) *100
            
        # Apply exchange rate for non USD assets
        if currency != 'USD':
            currency_ticker = currency.upper()+'USD=X'
            if currency_ticker in df['Ticker'].values:
                for i, value in enumerate(df['Ticker'].values):
                    if currency_ticker == value:
                        exch_rate = float(df['Price'][i])                        
                        break
                    
            else:
                price = get_asset_info(currency_ticker)[1]
                exch_rate = float(price)
            
            if currency[-1].islower():
                Price/=100.0
                
        else:
            exch_rate = 1.0
            
        
        if 'volume24Hr' in data.info and data.info['volume24Hr'] is not None:
            volume24hr = float(data.info['volume24Hr'])
        elif 'volume' in data.info and data.info['volume'] is not None:
            volume24hr = float(data.info['volume']) * Price
        else:
            volume24hr = 0.0
            
        if 'circulatingSupply' in data.info and data.info['circulatingSupply'] is not None:
            Circulating_Supply = float(data.info['circulatingSupply'])
            Marketcap = (Circulating_Supply * Price) * exch_rate
        else:
            if 'marketCap' in data.info and data.info['marketCap'] is not None:
                Marketcap = float(data.info['marketCap']) * exch_rate
                Circulating_Supply = (Marketcap / (Price * exch_rate)) 
            else:
                print(data.info['circulatingSupply'])
                print(data.info['marketCap'])
                print('Failed circ and mc')
                Circulating_Supply = 0.0
                Marketcap = 0.0
        
        logo_url = data.info['logo_url']
        
        if len(logo_url) < 1:        
            if "=" in ticker:
                logo_url= 'static/icons/'+ticker.lower()+'.png'                
            else:
                logo_url= 'static/icons/'+ticker[:-4].lower()+'.png'
            
        logo_html = '<img src='+logo_url+' width="40" height="40">'
        
        Price *= exch_rate  
    
    if asset_type != 'Cryptocurrency':        
        Circulating_Supply = Marketcap / Price
        
        
    # Find missing logo images
    if ticker in ['GOOGL','BAC','HD','PG','TMUS','2222.SR', 'FB', 'BRK-A', 'BABA']:    
        logo_url = Get_Broken_Images(ticker)   
        logo_html = '<img src='+logo_url+' width="40" height="40">'
    
    # Reduce height of some images    
    if ticker in ['GOOGL', 'MA', 'PYPL', 'ADBE', 'BARC.L', 'AV.L', 'ANTO.L',
                  'IAG.L', 'CCH.L', 'BABA', 'AXP']:
        logo_html = '<img src='+logo_url+' width="40" height="20">'
        
    if asset_type == 'Cryptocurrency':
        Name = Name[:-4] # remove the USD at end of name


    change24Hr_html = format_price_change(change24hr)
    
    # Create dataframe of asset
    dataframe1 = pd.DataFrame([[index,
                                logo_html,
                                Name,
                                ticker,                                  
                                asset_type,
                                Price,
                                change24Hr_html,
                                volume24hr,
                                Circulating_Supply,
                                Marketcap]], columns=labels)
    
    # Append to the main dataframe
    df1 = df1.append(dataframe1, ignore_index=True)  
    df1 = df1.iloc[1:]
    df.reset_index(inplace=True, drop=True)
    return df1


# def main():
# Collate assets   
for asset in assets:
    a = read_asset_lists(asset)
    for i in a:
        all_assets.append(i)

            
for i in all_assets:
    if i[0] == 'Currency':
        ticker = i[1][1]
        area_code = i[1][3]
        circulating_supplys[ticker[:3]] = get_currency_supplies(area_code)


df = pd.DataFrame()



# Multithread each request
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = [executor.submit(wrapper, all_assets[i]) for i in range(len(all_assets))]
    
    for f in concurrent.futures.as_completed(results):
        if f.result() is not None:
            df = df.append(f.result())
            
# #single procesing for debugging
# for i in all_assets:
#     df = df.append(wrapper(i))

# Sort table by market cap    
df = df.sort_values('Market Cap', ascending=False)

# remove indices
df = df.drop('Ticker', 1)
df = df.drop('index', 1)

# Remove duplicate entry    
df = df[~df['Name'].isin(['Alphabet Inc. Class C Capital Stock'])]

# Cleanup
df['Name'] = df['Name'].apply(lambda x: x.replace("Common Stock", ""))
df['Name'] = df['Name'].apply(lambda x: x.replace("Class A", ""))
df['Name'] = df['Name'].apply(lambda x: x.replace("Class B", ""))
df['Name'] = df['Name'].apply(lambda x: x.replace("Class C", ""))
df['Name'] = df['Name'].apply(lambda x: x.replace("Ordinary Shares", ""))
df['Name'] = df['Name'].apply(lambda x: x.replace("Ordinary Share", ""))
df['Name'] = df['Name'].apply(lambda x: x.replace("(Each representing 1 Common Share)", ""))
df['Name'] = df['Name'].apply(lambda x: x.replace("American Depositary Shares", ""))
df['Name'] = df['Name'].apply(lambda x: x.replace("each representing eight Ordinary share", ""))

#Insert ranking column
df.insert(0, "Rank", range(1, len(df) + 1))

df.to_pickle(server_path+'database.pkl')

# if __name__ == "__main__":
#     main()
