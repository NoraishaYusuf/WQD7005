from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from lxml import html
import requests
from bs4 import BeautifulSoup
import string
import re
import os
import mysql.connector
import datetime

##############################
#   CRAWLING STOCK INFO
##############################
print("!!! START CRAWLING STOCK INFO")
urlTheStar='https://www.thestar.com.my/business/marketwatch/stock-list/?alphabet='
alpha = []
for letter in string.ascii_uppercase:
    alpha.append(letter)     
alpha.append('0-9')
print("!!!  Array of chars")
print(alpha)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="datamining"
)
mycursor = mydb.cursor()
print("!!!  Connected to db")


for i in alpha:
    print("!!!  Now char "+ i)
    browser = webdriver.Firefox(executable_path=r'C:\geckodriver.exe')
    browser.get(urlTheStar + i)
    innerHTML = browser.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(innerHTML, 'lxml')
    stock_table = soup.find('table',{'class':'market-trans'})
    links = stock_table.findAll('a')

    company = []
    for link in links:
        start_page = requests.get('https://www.thestar.com.my'+link.get('href'))
        tree = html.fromstring(start_page.text)
        
        url_link = 'https://www.thestar.com.my'+link.get('href')
        board = tree.xpath('//li[@class="f14"]/text()')[0]
        stock_code = tree.xpath('//li[@class="f14"]/text()')[1]
        name = tree.xpath('//h1[@class="stock-profile f16"]/text()')[0]
        w52high = tree.xpath('//li[@class="f14"]/text()')[2]
        w52low = tree.xpath('//li[@class="f14"]/text()')[3]
        updateDate = tree.xpath('//span[@id="slcontent_0_ileft_0_datetxt"]/text()')[0]
        updateTime = tree.xpath('//span[@class="time"]/text()')[0]
        open_price = tree.xpath('//td[@id="slcontent_0_ileft_0_lastdonetext"]/text()')[0]
        high_price = tree.xpath('//td[@id="slcontent_0_ileft_0_opentext"]/text()')[0]
        low_price = tree.xpath('//td[@id="slcontent_0_ileft_0_lowtext"]/text()')[0]
        last_price = tree.xpath('//td[@id="slcontent_0_ileft_0_lastdonetext"]/text()')[0]
        volume = tree.xpath('//*[@id="slcontent_0_ileft_0_voltext"]/text()')[0]
        buy_vol_hundred = tree.xpath('//*[@id="slcontent_0_ileft_0_buyvol"]/text()')[0]
        sell_vol_hundred = tree.xpath('//*[@id="slcontent_0_ileft_0_sellvol"]/text()')[0]
        date_crawl = str(datetime.datetime.now())
        
        print(url_link)
        print(board[3:])    # to remove the first 3 character in the string
        print(stock_code[3:])# to remove the first 3 character in the string
        print(w52high[3:])
        print(w52low[3:])
        print(name)
        print(updateDate[10:-2])
        print(updateTime)
        print(open_price)
        print(high_price)
        print(low_price)
        print(last_price)
        print(volume)
        print(buy_vol_hundred)
        print(sell_vol_hundred)

        sql = "INSERT INTO stock_test (url_link, board, stock_code, name, 52weekhigh, 52weeklow, date, time, open_price, high_price, low_price, last_price, volume, buy_price, sell_price, date_crawl) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val = (url_link, board[3:],stock_code[3:], name, w52high, w52low, updateDate[10:-2],updateTime,open_price,high_price,low_price,last_price, volume, buy_vol_hundred, sell_vol_hundred, date_crawl)
        mycursor.execute(sql, val)
        mydb.commit()

        print(mycursor.rowcount, "record inserted at " +str(datetime.datetime.now()))
        break;

    print("!!!  Done for char "+ i)    
    break;
    
    
    browser.quit()

