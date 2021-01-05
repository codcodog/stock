import json
import math

import numpy as np
from flask import Flask
from flask import request

from dao.dao import Dao
from crawl.crawl import Crawl
from crawl.init import Init
from utils import log
from utils import config
from utils import util

app = Flask(__name__)
dao = Dao()


@app.before_request
def ping_mysql():
    '''确保 mysql 连接没有丢失'''
    dao.conn.ping(reconnect=True)


@app.route('/data/close')
def get_close():
    '''获取某股 close 数据'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = dao.get_close(code, start_date, end_date)
    return success(deal_data(data, 'close'))


@app.route('/data/low')
def get_low():
    '''获取某股 low 数据'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = dao.get_low(code, start_date, end_date)
    return success(deal_data(data, 'low'))


@app.route('/data/high')
def get_high():
    '''获取某股 high 数据'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = dao.get_high(code, start_date, end_date)
    return success(deal_data(data, 'high'))


@app.route('/data/bias')
def get_bias():
    '''获取某股22日bias'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = dao.get_bias(code, start_date, end_date)
    return success(deal_bias_data(data))


def deal_bias_data(data):
    '''处理bias数据'''
    biases = [row[1] for row in data]
    data_num = len(biases)
    if data_num < 10:    # 确保数据有两周
        buy_bias = 0
        sell_bias = 0
    index = round(data_num * 0.1)

    biases.sort()
    buy_bias = float(round(biases[index], 2))
    sell_bias = float(round(biases[-(index + 1)], 2))

    deal_data = []
    for row in data:
        date, bias = row
        uint = {
            'date': date.strftime("%Y-%m-%d"),
            'bias': float(round(bias, 2)),
        }
        deal_data.append(uint)

    result = {
        'buy_bias': buy_bias,
        'sell_bias': sell_bias,
        'biases': deal_data,
    }
    return result


def deal_data(data, data_type):
    '''处理数据'''
    prices = [row[1] for row in data]
    ave = float(round(util.average(prices), 2))
    mid = float(round(util.median(prices), 2))

    prices.sort()
    index = math.floor(len(prices)*0.2)
    if data_type == 'low':
        price28 = prices[index]
    elif data_type == 'high':
        price28 = prices[-(index+1)]
    else:
        price28 = 0
    price28 = float(round(price28, 2))

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
        'price28': price28,
        'prices': deal_data,
    }
    return result


@app.route('/stock/add', methods=['post'])
def add():
    '''新增股票'''
    code = request.json.get('code', '')
    if code == '':
        return error("code 不能为空")
    code_name = request.json.get('name', '')
    if code_name == '':
        return error("code_name 不能为空")
    start_date = request.json.get('startDate', '')
    if start_date == '':
        return error("start_date 不能为空")

    done = dao.add_stock(code, code_name, start_date)
    if done:
        return success()
    else:
        return error("添加失败")


@app.route('/stock/delete', methods=['post'])
def delete():
    '''删除某股'''
    code = request.json.get('code', '')
    if code == '':
        return error("code 不能为空")
    done = dao.delete_code(code)
    if done:
        return success()
    else:
        return error("删除失败")


@app.route('/stock/list')
def list():
    '''股票列表'''
    rows = dao.get_stock_list()
    data = []
    for row in rows:
        id, code, code_name, is_init, status = row
        uint = {
            'id': id,
            'code': code,
            'name': code_name,
            'isInit': is_init,
            'status': status
        }
        data.append(uint)

    return success(data)


@app.route('/price/monitor/save', methods=['post'])
def price_monitor_save():
    '''保存价格监控'''
    errs = validate_price_monitor()
    if errs != '':
        return errs

    code = request.json.get('code', '')
    status = request.json.get('status')
    ave_price = request.json.get('ave_price', 0)
    buy_bias = request.json.get('buy_bias', 0)
    sell_bias = request.json.get('sell_bias', 0)
    done = dao.save_price_monitor(code, ave_price, buy_bias, sell_bias, status)
    if done:
        return success()
    return error("保存失败")


