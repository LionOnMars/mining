#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import Bottle
from bottle.ext.mongo import MongoPlugin

from redis import Redis
from rq import Queue

from settings import MONGO_URI
from .base import get, post, put, delete


ADMIN_BUCKET_NAME = 'openminig-admin'
collection = 'cube'

cube_app = Bottle()
mongo = MongoPlugin(uri=MONGO_URI, db=ADMIN_BUCKET_NAME, json_mongo=True)
cube_app.install(mongo)


@cube_app.route('/', method='GET')
@cube_app.route('/<slug>', method='GET')
def cube_get(mongodb, slug=None):
    return get(mongodb, collection, slug)


@cube_app.route('/', method='POST')
def cube_post(mongodb, slug=None):
    ret = post(mongodb, collection, opt={'status': False})
    if 'status' not in ret:
        Queue(connection=Redis()).enqueue_call(
            func='bin.mining.run',
            args=(ret['slug'],)
        )

    return ret


@cube_app.route('/<slug>', method='PUT')
def cube_put(mongodb, slug=None):
    ret = put(mongodb, collection, slug, opt={'status': False})
    if 'status' not in ret:
        Queue(connection=Redis()).enqueue_call(
            func='bin.mining.run',
            args=(ret['slug'],)
        )

    return ret


@cube_app.route('/<slug>', method='DELETE')
def cube_delete(mongodb, slug=None):
    return delete(mongodb, collection, slug)
