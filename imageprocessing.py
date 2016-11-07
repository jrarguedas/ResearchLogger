#!/usr/bin/env python

'''
Simple "Square Detector" program.

Loads several images sequentially and tries to find squares in each image.
'''

# Python 2/3 compatibility
import sys
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2
import pytesseract
from PIL import Image


def is_inside(contour,x,y):
    returnvalue = cv2.pointPolygonTest(contour, (x,y), False)
    if returnvalue >= 0: #positive means inside, zero means on the border
        return True
    else: return False

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )


def find_squares(img):
    img = cv2.GaussianBlur(img, (5, 5), 0)
    squares = []
    for gray in cv2.split(img):
        for thrs in xrange(0, 255, 26):
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                kernel = np.ones((3,3),np.uint8)
                bin = cv2.dilate(bin, kernel, iterations = 1)
                bin = cv2.morphologyEx(bin, cv2.MORPH_OPEN, kernel)
                bin = cv2.morphologyEx(bin, cv2.MORPH_CLOSE, kernel)

                kernel = np.ones((5,5),np.uint8)
                bin = cv2.morphologyEx(bin, cv2.MORPH_CLOSE, kernel)

            else:
                retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                    if max_cos < 0.1:
                        squares.append(cnt)


            break
        break
    return squares
#cv2 style[Y1:Y2, X1:X2]
def get_corners_cv2_style(contours):
    max_left = float("inf")
    max_right = -1

    max_down = float("inf")
    max_up = -1
    #for i in range(1, len(contour)):
    for contour in contours:
        contour_x = np.squeeze(contour)[0]
        contour_y = np.squeeze(contour)[1]
        if contour_x > max_right: max_right = contour_x
        if contour_x < max_left: max_left = contour_x
        if contour_y > max_up: max_up = contour_y
        if contour_y < max_down: max_down = contour_y

    return [(max_down,max_up),(max_left,max_right)]

#cv1_style[X1:Y1, width:height]
def get_corners_cv1_style(contours):
    max_left = float("inf")
    max_right = -1

    max_down = float("inf")
    max_up = -1
    #for i in range(1, len(contour)):
    for contour in contours:
        contour_x = np.squeeze(contour)[0]
        contour_y = np.squeeze(contour)[1]
        if contour_x > max_right: max_right = contour_x
        if contour_x < max_left: max_left = contour_x
        if contour_y > max_up: max_up = contour_y
        if contour_y < max_down: max_down = contour_y
    topleft = (max_left,max_down)
    width = max_right-max_left
    height = max_up-max_down
    bottomright_delta = (width, height)

    return [topleft,bottomright_delta]

i = 0
def find_polys(image_data,x,y):
    img = np.asarray(image_data)
    original_image = img.copy()
    global i
    img = cv2.GaussianBlur(img, (5, 5), 0)
    #cv2.imwrite('blurred' + str(i) + '.png',img)
    squares = []
    for gray in cv2.split(img):
        pepito = True
        if pepito:
        #for thrs in xrange(0, 255, 26):
            thrs = 0
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin = cv2.dilate(bin, None)

                bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                kernel = np.ones((3,3),np.uint8)
                bin = cv2.dilate(bin, kernel, iterations = 1)
                bin = cv2.morphologyEx(bin, cv2.MORPH_OPEN, kernel)
                bin = cv2.morphologyEx(bin, cv2.MORPH_CLOSE, kernel)

                kernel = np.ones((5,5),np.uint8)
                bin = cv2.morphologyEx(bin, cv2.MORPH_CLOSE, kernel)


            contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(bin, contours, -1, (255,255,0), 1)

            #cv2.imwrite('contours' + str(i) + '.png',bin)
            for cnt in contours:

                corners = get_corners_cv2_style(cnt)
                polygon_height = abs(corners[0][1] - corners[0][0])
                polygon_width= abs(corners[1][1] - corners[1][0])
                pepe = True
                if is_inside(cnt,x,y) and polygon_width>20 and polygon_height>5 and polygon_width<200 and polygon_height<50:
                    #cropped_image = original_image[Y1:Y2, X1:X2]
                    cropped_image = original_image[corners[0][0]:corners[0][1],corners[1][0]:corners[1][1]]
                    cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_RGB2GRAY)

                    ret,cropped_image = cv2.threshold(cropped_image,200,255,cv2.THRESH_BINARY)
                    kernel = np.ones((1,1),np.uint8)
                    cropped_image = cv2.dilate(cropped_image, kernel, iterations = 1)
                    cropped_image = cv2.morphologyEx(cropped_image, cv2.MORPH_OPEN, kernel)
                    cropped_image = cv2.morphologyEx(cropped_image, cv2.MORPH_CLOSE, kernel)

                    cv2.imwrite('messigray' + str(i) + '.png',cropped_image)


                    img = Image.fromarray(cropped_image)
                    txt = pytesseract.image_to_string(img)
                    print(txt)
                    i += 1
                    cnt_len = cv2.arcLength(cnt, True)
                    cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                    area = cv2.contourArea(cnt)
                    max_and_min = (5000,50)
                    if area < max_and_min[0] and area > max_and_min[1]:
                        squares.append(cnt)

        break
    return squares

if __name__ == '__main__':
    img = cv2.imread('saved2.png')
    #squares = find_squares(img)
    polys = find_polys(img)
    #cv2.fillPoly(img, squares, (255, 0, 0))
    cv2.fillPoly(img, polys, (0, 0, 255))
    #cv2.drawContours( img, squares, -1, (0, 0, 255), 1 )
    cv2.imshow('squares', img)
    ch = 0xFF & cv2.waitKey()
    #if ch == 27:
    #    cv2.destroyAllWindows()
    cv2.destroyAllWindows()
