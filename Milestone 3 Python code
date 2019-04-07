# =============================================================================
# Milestone 3
# =============================================================================
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import string
import time
import matplotlib.pyplot as plt
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.piecewise import PiecewiseAggregateApproximation
from tslearn.piecewise import SymbolicAggregateApproximation, OneD_SymbolicAggregateApproximation


# =============================================================================
# Part 1:
# Crawling all the stockname from the star (only once)
# =============================================================================

urlTheStar='https://www.thestar.com.my/business/marketwatch/stock-list/?alphabet='
alpha = []
for letter in string.ascii_uppercase:
    alpha.append(letter)     
alpha.append('0-9')
print("!!!  Array of chars")
print(alpha)

stockname = []
for i in alpha:
    print("!!!  Now char "+ i)
    browser = webdriver.Firefox(executable_path=r'C:\Users\shash\Anaconda3\geckodriver.exe')
    browser.implicitly_wait(40)
    browser.get(urlTheStar + i)
    WebDriverWait(browser,40).until(EC.visibility_of_element_located((By.ID,'marketwatchtable')))
    innerHTML = browser.find_element_by_id("marketwatchtable").get_attribute("innerHTML")
    soup = BeautifulSoup(innerHTML, 'lxml') 
    links = soup.findAll('a')
    for link in links:
        splitlink = link['href'].split('=')
        stock = splitlink[1]
        stockname.append(stock)
        print(stock)
    browser.close()

dict = {'name':stockname}
df_stockname = pd.DataFrame(dict)
df_stockname.to_csv('stockname.csv')


# =============================================================================
# Part 2:
# Crawling historical prices (only once)
# =============================================================================

#using the stockname crawled and saved in csv. Then transform dataframe into list
df1 = pd.read_csv('stockname.csv',usecols=[1])
datanames = df1['name'].tolist()

sl=[];cl=[];ol=[];hl=[];ll=[];dl=[];vl=[];stocknames2=[]  

#set timeframe to crawl e.g. 3 months
startdate=str(1546343431) #date = Tuesday, January 1, 2019 7:50:31 PM
enddate=str(1554205831) #date = Tuesday, April 2, 2019 7:50:31 PM 

for name in datanames:
    url = 'https://charts.thestar.com.my/datafeed-udf/history?symbol='+name+'&resolution=D&from='+startdate+'&to='+enddate
    r = requests.get(url).json() 
    if r["s"] == "ok":
        stocknames2.append(name)
        for t in r["t"]:
            day=time.strftime("%Y-%m-%d",time.localtime(int(t)))
            dl.append(day)
            sl.append(name)
        for o in r["o"]:ol.append(o) #open price
        for c in r["c"]:cl.append(c) #closing price
        for h in r["h"]:hl.append(h) #high price
        for l in r["l"]:ll.append(l) #low price
        for v in r["v"]:vl.append(v) #volume
    print("Done for "+ name)
    #break       
    
df = pd.DataFrame({'name':sl,'day':dl,'close':cl,'open':ol,'high':hl,'low':ll,'volume':vl})
df.to_csv('price_df.csv')



# =============================================================================
# Part 3:
# Computing covariance and correlation matrix
# =============================================================================
df = pd.read_csv('price_df.csv',usecols=[i for i in range(7) if i != 0]);print(df)

# find the change in daily closing prices
df['dif'] = df.groupby('name')['close'].diff()
print(df)

#transpose data frame according to name, and indexing by date for closing prices only
df_transposed = df.set_index(['name','day']).close.unstack('name')
#compute stock daily return/change
df_return = df_transposed.pct_change()
print(df_return)
df_return['ASIAPAC-WB']
# create covariance matrix
df_return.cov()
# create correlation matrix
df_return.corr()


# variation of number of records per stock
groups = df.groupby(['name'])
groups.get_group('AIRPORT-C8') #only have 1
groups.get_group('3A') # have full records for 3 months

#for more meaningful covariance interpretation, we decided to filter stocks with 60 records or more
df_new = groups.filter(lambda x : len(x)>=60)
df_new.to_csv('stocks60.csv')
df_transposed1 = df_new.set_index(['name','day']).close.unstack('name')
df_return1 = df_transposed1.pct_change()
df_return1.cov()
df_return1.corr()


