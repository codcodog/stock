import json

import numpy as np
from flask import Flask
from flask import request

from dao.dao import Dao
from crawl.crawl import Crawl

app = Flask(__name__)
dao = Dao()


@app.route('/data/close')
def get_close():
    '''获取某股 close 数据'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = dao.get_close(code, start_date, end_date)
    return success(deal_data(data))


@app.route('/data/low')
def get_low():
    '''获取某股 low 数据'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = dao.get_low(code, start_date, end_date)
    return success(deal_data(data))


@app.route('/data/high')
def get_high():
    '''获取某股 high 数据'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = dao.get_high(code, start_date, end_date)
    return success(deal_data(data))


def deal_data(data):
    '''处理数据'''
    prices = [row[1] for row in data]
    ave = float(round(average(prices), 2))
    mid = float(round(median(prices), 2))
    deal_data = []
    for row in data:
        date, price = row
        uint = {
            'date': date.strftime("%Y-%m-%d"),
            'price': float(round(price, 2)),
        }
        deal_data.append(uint)

    result = {
        'ave': ave,
        'mid': mid,
        'prices': deal_data,
    }
    return result


@app.route('/crawl')
def crawl():
    '''手动触发爬取数据'''
    Crawl.run()
    return success(message='爬取完成')


def error(message):
    '''错误信息'''
    result = {
        'code': 1,
        'message': message,
        'data': [],
    }
    return json.dumps(result)


def success(data=[], message=''):
    '''成功信息'''
    result = {
        'code': 20000,
        'message': message,
        'data': data,
    }
    return json.dumps(result)


def average(data):
    '''求取平均数'''
    if len(data) == 0:
        return 0

    data.sort()
    if len(data) > 2:
        filter_data = data[1:-1]
    else:
        filter_data = data
    return np.mean(filter_data)


def median(data):
    '''求取中数'''
    if len(data) == 0:
        return 0
    return np.median(data)
