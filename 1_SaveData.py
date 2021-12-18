from flask import Flask
import yfinance as yf
import pandas as pd
import csv
import concurrent.futures

multiThreading = True

app = Flask(__name__)

# if runing locally no need to include server path, if running on server however full path required
server_path = ''
server_path = '/var/www/webApp/webApp/' # comment this out if running locally

# # Define which assets to work with
# crypto_file = "Yahoo_Cryptos.csv"

# def delete_empty_rows(file_path, new_file_path):
#     data = pd.read_csv(file_path, skip_blank_lines=True)
#     data.dropna(how="all", inplace=True)
#     data.to_csv(new_file_path, header=True)

# delete_empty_rows(crypto_file, crypto_file[:-4]+"_filtered.csv")
assetLists = "assetlists/"
cryptos = ["Cryptocurrency", server_path+assetLists+"Yahoo_Cryptos_filtered.csv"] # https://finance.yahoo.com/cryptocurrencies/?&offset=0&count=200
# sp100 = ["US Stock", server_path+"S&P100-Info.csv"]
NASDAQ = ["US Stock", server_path+assetLists+"NASDAQ_Shortlist.csv"]
NYSE = ["US Stock", server_path+assetLists+"NYSE_Shortlist.csv"]
FTSE100 = ["UK Stock", server_path+assetLists+"FTSE100-Info.csv"]
commodities = ["Commodity", server_path+assetLists+"Commodities.csv"]
Other_Companies = ["Saudi Stock", server_path+assetLists+"BigCompanies.csv"]
currencies = ["Currency", server_path+assetLists+"Currencies.csv"]
 
#   currencies, NASDAQ, NYSE, FTSE100, commodities, Other_Companies, cryptos
assets = [currencies, NASDAQ, NYSE, FTSE100, commodities, Other_Companies, cryptos]
all_assets = []

df = pd.DataFrame()

# def main():

