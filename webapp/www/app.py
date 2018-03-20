import logging;logging.basicConfig(level=logging.INFO) #导入INFO级日志类

import asyncio,os,json,time
from datetime import datetime

from aiohttp import web #导入asyncio的HTTP框架

def index(request):
    home = web.Response(body = '<h1>我的第一个项目</h1>') #响应web请求
    home.content_type = 'text/html;charset=utf-8' #声明content_type易避免浏览器解析为下载文件
    return home #返回html页面内容

@asyncio.coroutine
def init(loop):
    app = web.Application(loop = loop)
    app.router.add_route('GET','/',index) #添加路由
    srv = yield from loop.create_server(app.make_handler(),'127.0.0.1',5000)
    logging.info('本地服务器启动 http://127.0.0.1:5000 ...') 
    return srv

loop = asyncio.get_event_loop() #创建消息循环
loop.run_until_complete(init(loop)) #执行协程 init
loop.run_forever() #循环等待

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