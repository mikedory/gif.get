import datetime
from random import random

from mongoengine import *


# each known site that hosts gifs
class Gifsite(Document):
    created_at = DateTimeField(default=datetime.datetime.now, required=True)
    title = StringField(max_length=255, required=True)
    slug = StringField(max_length=255, required=True)
    body = StringField(required=True)
    tags = ListField(StringField(max_length=30), required=False)
    random = FloatField(default=random())

    def __unicode__(self):
        return self.title

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }


# the magical gifs themselves!
class Gif(Document):
    created_at = DateTimeField(default=datetime.datetime.now, required=True)
    title = StringField(max_length=255, required=True)
    slug = StringField(max_length=255, required=False)
    img_url = StringField(max_length=255, required=True)
    img_type = StringField(max_length=25, required=True)
    host_name = StringField(max_length=255, required=True)
    host_url = StringField(max_length=255, required=True)
    tags = ListField(StringField(max_length=30), required=False)
    random = FloatField(default=random())

    def __unicode__(self):
        return self.title

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }
