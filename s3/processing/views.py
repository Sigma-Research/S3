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
    object_name, option = name.split('@', 1)
    img = cv2.imread(os.path.join(STATIC, bucket, object_name))
    height, width = img.shape[:2]
    _, ext = os.path.splitext(option)
    ext = ext if ext else '.jpg'
    w = re.findall('(\d+)w', option)
    if w:
        w = w[-1]
    h = re.findall('(\d+)h', option)
    if h:
        h = h[-1]
    if w or h:
        w = w if w else int(width * 1.0 / height * h + 0.5)
        h = h if h else int(height * 1.0 / width * w + 0.5)
        img = cv2.resize(img, (w, h))
        height, width = img.shape[:2]
    a = re.findall('(\d+)-(\d+)-(\d+)-(\d+)a', option)
    if a:
        x, y, w, h = a[-1]
        if x < width and y < height:
            img = img[y: y + h, x: x + w]
    q = re.findall('(\d+)q', option)
    if q:
        q = q[-1]
    else:
        q = 90
    try:
        ret, buf = cv2.imencode(ext, img, [1, q])
    except Exception, e:
        print e
        return HttpResponseRedirect('/%s/%s' % (bucket, object_name))
    if ret:
        data = buf.tostring()
        return HttpResponse(data, mimetype='image/%s' % (ext[1:]))
    else:
        return HttpResponseRedirect('/%s/%s' % (bucket, object_name))