@app.route('/price/monitor')
def price_monitor():
    '''获取价格监控'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")

    rows = dao.get_price_monitor(code)
    if len(rows) > 0:
        row = rows[0]
        _, ave, buy_bias, sell_bias, status = row
        data = {
            'status': status,
            'ave_price': float(round(ave, 2)),
            'buy_bias': float(round(buy_bias, 2)),
            'sell_bias': float(round(sell_bias, 2)),
        }
        return success(data)
    else:
        return success({})


def validate_price_monitor():
    code = request.json.get('code', '')
    if code == '':
        return error("code 不能为空")
    status = request.json.get('status')
    if status != 0 and status != 1:
        return error("非法 status 值")
    ave_price = request.json.get('ave_price', 0)
    if ave_price == 0:
        return error("ave_price 不能为空")
    buy_bias = request.json.get('buy_bias', 0)
    if buy_bias == 0:
        return error("buy_bias 不能为空")
    sell_bias = request.json.get('sell_bias', 0)
    if sell_bias == 0:
        return error("sell_bias 不能为空")
    return ''


@app.route('/crawl')
def crawl():
    '''手动触发爬取数据'''
    Crawl.run()
    return success(message='爬取完成')


@app.route('/stock/init', methods=['post'])
def init():
    '''初始化股票数据'''
    code = request.json.get('code', '')
    if code == '':
        return error("code 不能为空")

    result = dao.get_init_date(code)
    if not result:
        log.error("获取 {} 初始化日期失败".format(code))
        return error("服务异常.")

    start_date, = result
    Init.run(code, start_date)

    return success()


@app.route('/stock/track', methods=['post'])
def track():
    '''跟踪该股'''
    code = request.json.get('code', '')
    if code == '':
        return error("code 不能为空")
    dao.track_stock(code)
    return success()


@app.route('/stock/untrack', methods=['post'])
def untrack():
    '''不再跟踪某股'''
    code = request.json.get('code', '')
    if code == '':
        return error("code 不能为空")
    dao.untrack_stock(code)
    return success()


@app.route('/stock/info')
def info():
    '''获取某股信息'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")
    result = dao.get_stock_info(code)
    if not result:
        log.error("获取 {} 基本信息失败".format(code))
        return error("服务异常.")
    code, code_name, init_date = result
    data = {
        'code': code,
        'name': code_name,
        'startDate': init_date.strftime("%Y-%m-%d"),
    }
    return success(data)


@app.route('/stock/info/update', methods=['post'])
def update_info():
    '''更新某股信息'''
    code = request.json.get('code', '')
    if code == '':
        return error("code 不能为空")
    code_name = request.json.get('name', '')
    if code_name == '':
        return error("name 不能为空")
    dao.update_stock_info(code, code_name)
    return success()


@app.route('/stock/sync/incr', methods=['post'])
def incr_sync():
    '''增量同步'''
    code = request.json.get('code', '')
    if code == '':
        return error("code 不能为空")
    crawl = Crawl()
    crawl.inc_crawl(code)
    return success()


@app.route('/stock/log')
def log_list():
    '''获取某股同步日志'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")
    rows = dao.get_stock_log(code)
    data = []
    for row in rows:
        id, code, status, message, date = row
        uint = {
            'id': id,
            'code': code,
            'status': status,
            'message': message,
            'date': date.strftime("%Y-%m-%d"),
        }
        data.append(uint)
    return success(data)


@app.route('/stock/codes')
def get_codes():
    '''获取 codes 列表'''
    result = dao.get_codes()
    data = []
    for row in result:
        code, name = row
        uint = {'code': code, 'name': name}
        data.append(uint)
    return success(data)


@app.route('/user/login', methods=['post'])
def login():
    '''登录'''
    username = request.json.get('username', '')
    password = request.json.get('password', '')

    if username != config.get('USERNAME'):
        return error("帐号不存在.")
    if password != config.get('PASSWORD'):
        return error("密码错误.")
    data = {
        'token': config.get('TOKEN'),
    }
    return success(data)


@app.route('/user/logout', methods=['post'])
def logout():
    '''退出'''
    return success()


@app.route('/user/info')
def user_info():
    '''用户信息'''
    token = request.args.get('token', '')
    if token != config.get('TOKEN'):
        return error("用户认证失败.")
    data = {
        'name': config.get("USERNAME"),
        'avatar': config.get("AVATAR"),
    }
    return success(data)


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
