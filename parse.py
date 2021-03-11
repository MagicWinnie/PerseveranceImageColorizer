# -*- coding: utf-8 -*-
import os
import shutil
import requests
import argparse
import platform
import urllib.request
from tqdm import tqdm
from pathlib import Path

def process_url(s: str)-> str:
    ind_under = s.rindex('_')
    ind_dot = s.rindex('.')
    s = s[:ind_under] + s[ind_dot:]
    s = s.replace('jpg', 'png')
    return s

def download_picture(url: str, path: str)->bool:
    r = requests.get(url, stream = True)

    if r.status_code == 200:
        r.raw.decode_content = True
        
        with open(path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
            
        return True
    return False

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--sol", type=int, default=-1, help="The sol you want to download (use -1 for all)")
parser.add_argument("-r", "--rewrite", type=bool, default=False, help="Whether to rewrite existing files or not")
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

print("[INFO] GETTING DATA ABOUT ROVER")
M_RESPONSE = requests.get(url=MANIFEST.format(API=API)).json()
SOLS = [x["sol"] for x in M_RESPONSE['photo_manifest']['photos']]
PHOTOS_INFO = M_RESPONSE['photo_manifest']['photos']

if (args.sol not in SOLS) or (args.sol < -1):
    raise ValueError("Sol number incorrect.\nAvailable: {}".format(SOLS))

print("[INFO] STARTED SCRAPING")

for i in tqdm(range(len(SOLS))):
    s = SOLS[i]
    resp = requests.get(url=URL.format(SOL=s, API=API)).json()
    Path(os.path.join(SAVE_PATH, str(s))).mkdir(parents=True, exist_ok=True)
    EXISTING = os.listdir(os.path.join(SAVE_PATH, str(s)))
    for p in tqdm(range(PHOTOS_INFO[i]['total_photos']), leave=False):
        DOWNLOAD_URL = resp["photos"][p]["img_src"]
        if not(args.rewrite) and DOWNLOAD_URL.split('/')[-1] in EXISTING:
            continue
        status = download_picture(DOWNLOAD_URL, os.path.join(SAVE_PATH, str(s), DOWNLOAD_URL.split('/')[-1]))
        if not(status):
            print("Failed: URL: {}; SOL: {}; #: {}".format(DOWNLOAD_URL, s, p))

print("[INFO] FINISHED DOWNLOADING")
