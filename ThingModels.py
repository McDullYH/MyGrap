#!/usr/bin/python
#-*- coding:utf-8 -*-

from peewee import *
from settings import *

class BaseModel(Model):
    class Meta:
        database = mysql_db

class Shop(BaseModel):
    id=BigIntegerField(primary_key=True)
    url=CharField(null=False)

class Thing(BaseModel):
    id=BigIntegerField(primary_key=True)
    current_describe=CharField(null=False)
    current_price=FloatField(null=False)
    update_time=DateTimeField(null=False)
    shop=ForeignKeyField(Shop)



class ThingPrice(BaseModel):
    thing=ForeignKeyField(Thing)
    price=FloatField(null=False)
    time=DateTimeField(null=False)