class assetClass():
    
    # Keep track of totals
    total = 0 #class Attribute
    
        
    def __init__(self, inputData):
        
        self.name = inputData['Name']
        self.type = inputData['Type']
        self.ticker = inputData['Ticker']
        self.data = self.getData(self.ticker)
        self.currency = self.getCurrency()
        self.exchangeRate = self.exchangeRate()
        if self.exchangeRate is not None and self.exchangeRate != 0.0:
            self.price = self.getPrice(self.data) * self.exchangeRate
        else: 
            self.price = self.getPrice(self.data)
        self.volume24hr = self.getVolume24Hr(self.data)
        self.change24hr = self.change24Hr_html()
        self.logo = self.getLogo()
        
        assetClass.total =+ 1       

        
    def getCurrency(self):
        return ("USD")
    
    def exchangeRate(self):
        return 1.0

    def getData(self, ticker):
        
        for i in range(1,4):
            try:
                print('%s Attempt A: %s'%(ticker, i))
                data = yf.Ticker(ticker)
                if data is not None:
                    return data
                else:
                    raise ValueError('Data is None.')
            except:
                continue
            
        else:
            return None
    
                
    def getPrice(self, data):
        
        if self.ticker == 'USD':
            return 1.0

        try:
            hist = data.history(period="5d", interval = "5m")
            price = float(hist.iloc[-2 : -1]['Open'])
            if price is not None:
                return price
            else:
                raise ValueError('Price is None.')
            
        except:
            try:
                price = data.info['regularMarketPrice']
                if price is not None:
                    return price
                else:
                    raise ValueError('Price is None.')
            except:
                return 0.0


    def getLogo(self):
        
        logo_url = self.data.info['logo_url']
        
        if len(logo_url) < 1:        
            if "=" in self.ticker:
                logo_url= 'static/icons/'+self.ticker.lower()+'.png'                
            else:
                logo_url= 'static/icons/'+self.ticker[:-4].lower()+'.png'
            
        
        if self.ticker == 'GOOGL':
           logo_url = "static/icons/google.png"
        
        if self.ticker == 'FB':
           logo_url = "/static/icons/facebook.png"
            
        if self.ticker == 'BAC':
           logo_url = "/static/icons/Bank-of-America.png"
            
        if self.ticker == 'HD':
           logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/TheHomeDepot.svg/360px-TheHomeDepot.svg.png"
    
        if self.ticker == 'PG':
           logo_url = "/static/icons/Procter_Gamble.png"
         
        if self.ticker == 'TMUS':
           logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Telekom_Logo_2013.svg/440px-Telekom_Logo_2013.svg.png"
    
        if self.ticker == '2222.SR':
           logo_url = "/static/icons/saudi_aramco.png"
    
        if self.ticker == 'BABA':
           logo_url = "/static/icons/Alibaba-Group.png"
    
        if self.ticker == 'BRK-A':
           logo_url = "/static/icons/brk-a.png"
       
        logo_html = '<img src='+logo_url+' width="40" height="40">'

    
        return logo_html
        

            
    # def getCiculatingSuppy(self, data):
        
    #     data.info['ciculatingSupply']
        
    def getVolume24Hr(self, data):    
        if 'volume24Hr' in data.info and data.info['volume24Hr'] is not None:
            volume24hr = float(data.info['volume24Hr'])
        elif 'volume' in data.info and data.info['volume'] is not None:
            volume24hr = float(data.info['volume']) * self.price
        else:
            volume24hr = 0.0
            
        return volume24hr
    
    def change24Hr(self):    
        
        if 'previousClose' in self.data.info:
            previous_close = self.data.info['previousClose']
        else:
            previous_close = self.price
            
        if previous_close > 0:            
            change24hr = ((self.price - previous_close) / previous_close) *100
        else:
            change24hr = 0.0
        
        return change24hr
    
    def change24Hr_html(self):
        # colour the 24hr price change red or green
        change24hr = self.change24Hr()
        if change24hr >= 0:
            change24hr = '{:.2f}%'.format(change24hr)    
            change24Hr_html = '<p style="color: green; text-align:center; "> '+change24hr+ ' </p>'
        else:
            change24hr = '{:.2f}%'.format(change24hr)
            change24Hr_html = '<p style="color: red; text-align:center; "> '+change24hr+ ' </p>'
            
        return change24Hr_html
        
    def as_dict(self):
        
        return {'Name': self.name, 
                'Asset Type': self.type, 
                'Ticker': self.ticker,
                'Price': self.price,
                'Currency': self.currency,
                'Market Cap': self.marketCap,
                'Circulating Supply': self.circulatingSupply,
                'Volume 24Hr': self.volume24hr,
                '24Hr Change': self.change24hr,
                'Logo': self.logo}
            

            
class stock(assetClass): #inherit from the defineAsset class

    total = 0  #class attribute
    
    def __init__(self, inputData):
        super().__init__(inputData) # used for extra variables to input i.e. country
        self.circulatingSupply = self.getCirculatingSupply(self.data)
        
        stock.total += 1
        
    def getCirculatingSupply(self, data):
        if 'sharesOutstanding' in data.info:
            circulatingSupply = data.info['sharesOutstanding']
            if circulatingSupply is not None:
                return circulatingSupply
            else:
                return 0.0
        else:        
            return 0.0
        
    def getCurrency(self):
        
        data = self.data
    

        if 'currency' in data.info and data.info['currency'] is not None:
            return data.info['currency']
        elif 'toCurrency' in data.info and data.info['toCurrency'] is not None:
            return data.info['toCurrency']
        elif 'financialCurrency' in data.info and data.info['financialCurrency'] is not None:
            return data.info['financialCurrency']
        
        else:
            print('Couldnt find currency or toCurrency, assuming USD')
            return 'USD'
            
    def exchangeRate(self):
        
        
        currency = self.currency            
        # Apply exchange rate for non USD assets
        if currency is not None:
            currency_ticker = currency.upper()+'USD=X'
        else:
            currency_ticker = 'USD'
        
        try:
            for index, value in enumerate(df['Ticker']):
                if currency_ticker == value:
                    exch_rate = df['Price'][index]
                    break
                else:
                    
                    exch_rate = 1.0
        except:
            exch_rate = 1.0


        if currency is not None and currency[-1].islower():
            exch_rate /= 100.0
            
        return exch_rate         

        

class currency(assetClass):
    
    total = 0  #class attribute
    
    def __init__(self, inputData):
        super().__init__(inputData) # used for extra variables to input i.e. country
        self.country = self.getCountry(inputData)
        self.circulatingSupply = self.getCirculatingSupply(self.country)
        
        currency.total +=1

    def getCountry(self, inputData):
        if 'CountryCode' in inputData:
            return inputData['CountryCode']
        else:
            return None
    
    def getCirculatingSupply(self, country):
        
       
        m2_m3 = "m2"
        
        
        # australia has no m2 so using m3
        if country == "australia":
            m2_m3 = "m3"
        
        for i in range(1,4):
            try:
                print ("Getting Circulating Supply of %s, Attempt: %s" %(country, i))
                tables = pd.read_html('https://tradingeconomics.com/%s/money-supply-%s' %(country,m2_m3))
                break
            except:        
                print('exception')
                continue


        else:
            return 0.0
        
        for table in tables:
            
            
            if 'Last' in table:
                df = table
                # print(table)
                filter_m2 = df.apply(lambda row: row.astype(str).str.contains(m2_m3.upper()).any(), axis=1)
                df = df.loc[filter_m2]
                m2_supply = float(df['Last'])
                m2_unit = str(df['Unit'])
                break
    
            else:
                m2_supply = 0.0
                m2_unit = 0.0
                
                    
        if 'Million' in m2_unit:
            m2_supply*= 1e6
        elif 'Billion' in m2_unit:
            m2_supply*= 1e9
                        
        return m2_supply
    
    def getLogo(self):
        
        logo_url = 'static/icons/flags/'+self.ticker[:2].lower()+'.png'
        logo_html = '<img src='+logo_url+' width="40" height="30">' 

        return logo_html  
    
class cryptocurrency(assetClass):
    
    total = 0  #class attribute   
    
    def __init__(self, inputData):
        super().__init__(inputData)
        self.circulatingSupply = self.getCirculatingSupply(self.data)     
        
        cryptocurrency.total += 1                
        
    def getCirculatingSupply(self, data):
        if 'circulatingSupply' in data.info:
            return data.info['circulatingSupply']
        else:        
            return 0.0
    

