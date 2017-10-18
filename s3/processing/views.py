# -*-encoding: utf-8 -*-
#
# @author gaoyuan
#
# Apr 2016


import cv2
import json
import os
import re
from django.http import HttpResponse, HttpResponseRedirect
from s3.constants import STATIC


def json_to_response(json_data):
    response = json.dumps(json_data)
    return HttpResponse(response, mimetype='application/json')


def processing(request, name):
    bucket = 'sigmalove-dev-img'
    if '@' in name:
        object_name, option = name.split('@', 1)
        _Ver = 1
    elif '?' in name:
        object_name, option = name.split('?', 1)
        _Ver = 2

    img = cv2.imread(os.path.join(STATIC, bucket, object_name))
    height, width = img.shape[:2]
    _, ext = os.path.splitext(option)
    ext = ext if ext else '.jpg'

    if _Ver == 1:
        w = re.findall('(\d+)w', option)
    elif _Ver == 2:
        w = re.findall('w_(\d+)', option)
    if w:
        w = int(w[-1])

    if _Ver == 1:
        h = re.findall('(\d+)h', option)
    elif _Ver == 2:
        h = re.findall('h_(\d+)', option)
    if h:
        h = int(h[-1])

    if w or h:
        w = w if w else int(width * 1.0 / height * h + 0.5)
        h = h if h else int(height * 1.0 / width * w + 0.5)
        img = cv2.resize(img, (w, h))
        height, width = img.shape[:2]

    if _Ver == 1:
        a = re.findall('(\d+)-(\d+)-(\d+)-(\d+)a', option)
    elif _Ver == 2:
        a = re.findall('crop,x_(\d+),y_(\d+),w_(\d+),h_(\d+)', option)

    if a:
        x, y, w, h = [int(i) for i in a[-1]]
        if x < width and y < height:
            img = img[y: y + h, x: x + w]

    if _Ver == 1:
        q = re.findall('(\d+)q', option)
    elif _Ver == 2:
        q = re.findall('rotate,(\d+)', option)

    if q:
        q = int(q[-1])
    else:
        q = 90

    try:
        data = cv2.imencode(ext, img, [1, q])[1].tostring()
        return HttpResponse(data, mimetype='image/%s' % (ext[1:]))
    except Exception, e:
        print e
        return HttpResponseRedirect('/%s/%s' % (bucket, object_name))
