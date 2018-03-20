#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'K少'
'''
async web application.
'''

import asyncio, logging
import logging


@asyncio.coroutine
def create_pool(loop,**kw):
    logging.info('创建数据库连接池')
    global __pool #声明全局连接池变量
    __pool = yield from aiomysql.create_pool(
        host = kw.get('host','localhost'),
        port = kw.get('port',3306),
        user = kw['user'],
        password = kw['password'],
        db = kw['db'],
        charset = kw.get('charset','utf-8'),
        autocommit = kw.get('autocommit',True),
        maxsize = kw.get('maxsize',10),
        minsize = kw.get('minsize',1),
        loop = loop
    )#调用数据库异步模块配置连接池属性

@asyncio.coroutine
def select(sql,args,size = None):
    log(sql,args)
    global __pool
    with (yield from __pool) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)#调用子协程
        yield from cur.execute(sql.replace('?','%s'),args or ())
        if size:
            rs = yield from cur.fetchmany(size)
        else:
            rs = yield from cur.fechall()
        yield from cur.close()
        logging.info('共查询到: %s 条数据' % len(rs))
        return rs

@asyncio.coroutine
def execute(sql,args):
    log(sql)
    with (yield from __pool) as conn:
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace('?','%s'),args)
            affected = cur.rowcount
            yield from cur.close()
        except BaseException as e:
            rasie
        return affected

class User(Model):
    __table__ = 'users'

    id = IntergerField(primary_key = True)
    name = StringField()

class Model(dict,metaclass=ModelMetaclass):
    def __init__(self,**kw):
        super(Model,self).__init__(**kw)

    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            rasie AttributeError(r"'Model' 类不包含属性 '%s' " % key)

    def __setattr__(self,key,value):
        self[key] = value

    def getValue(self,key):
        return getattr(self,key,None)

    def getValueOrDefault(self,key):
        value = getattr(self,key,None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default()
                if callable(field.default) else field.default
                logging.debug('使用默认值 %s:%s' % (key,str(value)))
                setattr(self,key,value)
        return value

class Field