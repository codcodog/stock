#!/usr/bin/env python
# 定时脚本，周一到周五 9:00~15:00 执行
# 频率：每分钟
# 监控价格是否在区间范围，若不在则发送钉钉通知

import requests
import redis
from datetime import datetime

from dao.dao import Dao
from dingtalk.ding import Ding
from decimal import Decimal
from utils import config
from utils import util

dao = Dao()
ding = Ding()
r = redis.StrictRedis(host=config.get("REDIS_HOST"),
                      port=config.get("REDIS_PORT"),
                      db=config.get("REDIS_DB"))

uri = "http://hq.sinajs.cn/list={}"
MESSAGE_TPL = "[ALERT] {} {}"
EXPIRE_TIME = 60 * 60 * 6    # 缓存8小时


def start():
    now = datetime.now()
    start = datetime.strptime(
        str(datetime.now().date()) + '9:30', '%Y-%m-%d%H:%M')
    if now < start:    # 9:30 前不执行，uri 爬取不了数据
        return

    list = get_monitor_list()
    if not list:
        return

    for row in list:
        code, monitor_type, buy_bias, sell_bias, buy_price, sell_price = row
        name, price = get_price(code)
        if price == 0:    # 获取不到价格或者其他原因
            continue

        if monitor_type == 0: # bias
            ave_close = get_22_close(code)
            if ave_close == 0:
                continue
            bias = round((price - ave_close) / ave_close * 100, 2)
            if bias <= buy_bias:
                notify(code, name, "BUY")
            if bias >= sell_bias:
                notify(code, name, "SELL")
        else: # price
            if price <= buy_price:
                notify(code, name, "BUY")
            if price >= sell_price:
                notify(code, name, "SELL")

def get_22_close(code):
    '''获取最近22日股价平均值'''
    date = datetime.today().strftime('%Y-%m-%d')
    data = dao.get_22_stock_data(code, date)
    if len(data) < 22:
        return 0

    prices = [row[0] for row in data]
    ave_close = util.average(prices)
    return ave_close


def notify(code, name, action):
    '''通知'''
    today = datetime.today().strftime('%Y-%m-%d')
    key = "{}:{}".format(code, today)
    cached = r.get(key)
    if cached is None:
        message = MESSAGE_TPL.format(name, action)
        ding.send(message)
        r.set(key, 1, ex=EXPIRE_TIME)


def get_monitor_list():
    '''获取监控名单'''
    rows = dao.get_price_monitor_list()
    return rows


def get_price(code):
    '''获取某股股价'''
    code = code.replace(".", "")
    url = uri.format(code)
    contents = requests.get(url).text
    infos = contents.split(",")
    if len(infos) <= 3:
        log.error('[monitor.get_price] error: {}', contents)
        return

    price = Decimal(infos[3])
    tmp_name = infos[0].split("=")
    name = tmp_name[1][1:]

    return (name, price)


if __name__ == '__main__':
    start()
