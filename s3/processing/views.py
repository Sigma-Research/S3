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
bucket = 'sigmalove-dev-img'


def json_to_response(json_data):
    response = json.dumps(json_data)
    return HttpResponse(response, content_type='application/json')


def processing(request, name):
    if '@' in name:
        object_name, option = name.split('@', 1)
        return version1(request, object_name, name)
    elif 'x-oss-process' in request.GET:
        object_name = name
        option = request.GET.get('x-oss-process')
        return version2(request, object_name, option)
    else:
        return HttpResponseRedirect('/%s/%s' % (bucket, name))


def resize(w, h, width, height, img):
    w = w if w else int(width * 1.0 / height * h + 0.5)
    h = h if h else int(height * 1.0 / width * w + 0.5)
    img = cv2.resize(img, (w, h))
    return img.shape[:2], img


def rotate(r, img):
    if r == 90:
        img = cv2.flip(cv2.transpose(img), 1)
    elif r == 180:
        img = cv2.flip(img, -1)
    elif r == 270:
        img = cv2.flip(cv2.transpose(img), 0)
    return img


def compress(q, ext, img):
    return cv2.imencode(ext, img, [1, q])[1].tostring()


def crop(x, y, w, h, height, width, img):
    w = w or width
    h = h or height
    if x < width and y < height:
        img = img[y: y + h, x: x + w]
    return img.shape[:2], img


def version1(request, object_name, option):
    img = cv2.imread(os.path.join(STATIC, bucket, object_name))
    height, width = img.shape[:2]

    _, ext = os.path.splitext(option)
    ext = ext if ext else '.jpg'
    w = re.findall('(\d+)w', option)
    h = re.findall('(\d+)h', option)

    w = int(w[-1]) if w else w
    h = int(h[-1]) if h else h

    if w or h:
        (height, width), img = resize(w, h, width, height, img)

    a = re.findall('(\d+)-(\d+)-(\d+)-(\d+)a', option)
    if a:
        x, y, w, h = [int(i) for i in a[-1]]
        img = crop(x, y, w, h, height, width, img)

    r = re.findall('(\d+)r', option)
    if r:
        r = int(r[-1])
        img = rotate(r, img)

    q = re.findall('(\d+)q', option)
    q = int(q[-1]) if q else 90

    try:
        return HttpResponse(compress(q, ext, img), content_type='image/%s' % (ext[1:]))
    except Exception, e:
        print e
        return HttpResponseRedirect('/%s/%s' % (bucket, object_name))


def version2(request, object_name, option):
    img = cv2.imread(os.path.join(STATIC, bucket, object_name))
    height, width = img.shape[:2]
    ext = re.findall('/format,(\w+)', option)
    ext = ext[0] if ext else '.jpg'

    for cmd in option.split('/'):
        if cmd.startswith('resize'):
            w = re.findall('w_(\d+)', cmd)
            h = re.findall('h_(\d+)', cmd)
            (height, width), img = resize(w, h, height, width, img)
        elif cmd.startswith('crop'):
            x, y, w, h = map(int, re.findall('crop,x_(\d+),y_(\d+),w_(\d+),h_(\d+)', cmd).groups())
            (height, width), img = crop(x, y, w, h, height=height, width=width, img=img)
        elif cmd.startswith('rotate'):
            r = int(re.findall('rotate,(\d+)', cmd)[0])
            img = rotate(r, img)

    q = re.findall('/quality,q_(\d+)', option)
    Q = q if q else re.findall('/quality,Q_(\d+)', option)
    q = Q if Q else 90

    try:
        return HttpResponse(compress(q, ext, img), content_type='image/%s' % (ext[1:]))
    except Exception, e:
        print e
        return HttpResponseRedirect('/%s/%s' % (bucket, object_name))
