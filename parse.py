# -*- coding: utf-8 -*-
import requests
import shutil
import urllib.request
from lxml import etree
from bs4 import BeautifulSoup
from lxml import html
from selenium import webdriver
from selenium.webdriver import ActionChains
import numpy as np
import os

def process_url(s: str)-> str:
    ind_under = s.rindex('_')
    ind_dot = s.rindex('.')
    s = s[:ind_under] + s[ind_dot:]
    s = s.replace('jpg', 'png')
    return s

def download_pictures(url: str, path: str)->bool:
    r = requests.get(url, stream = True)

    if r.status_code == 200:
        r.raw.decode_content = True
        
        with open(path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
            
        return True
    return False

FOLDER = '\\'.join(os.path.realpath(__file__).split('\\')[:-1])
SAVE_PATH = os.path.join('\\'.join(os.path.realpath(__file__).split('\\')[:-1]), 'raw_images')

if not(os.path.exists(SAVE_PATH)):
    os.mkdir(SAVE_PATH)

URL = 'https://mars.nasa.gov/mars2020/multimedia/raw-images/'

driver = webdriver.Firefox()
driver.get(URL)

html_raw = driver.page_source

soup = BeautifulSoup(html_raw, features="lxml")

URLS = []

pages = int(soup.find('span', class_="total_pages").text.strip())

for i in range(pages):
    class_list = soup.find_all('img')
    class_list = list(filter(lambda x: 'mars.nasa.gov/mars2020' in x['src'], class_list))
    URLS += [x['src'] for x in class_list]
    if i < pages - 1:
        driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div/div/div[3]/div/div/div/div/div/div[2]/div[2]/div/div/nav/span[2]').click()
        html_raw = driver.page_source
        soup = BeautifulSoup(html_raw, features="lxml")

driver.close()

URLS = list(set(URLS))
URLS = list(map(process_url, URLS))

for u in URLS:
    print("Downloading:", u, end = "")
    path = os.path.join(SAVE_PATH, u.split("/")[-1])
    if not(download_pictures(u, path)):
        print("\nDownload failed:", u)
    else:
        print(" - Saved to:", path)