# function defined to compute top positive and negative correlation
#=================================================================================
def get_redundant_pairs(df):
    '''Get diagonal and lower triangular pairs of correlation matrix'''
    pairs_to_drop = set()
    cols = df.columns
    for i in range(0, df.shape[1]):
        for j in range(0, i+1):
            pairs_to_drop.add((cols[i], cols[j]))
    return pairs_to_drop

def get_top_pos_correlations(df, n):
    au_corr = df.corr().unstack()
    labels_to_drop = get_redundant_pairs(df)
    au_corr = au_corr.drop(labels=labels_to_drop).sort_values(ascending=False)
    return au_corr[0:n]

def get_top_neg_correlations(df, n):
    au_corr = df.corr().unstack()
    labels_to_drop = get_redundant_pairs(df)
    au_corr = au_corr.drop(labels=labels_to_drop).sort_values(ascending=True)
    return au_corr[0:n]
#=================================================================================
n = 10

#For top n positive correlated stocks
x = get_top_pos_correlations(df_return, n)
y = get_top_pos_correlations(df_return1, n)

print("Top %d Positive Correlations" % n)
print("For different range of records: ");print(x)
print("Top %d Positive Correlations" % n)
print(" For stocks with >60 records: " );print(y)

#For top n negative correlated stocks
r = get_top_neg_correlations(df_return, n)
s = get_top_neg_correlations(df_return1, n)
    
print("Top %d Negative Correlations" % n)
print("For different range of records: ");print(r)
print("Top %d Negative Correlations" % n)
print(" For stocks with >60 records: " );print(s)



# =============================================================================
# Part 4:
# Normalising, PAA & SAX    
# =============================================================================
df_new = pd.read_csv('stocks60.csv',usecols=[i for i in range(8) if i != 0]);print(df_new)
#No. of companies with >60 records
listnew = df_new["name"].unique().tolist()
len(listnew)
df_red = df_new.set_index(['name','day']).dif.dropna()
print(df_red)

scaler = TimeSeriesScalerMeanVariance(mu=0., std=1.)  # Rescale time series
n_paa_segments = 10
n_sax_symbols = 10
n_sax_symbols_avg = 10
n_sax_symbols_slope = 6
for i in listnew:
    records = len(df_red[[i]])
    print("stockname"+str(i))      
    scaleddata = scaler.fit_transform(df_red[[i]])
    #print(scaleddata)      
    paa = PiecewiseAggregateApproximation(n_segments=n_paa_segments)
    paa_dataset_inv = paa.inverse_transform(paa.fit_transform(scaleddata))
    # SAX transform
    sax = SymbolicAggregateApproximation(n_segments=n_paa_segments, alphabet_size_avg=n_sax_symbols)
    sax_dataset_inv = sax.inverse_transform(sax.fit_transform(scaleddata))
    # 1d-SAX transform
    one_d_sax = OneD_SymbolicAggregateApproximation(n_segments=n_paa_segments, alphabet_size_avg=n_sax_symbols_avg,
                                                    alphabet_size_slope=n_sax_symbols_slope)
    one_d_sax_dataset_inv = one_d_sax.inverse_transform(one_d_sax.fit_transform(scaleddata))
    plt.figure()
    # First, raw time series
    plt.subplot(2, 2, 1)  
    plt.plot(scaleddata[0].ravel(), "b-")
    plt.title("Raw time series")
    # Second, PAA
    plt.subplot(2, 2, 2)  
    plt.plot(scaleddata[0].ravel(), "b-", alpha=0.4)
    plt.plot(paa_dataset_inv[0].ravel(), "b-")
    plt.title("PAA")
    #SAX plot
    plt.subplot(2, 2, 3)  # Then SAX
    plt.plot(scaleddata[0].ravel(), "b-", alpha=0.4)
    plt.plot(sax_dataset_inv[0].ravel(), "b-")
    plt.title("SAX, %d symbols" % n_sax_symbols)
    
    plt.subplot(2, 2, 4)  # Finally, 1d-SAX
    plt.plot(scaleddata[0].ravel(), "b-", alpha=0.4)
    plt.plot(one_d_sax_dataset_inv[0].ravel(), "b-")
    plt.title("1d-SAX, %d symbols (%dx%d)" % (n_sax_symbols_avg * n_sax_symbols_slope,
                                              n_sax_symbols_avg,
                                              n_sax_symbols_slope))

    plt.tight_layout()
    plt.suptitle('Stockname: ' + i)
    plt.show()


    #break
   

    