##############################
#   CRAWLING NEWS
##############################
print("!!! START CRAWLING NEWS")
urlNews='https://klse.i3investor.com/jsp/newshl.jsp'
browser = webdriver.Firefox(executable_path=r'C:\geckodriver.exe')
browser.get(urlNews)
innerHTML = browser.execute_script('return document.body.innerHTML')
soup = BeautifulSoup(innerHTML, 'lxml')
date = soup.select('div > h3')
for a in date:
    print(" ")
    print(a.text)
    div = soup.find('h3', text=a.text).find_next_siblings('ul')[0]
    title = div.find_all('a') 
    for b in title:
        time_raw = b.find_next_siblings('span', {'class': 'graydate'})[0].text
        time = time_raw[3:].strip()
        dateInsert = str(datetime.datetime.now())
        tarikh = a.text
        tajuk = b.text
        penulis = None
        category = "news"        
        print(b.text)
        print(time)             
        
        sql = "INSERT INTO test_newsblog (date_crawl, date_publish, time_publish, title, author, category) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (dateInsert, tarikh, time, tajuk, penulis, category)
        mycursor.execute(sql, val)
        mydb.commit()

browser.quit()    

##############################
#   CRAWLING BLOGS
##############################
print("!!! START CRAWLING BLOG")
urlBlogs='https://klse.i3investor.com/jsp/blog/bloghl.jsp'
browser = webdriver.Firefox(executable_path=r"C:\geckodriver.exe")
browser.get(urlBlogs)
#page = requests.get(urlBlogs)
#soup = BeautifulSoup(page.text, 'html.parser')
innerHTML = browser.execute_script('return document.body.innerHTML')
soup = BeautifulSoup(innerHTML, 'lxml')
date = soup.find("div", {"id": "maincontent730"}).find_all('h3')
print(date)
for a in date:
    print(" ")
    data_ul = soup.find('h3', text=a.text).find_next_siblings('ul')[0]
    #data_li = data_ul.select('ul > li')
    data_li = data_ul.findAll('li')
    for b in data_li:
        title = b.find('a')
        author = b.find('span', {'class': 'comuid'})
        all_text = b.find('span', {'class': 'graydate'}).text
        child_text = b.find('span', {'class': 'comuid'}).text
        parent_text = all_text.replace(child_text, '')
        print(" ")      
        dateInsert = str(datetime.datetime.now())
        tarikh = a.text
        print(tarikh)
        tajuk = title.text
        print(tajuk)
        penulis = author.text
        print(penulis)
        category = "blog"
        time = parent_text[5:].strip()

        sql = "INSERT INTO test_newsblog (date_crawl, date_publish, time_publish, title, author, category) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (dateInsert, tarikh, time, tajuk, penulis, category)
        mycursor.execute(sql, val)
        mydb.commit()

    print("!!! END CRAWLING BLOG FOR TODAY")

    break;

browser.quit() 


##############################
#   CRAWLING Financial Statement
##############################
print("!!! START CRAWLING FINANCIAL DATA")

browser = webdriver.Firefox(executable_path=r'C:\geckodriver.exe')
browser.implicitly_wait(40)

Financialurl = 'https://klse.i3investor.com/financial/quarter/latest.jsp'
browser.get(Financialurl)

#to expand the "modify the visible columns i.e. checkboxes"
WebElementexpanded = browser.find_element_by_xpath("//*[@id='ui-accordion-financialResultTableColumnsDiv-header-0']/span")
WebElementexpanded.click()

# to ensure all checkboxes are checked 
allLinks = browser.find_elements_by_xpath('//input[@type="checkbox"]')
for link in allLinks:
    if link.is_selected():
        print('Checkbox already selected');
    else:
        link.click();
        print('Checkbox selected'); 

elm = browser.find_element_by_class_name('next')
tbl = browser.find_element_by_xpath('//*[@id="tablebody"]')
while True:
    element = WebDriverWait(browser, 100).until(lambda x: x.find_element_by_id('tablebody'))
    for row in tbl.find_elements_by_tag_name('tr'):
        data = row.find_elements_by_tag_name('td')
        file_row = []
        for datum in data:
            datum_text = datum.text
            file_row.append(datum_text)
        dateInsert = str(datetime.datetime.now())
        print(file_row)
        tpl = tuple(file_row)
        tpl = (dateInsert,)+tpl
        val = tpl
        mycursor = mydb.cursor()
        sql = "INSERT INTO test_financial (date_crawl, no, stock, annDate, fy, quarter, h, price, ch, percentage, revenue, pbt, np, NptoSh, dividend, networth, divpayout, npmargin, roe, rps, eps, dps, naps, QoY, YoY) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"      
        mycursor.execute(sql,val)
        mydb.commit()
    elm = browser.find_element_by_class_name('next')
    if 'ui-state-disabled' in elm.get_attribute('class'):
        break;
    elm.click()