class commodity(assetClass):
    
    Total = 0  #class attribute
    
    def __init__(self, inputData):
        super().__init__(inputData)
        self.circulatingSupply = self.getCirculatingSupply(self.data)
        
        commodity.Total += 1
        
        if self.name == 'Real Estate':

            self.marketCap = self.getRealEstateMarketCap()  
            self.price = self.marketCap / self.circulatingSupply
        

    def getRealEstateMarketCap(self):
        
        today = pd.Timestamp.today().date()
        old_date = pd.Timestamp('2017/04/10').date()
        price_old_date = 282000000000000.0 
        days_lapsed = today - old_date
        days_lapsed = days_lapsed.total_seconds() / (24*60*60)
        inflation_per_day = 1.05**(1/365.25)
        mulitplier = inflation_per_day**days_lapsed # consider 5% inflation
        price = price_old_date * mulitplier
        return price
 


    def getCirculatingSupply(self, data):

        if self.name == 'Real Estate':
            table=pd.read_html('https://en.wikipedia.org/wiki/List_of_countries_by_number_of_households')
            df_houses = table[1]
            return df_houses['Households'].sum()
        
        if self.name == 'Oil':
            table=pd.read_html('https://en.wikipedia.org/wiki/List_of_countries_by_proven_oil_reserves')
            df_oil = table[0]
            return df_oil.iloc[:, [2]].sum()[0] * 1000000000
        
        if self.name == 'Natural Gas':
            table=pd.read_html('https://en.wikipedia.org/wiki/List_of_countries_by_natural_gas_proven_reserves')
            df_gas = table[1]
            return (df_gas.iloc[:, [2]].sum()[0] * (1000 * 1000 * 1000) * 35.3147) / 1000 # price is per thousand cubic feet
        
        # need to find weblinks to these
        
        troy_oz = 31.1034768
        if self.name == 'Gold':
            return (201296*1000*1000) / troy_oz   # Gold https://www.gold.org/goldhub/data/above-ground-stocks
        if self.name == 'Silver':
            return (1751000*1000*1000) / troy_oz   # Silver
        if self.name == 'Platinum':
            return (10000*1000*1000) / troy_oz # Platinum
        if self.name == 'Palladium':
            return (20*1000*1000) / troy_oz # Palladium
        
    def getLogo(self):
    
        if self.ticker != 'Real-Est':
            logo_url = 'static/icons/'+self.ticker.lower()+'.png'
        else:
            logo_url = r'static/icons/real-est.png'
            
        logo_html = '<img src='+logo_url+' width="40" height="40">'
            
        return logo_html
        


def getStockData():
    # Get list of S&P100 Ticker from wikipedia
    table=pd.read_html('https://en.wikipedia.org/wiki/S%26P_100')
    df = table[2]
    df['Symbol'] = df['Symbol'].apply(lambda x: x.replace(".", "-"))
    df = df.rename(columns={"Symbol":"Ticker"})
    df.to_csv(server_path+assetLists+'S&P100-Info.csv')
    
    
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
    
    df = df.rename(columns={"EPIC": "Ticker",
                            "Company": "Name"})
    
    df.to_csv(server_path+assetLists+'FTSE100-Info.csv')

def read_asset_lists(inputData):    
    
    assetType = inputData[0]
    csv_file = inputData[1]

    def import_file(filename):
        with open(filename, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['Type'] = assetType
                yield row
                
    mydict = import_file(csv_file)
    
    listofDicts = list(mydict)
    
    return listofDicts


def get_Assets(asset):
        
    if asset['Type'] == 'Currency':
        output = currency(asset)
    if 'Stock' in asset['Type']:
        output = stock(asset)
    if asset['Type'] == 'Cryptocurrency':
        output = cryptocurrency(asset)
    if asset['Type'] == 'Commodity':
        output = commodity(asset)
    
    if output.price is not None and output.circulatingSupply is not None:
        output.marketCap = output.price * output.circulatingSupply
    else:
        output.marketCap = 0.0
    
    # if output.exchangeRate != 0.0:
    #     output.price = output.price * output.exchangeRate
    # else:
    #     output.price = 0.0

    return output.as_dict()


# if __name__ == '__main__':
#     main()
    
# Collate assets   
for asset in assets:
    a = read_asset_lists(asset)
    for i in a:
        all_assets.append(i)

getStockData()

df = pd.DataFrame()
    
if multiThreading is True:
    print ('MultiThreading')
    # Multithread each request
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(get_Assets, all_assets[i]) for i in range(len(all_assets))]
        
        for f in concurrent.futures.as_completed(results):
            if f.result() is not None:
                df = df.append(f.result(), ignore_index=True)
else:
    pass
    print ('Single Threading')
    # single procesing for debugging
    for i in all_assets:
        df = df.append(get_Assets(i), ignore_index=True)
    
    # df = pd.DataFrame([x.as_dict() for x in listOfAssets])

# Sort table by market cap    
df = df.sort_values('Market Cap', ascending=False)


# remove indices
df = df.drop('Ticker', 1)
df.reset_index(drop=True, inplace=True)

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
    