import numpy as np
import cv2
from matplotlib import pyplot as plt

MIN_MATCH_COUNT = 10

img1 = cv2.imread('Matthias/MatthiasOD00.jpg', 0)
img2 = cv2.imread('Matthias/MatthiasOD01.jpg', 0)

img1 = cv2.resize(img1, (400, 400), cv2.INTER_CUBIC)
img2 = cv2.resize(img2, (400, 400), cv2.INTER_CUBIC)

clahe = cv2.createCLAHE(clipLimit = 2.0, tileGridSize = (8, 8))
img1 = clahe.apply(img1)
img2 = clahe.apply(img2)

sift = cv2.xfeatures2d.SIFT_create()

kp1, des1 = sift.detectAndCompute(img1, None)
kp2, des2 = sift.detectAndCompute(img2, None)

FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks = 50)

flann = cv2.FlannBasedMatcher(index_params, search_params)

matches = flann.knnMatch(des1,des2,k=2)

good = []

for m, n in matches:
    if m.distance < 0.7 * n.distance:
        good.append(m)
        
if len(good) > MIN_MATCH_COUNT:
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1, 1, 2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1, 1, 2)

    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
    matchesMask = mask.ravel().tolist()

    h,w = img2.shape
    dst = cv2.warpPerspective(img1, M, (h, w))
    cv2.imshow('Img1', img1)
    cv2.imshow('Img2', img2)
    cv2.imshow('Dst', dst)
    cv2.waitKey(0)
