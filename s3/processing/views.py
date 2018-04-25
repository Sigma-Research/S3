# -*-encoding: utf-8 -*-
#
# @author gaoyuan
#
# Apr 2016


import cv2
import json
import os
import re
from PIL import Image
from django.http import HttpResponse, HttpResponseRedirect
from s3.constants import STATIC

bucket = 'sigmalove-dev-img'


def processing(request, name):
    if '@' in name:
        object_name, option = name.split('@', 1)
        return version1(request, object_name, option)
    elif 'x-oss-process' in request.GET:
        object_name = name
        option = request.GET.get('x-oss-process')
        if option == 'image/info':
            return info(request, object_name)
        return version2(request, object_name, option)
    else:
        return HttpResponseRedirect('/%s/%s' % (bucket, name))


def resize(img, size):
    height, width = img.shape[:2]
    w, h = size
    w = w if w else int(width * 1.0 / height * h + 0.5)
    h = h if h else int(height * 1.0 / width * w + 0.5)
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)


def rotate(img, degree):
    if degree == 90:
        return cv2.flip(cv2.transpose(img), 1)
    elif degree == 180:
        return cv2.flip(img, -1)
    elif degree == 270:
        return cv2.flip(cv2.transpose(img), 0)
    return img


def crop(img, rect):
    height, width = img.shape[:2]
    x, y, w, h = rect
    w = w or width
    h = h or height
    if x < width and y < height:
        return img[y: y + h, x: x + w]
    return img


def compress(img, ext, quality):
    return cv2.imencode(ext, img, [1, quality])[1].tostring()


def version1(request, object_name, option):
    img = cv2.imread(os.path.join(STATIC, bucket, object_name))

    w = re.findall('(\d+)w', option)
    h = re.findall('(\d+)h', option)
    w = int(w[-1]) if w else w
    h = int(h[-1]) if h else h
    if w or h:
        img = resize(img, (w, h))

    a = re.findall('(\d+)-(\d+)-(\d+)-(\d+)a', option)
    if a:
        x, y, w, h = [int(i) for i in a[-1]]
        img = crop(img, (x, y, w, h))

    r = re.findall('(\d+)r', option)
    if r:
        degree = int(r[-1])
        img = rotate(img, degree)

    _, ext = os.path.splitext(option)
    ext = ext if ext else '.jpg'
    q = re.findall('(\d+)q', option)
    q = int(q[-1]) if q else 90

    try:
        return HttpResponse(compress(img, ext, q), content_type='image/%s' % (ext[1:]))
    except Exception, e:
        print e
        return HttpResponseRedirect('/%s/%s' % (bucket, object_name))


def version2(request, object_name, option):
    img = cv2.imread(os.path.join(STATIC, bucket, object_name))

    for cmd in option.split('/'):
        if cmd.startswith('resize'):
            w = re.findall('w_(\d+)', cmd)
            h = re.findall('h_(\d+)', cmd)
            w = int(w[-1]) if w else w
            h = int(h[-1]) if h else h
            img = resize(img, (w, h))
        elif cmd.startswith('crop'):
            x, y, w, h = [int(i) for i in re.search('crop,x_(\d+),y_(\d+),w_(\d+),h_(\d+)', cmd).groups()]
            img = crop(img, (x, y, w, h))
        elif cmd.startswith('rotate'):
            degree = int(re.findall('rotate,(\d+)', cmd)[0])
            img = rotate(img, degree)

    ext = re.findall('/format,(\w+)', option)
    ext = '.' + ext[0] if ext else '.jpg'
    q = re.findall('/quality,[q,Q]_(\d+)', option)
    q = int(q[-1]) if q else 90

    try:
        return HttpResponse(compress(img, ext, q), content_type='image/%s' % (ext[1:]))
    except Exception, e:
        print e
        return HttpResponseRedirect('/%s/%s' % (bucket, object_name))


def info(request, object_name):
    img_path = os.path.join(STATIC, bucket, object_name)
    im = Image.open(img_path)
    data = {
        'FileSize': {'value': os.stat(img_path).st_size},
        'Format': {'value': im.format},
        'ImageHeight': {'value': im.height},
        'ImageWidth': {'value': im.width}
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
