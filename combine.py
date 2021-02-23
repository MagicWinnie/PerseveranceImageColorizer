'''
Combines several channels into one
Searches for similar images using compare_ssim
Doesn't work with images containing 'E' or 'M' 'cause
I don't know what it means
Also not working with low resolution images
By @MagicWinnie
'''
import numpy as np
from skimage.measure import compare_ssim
import cv2
import json
import os
import sys

def pretty(d, indent = 0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print('\t' * (indent + 1) + str(value))

def filter_func(new: str, orig: str)->str:
    temp_new = new.split('_')
    temp_orig = orig.split('_')
    if temp_new[0][:-1] == temp_orig[0][:-1] and temp_new[-1] == temp_orig[-1] and \
        temp_new[1] == temp_orig[1]:
            return True
    return False

def check_size(a, b, c, size_thresh = (100, 100)):
    if not(a.shape == b.shape == c.shape):
        return False
    if (a.shape[0] < size_thresh[0] and a.shape[1] < size_thresh[1]) and \
        (b.shape[0] < size_thresh[0] and b.shape[1] < size_thresh[1]) and \
        (c.shape[0] < size_thresh[0] and c.shape[1] < size_thresh[1]):
            return False
    return True

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
	dim = None
	(h, w) = image.shape[:2]
	if width is None and height is None:
		return image
	if width is None:
		r = height / float(h)
		dim = (int(w * r), height)
	else:
		r = width / float(w)
		dim = (width, int(h * r))
	resized = cv2.resize(image, dim, interpolation = inter)
	return resized

import platform
if platform.system() == "Windows":
    FOLDER = '\\'.join(os.path.realpath(__file__).split('\\')[:-1])
    SAVE_PATH = os.path.join('\\'.join(os.path.realpath(__file__).split('\\')[:-1]), 'raw_images')
else:
    FOLDER = '/'.join(os.path.realpath(__file__).split('/')[:-1])
    SAVE_PATH = os.path.join('/'.join(os.path.realpath(__file__).split('/')[:-1]), 'raw_images')
    
IMG_PATH = os.path.join(FOLDER, 'color_images')
FILES = os.listdir(SAVE_PATH)

if not(os.path.exists(IMG_PATH)):
    os.mkdir(IMG_PATH)

R = list(filter(lambda x: x.split('_')[0][-1] == 'R', FILES))
G = list(filter(lambda x: x.split('_')[0][-1] == 'G', FILES))
B = list(filter(lambda x: x.split('_')[0][-1] == 'B', FILES))
E = list(filter(lambda x: x.split('_')[0][-1] == 'E', FILES))
M = list(filter(lambda x: x.split('_')[0][-1] == 'M', FILES))

'''
{
    - FL
        {
            - R
            - G
            - B
        }
    - FR
     ...
    - RR
}
'''
imgs = dict()

m = max(len(R), len(G), len(B), len(E), len(M))

# print(len(R), len(G), len(B), len(E), len(M))

argv = sys.argv
if len(argv) > 1 and argv[1].split('.')[-1] == 'json':
    with open(argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)
    for key in data:
        if len(data[key]) != 3:
            print("PASSING:", key)
            continue
        a = cv2.imread(os.path.join(SAVE_PATH, data[key][0]), 0)
        b = cv2.imread(os.path.join(SAVE_PATH, data[key][1]), 0)
        c = cv2.imread(os.path.join(SAVE_PATH, data[key][2]), 0)
        assert a.shape == b.shape == c.shape
        cv2.imwrite(os.path.join(IMG_PATH, data[key][0]), cv2.merge((c, b, a)))
else:
    for f in FILES:
        key = f.split('_')[0][:-1]
        img = cv2.imread(os.path.join(SAVE_PATH, f), 0)
        
        if key not in imgs:
            imgs[key] = {}
        if str(img.shape) not in imgs[key]:
            imgs[key][str(img.shape)] = {}
        if f.split('_')[1] not in imgs[key][str(img.shape)]:
            imgs[key][str(img.shape)][f.split('_')[1]] = {'R': [], 'G': [], 'B': [], 'E': [], 'M': []}

        imgs[key][str(img.shape)][f.split('_')[1]][f.split('_')[0][-1]].append(f)
        # imgs[key][str(img.shape)][f.split('_')[0][-1]][-1]['img'] = img
        imgs[key][str(img.shape)][f.split('_')[1]][f.split('_')[0][-1]].sort()

    for cam in imgs:
        for size in imgs[cam]:
            temp_size = eval(size)
            if temp_size[0] < 100 and temp_size[1] < 100: continue
            for sol in imgs[cam][size]:
                temp = imgs[cam][size][sol]
                if len(temp["R"]) == 0 or len(temp["G"]) == 0 or len(temp["B"]) == 0:
                    continue
                min_len_key = min(temp.items(), key=lambda x: len(x))[0]

                if min_len_key == "R":
                    others = ["G", "B"]
                elif min_len_key == "G":
                    others = ["R", "B"]
                else:
                    others = ["R", "G"]
                
                for i in temp[min_len_key]:
                    orig = cv2.imread(os.path.join(SAVE_PATH, i), 0)
                    others_images = {}
                    for key in others:
                        values = []
                        imgs_values = []
                        for other in temp[key]:
                            new = cv2.imread(os.path.join(SAVE_PATH, other), 0)
                            (score, diff) = compare_ssim(orig, new, full=True)
                            diff = (diff * 255).astype("uint8")
                            values.append(score)
                            imgs_values.append(new)
                        if max(values) < 0.8:
                            continue
                        others_images[key] = imgs_values[values.index(max(values))]
                    if len(others_images.keys()) > 0:
                        # cv2.imshow('orig', image_resize(orig, width=300))
                        # cv2.imshow('other1', image_resize(others_images[others[0]], width=300))
                        # cv2.imshow('other2', image_resize(others_images[others[1]], width=300))
                        # orig = np.uint8(orig)
                        # others_images[others[0]] = np.uint8(others_images[others[0]])
                        # others_images[others[1]] = np.uint8(others_images[others[1]])
                        if min_len_key == "R" and others[0] == "G":
                            image = cv2.merge((others_images[others[1]], others_images[others[0]], orig))
                        elif min_len_key == "R" and others[0] == "B":
                            image = cv2.merge((others_images[others[0]], others_images[others[1]], orig))
                        elif min_len_key == "G" and others[0] == "R":
                            image = cv2.merge((others_images[others[1]], orig, others_images[others[0]]))
                        elif min_len_key == "G" and others[0] == "B":
                            image = cv2.merge((others_images[others[0]], orig, others_images[others[1]]))
                        elif min_len_key == "B" and others[0] == "R":
                            image = cv2.merge((orig, others_images[others[1]], others_images[others[0]]))
                        elif min_len_key == "B" and others[0] == "G":
                            image = cv2.merge((orig, others_images[others[0]], others_images[others[1]]))
                        cv2.imwrite(os.path.join(IMG_PATH, i), image)
                        # cv2.waitKey(0)
                    