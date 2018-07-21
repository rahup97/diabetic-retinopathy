from google.cloud import storage
import time
import numpy as np
import cv2
from firebase import firebase
import json

firebase = firebase.FirebaseApplication('<link_to_firebase_instance>', None)

color = cv2.imread('Mary/4387fDE_Demo Patient_Mary_19500703_20150817_OD_(125).jpg')
color = cv2.resize(color, (400, 400), interpolation = cv2.INTER_CUBIC)
img = cv2.imread('Mary/4387fDE_Demo Patient_Mary_19500703_20150817_OD_(138).jpg', 0)
img = cv2.resize(img, (400, 400), interpolation = cv2.INTER_CUBIC)


edge = cv2.Canny(img, 150, 255)
closing = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, np.ones((3, 3)))
_, contours, _ = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

black = np.zeros(img.shape)

for i in contours:
    if cv2.contourArea(i) < 20:
        cv2.drawContours(black, [i], 0, 255, -1)

_, contours, _ = cv2.findContours(black.copy().astype('uint8'), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
black2 = np.zeros(img.shape)

for i in contours:
    if cv2.contourArea(i) < 20:
        cv2.drawContours(black2, [i], 0, 255, -1)

black2[370:400,0:85] = 0

_, contours, _ = cv2.findContours(black2.copy().astype('uint8'), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
black3 = np.zeros(img.shape)

for i in contours:
    _, dim, _ = cv2.minAreaRect(i)
##    print(dim)
    if dim[1] > (4 * dim[0]) or dim[0] > (4 * dim[1]):
        continue
    cv2.drawContours(black3, [i], 0, 255, -1)

diff = img - black3
for i in diff:
    for j in i:
        j = max(0, j)

cv2.imshow('Edge', edge)
cv2.imshow('Image', img)
cv2.imshow('Black', black)
cv2.imshow('Black2', black2)
cv2.imshow('Black3', black3)
cv2.imshow('Closing', closing)

_, final_contour, _ = cv2.findContours(black3.copy().astype('uint8'), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

rect = []

for i in range(len(final_contour)):
    x, y, w, h = cv2.boundingRect(final_contour[i])
    rect.append((x, y, w, h))

final_x = []
final_y = []
count = 0

for x, y, w, h in rect:
    cv2.rectangle(color, (x, y), (x + w, y + h), (0, 255, 0), 1)
    xtemp = (x) + (w/2)
    ytemp = (y) + (h/2)
    x_final = xtemp - 200
    y_final = 200 - ytemp
    result = firebase.put('/Coordinates/mary@gmail,com/Image/Latitude','/'+str(count),x_final)
    result2 = firebase.put('/Coordinates/mary@gmail,com/Image/Longitude','/'+str(count),y_final)
    final_x.append(x_final)
    final_y.append(y_final)
    count+=1

result3 = firebase.put('/Coordinates/mary@gmail,com/Image','/number',count)
cv2.imshow('final', color)
cv2.imwrite('final.jpg', color)
print(final_x)
print(final_y)

time.sleep(3)

client = storage.Client()

sbucket = client.get_bucket('<relevant_path.appsot.com>')
blob = sbucket.get_blob('Mary_leak_detect.jpg')
blob.upload_from_filename(filename = 'final.jpg')


cv2.waitKey(0)
cv2.destroyAllWindows()
