# -*- encoding: utf-8 -*-
#
# #@author gaoyuan

import os
import json
import shutil
import base64
from s3 import constants
from django.http import HttpResponse
from poster.streaminghttp import register_openers

register_openers()


def json_to_response(json_data):
    response = json.dumps(json_data)
    return HttpResponse(response, content_type='application/json')


def verify_secret(func):

    def func_wrapper(request, *args, **kwargs):
        secret = request.POST.get('secret', None)
        if secret and secret == constants.SECRET:
            return func(request, *args, **kwargs)
        else:
            return json_to_response({'message': 'Auth failed', 'code': 1})

    return func_wrapper


#@verify_secret
def create_bucket(request):
    bucket = request.POST.get('bucket', None)
    if bucket:
        try:
            os.mkdir(os.path.join(constants.STATIC, bucket))
            return {'code': 0, 'message': ''}
        except:
            return json_to_response({'message': 'bucket existed', 'code': 1})
    else:
        return json_to_response({'message': 'No bucket name', 'code': 1})


#@verify_secret
def delete_bucket(request):
    bucket = request.POST.get('bucket', None)
    if bucket:
        if os.listdir(os.path.join(constants.STATIC, bucket)):
            return json_to_response({'message': 'Not empty', 'code': 1})
        else:
            shutil.rmtree(os.path.join(constants.STATIC, bucket))
            return json_to_response({'message': '', 'code': 0})
    else:
        return json_to_response({'message': 'No bucket name', 'code': 1})


#@verify_secret
def list_buckets(request):
    data = os.listdir(constants.STATIC)
    return json_to_response({'code': 0, 'data': data})


#@verify_secret
def get_bucket(request):
    bucket = request.POST.get('bucket', None)
    if bucket:
        data = os.listdir(os.path.join(constants.STATIC, bucket))
        return json_to_response({'code': 0, 'data': data})
    else:
        return json_to_response({'message': 'No bucket name', 'code': 1})


#@verify_secret
def put_object(request):
    bucket = request.POST.get('bucket', '').encode('utf-8')
    object_name = request.POST.get('object_name', '').encode('utf-8')
    content = request.POST.get('content', None)
    if bucket and object_name:
        try:
            if not os.path.exists(os.path.dirname(os.path.join(constants.STATIC, bucket, object_name))):
                os.makedirs(os.path.dirname(os.path.join(constants.STATIC, bucket, object_name)))
            if content:
                with open(os.path.join(constants.STATIC, bucket, object_name), 'wb') as f:
                    f.write(base64.b64decode(content.encode('utf-8')))
            else:
                content = request.FILES.get('content')
                with open(os.path.join(constants.STATIC, bucket, object_name), 'wb') as f:
                    f.write(content.read())
            return json_to_response({'code': 0, 'data': ''})
        except Exception, e:
            print e
            return json_to_response({'message': 'No bucket', 'code': 1})
    else:
        return json_to_response({'message': 'Miss Params', 'code': 1})


#@verify_secret
def get_object(request):
    bucket = request.POST.get('bucket', None)
    object_name = request.POST.get('object_name', None)
    if bucket and object_name:
        try:
            with open(os.path.join(constants.STATIC, bucket, object_name), 'rb') as f:
                data = f.read()
            return json_to_response({'code': 0, 'data': base64.b64encode(data)})
        except Exception, e:
            print e
            return json_to_response({'message': 'No object', 'code': 1})
    else:
        return json_to_response({'message': 'Miss Params', 'code': 1})


def list_objects(request):
    bucket = request.POST.get('bucket', None)
    path = request.POST.get('path', None)
    if bucket and path:
        if os.path.isdir(os.path.join(constants.STATIC, bucket, path)):
            return json_to_response({'code': 0, 'data': os.listdir(os.path.join(constants.STATIC, bucket, path))})
        else:
            return json_to_response({'code': 0, 'data': []})
    else:
        return json_to_response({'message': 'Miss Params', 'code': 1})
    

#@verify_secret
def delete_object(request):
    bucket = request.POST.get('bucket', None)
    object_name = request.POST.get('object_name', None)
    if bucket and object_name:
        try:
            os.remove(os.path.join(constants.STATIC, bucket, object_name))
            return json_to_response({'code': 0, 'data': ''})
        except:
            return json_to_response({'message': 'No object', 'code': 1})
    else:
        return json_to_response({'message': 'Miss Params', 'code': 1})
