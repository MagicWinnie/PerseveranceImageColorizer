# -*- coding: utf-8 -*-
import os
import shutil
import requests
import argparse
import platform
from typing import *
import urllib.request
from tqdm import tqdm
from pathlib import Path
from parfive import Downloader

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--sol", type=int, default=-1, help="The sol you want to download (use -1 for all)")
parser.add_argument("-r", "--rewrite", type=bool, default=False, help="Whether to rewrite existing files or not")
parser.add_argument("-c", "--color", type=int, default=0, help="Whether to download color-processed images. Assuming it is encoded with 'F'. (0: download all, 1: download only color-processed, 2: download only raw")
parser.add_argument("-a", "--api", type=str, required=True, help="Path to the file containing NASA API")
args = parser.parse_args()

delimeter = '\\' if platform.system() == "Windows" else '/'
FOLDER = delimeter.join(os.path.realpath(__file__).split(delimeter)[:-1])
SAVE_PATH = os.path.join(FOLDER, 'raw_images')
Path(SAVE_PATH).mkdir(parents=True, exist_ok=True)

with open(args.api, 'r') as f:
    API = f.read()

URL = 'https://api.nasa.gov/mars-photos/api/v1/rovers/perseverance/photos?sol={SOL}&api_key={API}'
MANIFEST = 'https://api.nasa.gov/mars-photos/api/v1/manifests/perseverance/?api_key={API}'

dl = Downloader()

print("[INFO] GETTING DATA ABOUT ROVER")
M_RESPONSE = requests.get(url=MANIFEST.format(API=API)).json()
SOLS = [x["sol"] for x in M_RESPONSE['photo_manifest']['photos']]
PHOTOS_INFO = M_RESPONSE['photo_manifest']['photos']

if ((args.sol) != -1 and (args.sol not in SOLS)) or (args.sol < -1):
    raise ValueError("Sol number incorrect.\nAvailable: {}".format(SOLS))

print("[INFO] STARTED SCRAPING")
for i in tqdm(range(len(SOLS))):
    s = SOLS[i]
    resp = requests.get(url=URL.format(SOL=s, API=API)).json()
    Path(os.path.join(SAVE_PATH, str(s))).mkdir(parents=True, exist_ok=True)
    EXISTING = os.listdir(os.path.join(SAVE_PATH, str(s)))
    for p in range(PHOTOS_INFO[i]['total_photos']):
        url = resp["photos"][p]["img_src"].replace('_1200.jpg', '.png')
        path = os.path.join(SAVE_PATH, str(s))
        if args.color == 1:
            if url.split('/')[-1].split('_')[0][-1] == 'F':
                dl.enqueue_file(url, path=path)
        elif args.color == 2:
            if url.split('/')[-1].split('_')[0][-1] != 'F':
                dl.enqueue_file(url, path=path)
        else:
            dl.enqueue_file(url, path=path)
print("[INFO] FINISHED SCRAPING")

print("[INFO] STARTED DOWNLOADING")
dl.download()
print("[INFO] FINISHED DOWNLOADING")
