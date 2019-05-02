# =============================================================================
# Milestone 4
# =============================================================================
from twitterscraper import query_tweets
import datetime as dt
import pandas as pd
from langdetect import detect
import matplotlib.pyplot as plt
import seaborn as sns
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
# =============================================================================
# Part 1: Crawl tweets
# =============================================================================

#crawl tweets within this time period
begin_date = dt.datetime.strptime("Jan 01 2019", "%b %d %Y").date()
end_date = dt.datetime.strptime("Apr 01 2019", "%b %d %Y").date()
#to obtain keywords to crawl tweets
data = pd.ExcelFile('stock60_final.xlsx')
df = data.parse('stock60')

#convert to list form
stockfilter = df['filters'].tolist();print(stockfilter)

#crawl loop function
tweets = []
filters = []
jsonlist=[]

for i in stockfilter:
    t = query_tweets(i,begindate=begin_date,enddate=end_date,lang='en',limit=400)
    for j in t:
        jsonlist.append(vars(j)) 
    size = len(t)
    if size >0:
        for m in range(size):
            filters.append(i)
    print("done for "+i)
    break #remove break to crawl full tweet

df1 = pd.DataFrame({'filters':filters})
df2 = pd.DataFrame(jsonlist)
df3 = pd.concat([df1,df2],axis=1) 
df3.to_csv('tweetsstock60.csv')

# =============================================================================
# Part 2: Pre-processing & Sentiment polarity
# =============================================================================
tweetsdf = pd.read_csv('tweetsstock60.csv',index_col = 0)
tweetsdf.columns
tweetsdf.info()
tweetsdf.head()

#1. a second process to filter out non-english tweets
tweetsdf['text'] = tweetsdf['text'].astype(str)
tweetsdf['lang'] = tweetsdf['text'].map(lambda x: detect(x)) #takes awhile to process
tweetsdf = tweetsdf[tweetsdf['lang']=='en']

#2. Generate sentiment analysis
analyzer = SentimentIntensityAnalyzer()
sentiment = tweetsdf['text'].apply(lambda x: analyzer.polarity_scores(x)) 
df4 = pd.concat([tweetsdf,sentiment.apply(pd.Series)],1)
df4.info()
df4.describe()

#3. save to csv
df4.to_csv('sentisstock60.csv',encoding='utf-8',index=False)


#4. Identify sentiment
senti60 = pd.read_csv('sentisstock60.csv')
#senti60 = pd.read_csv('sentisstock60.csv')
senti60.info()
senti60 = senti60.dropna() #drop missing values
senti60['timestamp']=pd.to_datetime(senti60['timestamp']) #update date format
senti60.sort_values(by='timestamp', inplace=True)
senti60.index = pd.to_datetime(senti60['timestamp']) #create index based on timestamp
senti60['mean'] = senti60['compound'].expanding().mean() #overall mean
senti60['rolling'] = senti60['compound'].rolling('12h').mean() #compute rolling mean for window size=12
senti60['summary'] = senti60['compound'].apply(lambda x: (x>0 and 'Positive') or (x<0 and 'Negative') or 'Neutral')
#save as new dataset
senti60.to_csv('senti60.csv',index=True)

# =============================================================================
# Part 3: Visualization & interpretation
# =============================================================================

#1. visualize total number of tweets by stock
tottweets = senti60.groupby('filters')['compound'].count().reset_index(name = 'Count')
print(tottweets)
fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
sns.distplot(tottweets['Count'], bins=20, ax=ax, color = '#FF5CCE')
plt.show()

#2. visualize top 50 tweeted stocks
sorttop50 = tottweets.sort_values('Count')[0:50]
print(sorttop50)
my_range=range(1,len(sorttop50.index)+1)
fig = plt.figure(figsize=(5,25))
plt.hlines(y=my_range, xmin=0, xmax=sorttop50['Count'], color='skyblue')
plt.plot(sorttop50['Count'], my_range, "o")
plt.yticks(my_range, sorttop50['filters'])
plt.title("A vertical lolipop plot", loc='left')
plt.xlabel('Total tweets: Top 50 stocks')
plt.ylabel('Stock filters')

#3. visualize top 10 tweeted stocks by sentiment polarity

totsent = senti60.groupby(['filters','summary'])['summary'].count().reset_index(name = 'Count')
totsentV = senti60.groupby(['filters','summary'])['summary'].count().unstack().fillna(0).sort_values(['Negative','Positive'],ascending=[False,False])
top10sent = pd.DataFrame(totsentV[0:10])

fig = plt.figure(figsize=(20,6.5))
barWidth = 0.25
r1 = np.arange(len(top10sent))
r2 = [x + barWidth for x in r1]
r3 = [x + barWidth for x in r2]
tick_pos = [i + (barWidth / 2) for i in r1]
name = top10sent.index
# Make the plot
plt.bar(r1, top10sent.Positive, color='#8CF4F7', width=barWidth, edgecolor='white', label='positive')
plt.bar(r2, top10sent.Neutral, color='#A4FECE', width=barWidth, edgecolor='white', label='neutral')
plt.bar(r3, top10sent.Negative, color='#FEBDAD', width=barWidth, edgecolor='white', label='negative')
# Add xticks on the middle of the group bars
plt.xlabel('Filtered Stock Names', fontweight='bold')
plt.xticks(tick_pos,name, fontsize=12,rotation=35)
plt.title('Stock: Top 10 Tweets by Sentiment Polarity Counts',fontsize=16)
plt.legend()
plt.show()

#4. Plot time series, overal tweeted sentiment, average & rolling average

senti60['date'] = senti60.timestamp.apply(lambda x: x.strftime('%Y-%m-%d'))
startdate='2019-01-01'
enddate='2019-04-01'

fig = plt.figure(figsize=(16,15))
ax = fig.add_subplot(111)
ax.scatter(senti60['date'],senti60['compound'], label='Tweet Sentiment',color = '#8CF4F7')
ax.plot(senti60['date'],senti60['rolling'], color ='#15DE1C', label='Rolling Mean')
ax.plot(senti60['date'],senti60['mean'], color='#C315DE', label='Expanding Mean')
fig.autofmt_xdate()
#ax.set_xlim([dt.date(2019,1,1),dt.date(2019,4,1)])
ax.set_xlim([startdate,enddate])
ax.set(title='Stock Related Tweets over Time', xlabel='Date', ylabel='Sentiment')
ax.legend(loc='best')
fig.tight_layout()
plt.show()#;fig.savefig('timeseries.png')

#5.plot distribution of sentiment
fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
sns.distplot(senti60['compound'], bins=15, ax=ax,color = '#37E6AB')
plt.title("Overall Distribution of Sentiment Scores", loc='left')
plt.show()








