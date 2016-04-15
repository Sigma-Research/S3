# -*- encoding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns(
    'api.views',
    (r'^api/create_bucket/?$', 'create_bucket'),
    (r'^api/delete_bucket/?$', 'delete_bucket'),
    (r'^api/list_buckets/?$', 'list_buckets'),
    (r'^api/get_bucket/?$', 'get_bucket'),
    (r'^api/put_object/?$', 'put_object'),
    (r'^api/get_object/?$', 'get_object'),
    (r'^api/delete_object/?$', 'delete_object'),
)

urlpatterns += patterns(
    'processing.views',
    (r'^sigmalove-dev-img/(.+)$', 'processing'),
)