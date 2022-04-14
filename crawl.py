# import du lieu
from os import pipe
from pickle import TRUE
import sys
from h11 import Data
from requests.api import request 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import re

import requests
import bs4
from bs4 import BeautifulSoup
import json



from sklearn.covariance import ledoit_wolf_shrinkage

# Option
sys.path.insert(0,'/Users/haonguyen/PycharmProjects/selenium_py/chromedriver')

# https://peter.sh/experiments/chromium-command-line-switches/
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless') 

chrome_options.add_argument('--no-sandbox') 
chrome_options.add_argument('--disable-dev-shm-usage') 



chrome_driver = webdriver.Chrome()

# BASE_URL: URL cở sở
BASE_URL = 'https://tiki.vn/bo-suu-tap/sa-gia-dung-nen-mua-b7319'


# Open website
chrome_driver.get(BASE_URL)

SCROLL_PAUSE_TIME = 0.5

# Get scroll height
last_height = chrome_driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    chrome_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    sleep(SCROLL_PAUSE_TIME)

    # if new scroll height = compare with last scroll height then break
    new_height = chrome_driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

#chrome_driver.maximize_window()


sleep(3)


# bs4 for source page
soup = BeautifulSoup(chrome_driver.page_source, 'lxml')


# Get link of items
link_items_list = []
for link in soup.select('div.styles__RowsLayoutContainer-sc-rn1g9v-1.lfjbto a[href]'):
    link_items_list.append(link['href'])

#print(link_items_list)

# Get items id in list products
p_id_list = []
sp_id_list = []
for i in range(len(link_items_list)):
    txt = link_items_list[i]
    p_id = re.findall("[0-9]*.html", txt)
    sp_id = re.findall("spid=\d*", txt)
    if p_id:
        p_id = re.sub("\D","", p_id[0])
        p_id_list.append(p_id)
    
    if sp_id:
        sp_id = re.sub("spid=","", sp_id[0])
        sp_id_list.append(sp_id)
    
#print(p_id_list)
#print(sp_id_list)

print(len(p_id_list))
print(len(sp_id_list))

total_comments = 0
#crawling comments
comment_list = []
def crawling_cmt(url):    
    header = {'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Safari/537.36"}
    response = requests.get(url,headers=header)
    data = response.json()
    if len(data) > 0:
        data = data['data']
        for i in range(len(data)):
            # get content vs rating in data           
            comment_list.append({"name":data[i]['created_by']['name'],"comment":data[i]['content'],"rating":data[i]['rating']})
    else:
        print("data:",data)
            
    print("Crawled:", len(data) , "comments for", p_id)

# duyệt qua các items
for i in range(len(p_id_list)):
    p_id = p_id_list[i]
    sp_id = sp_id_list[i]
    print("Crawling p_id:", p_id,"sp_id", sp_id)
    api_url = f"https://tiki.vn/api/v2/reviews?limit=1000&include=comments,contribute_info&sort=score%7Cdesc,id%7Cdesc,stars%7Call&page=1&spid={sp_id}&product_id={p_id}"
    crawling_cmt(api_url)

print("Tong số Comments: ",len(comment_list))

# Save to json
#with open('do_dung_nen_mua_tiki_crawled_ensure_ascii.json', 'w',  encoding='utf-8') as file:
    #json.dump(comment_list, file)

chrome_driver.close()
