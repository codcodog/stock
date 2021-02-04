import json
import math

from flask import Flask, g
from flask import request

from dao.dao import Dao
from crawl.crawl import Crawl
from crawl.init import Init
from utils import log
from utils import config
from utils import util

app = Flask(__name__)


@app.before_request
def ping_mysql():
    '''确保 mysql 连接没有丢失'''
    g.dao = Dao()


@app.route('/data/close')
def get_close():
    '''获取某股 close 数据'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = g.dao.get_close(code, start_date, end_date)
    return success(deal_data(data, 'close'))


@app.route('/data/low')
def get_low():
    '''获取某股 low 数据'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = g.dao.get_low(code, start_date, end_date)
    return success(deal_data(data, 'low'))


@app.route('/data/high')
def get_high():
    '''获取某股 high 数据'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = g.dao.get_high(code, start_date, end_date)
    return success(deal_data(data, 'high'))


@app.route('/data/ttm')
def get_ttm():
    '''获取 ttm'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")
    start_date = request.args.get('start_date')
    if start_date == '':
        return error('start_date 不能为空')
    end_date = request.args.get('end_date')
    if end_date == '':
        return error('end_date 不能为空')

    data = g.dao.get_ttm(code, start_date, end_date)
    return success(deal_ttm_data(data))


def deal_ttm_data(data):
    '''处理 ttm 数据'''
    if len(data) == 0:
        return []

    ttms = [row[1] for row in data]
    data_num = len(ttms)
    index = round(data_num * 0.1)

    ttms.sort()
    buy_ttm = float(round(ttms[index], 2))
    sell_ttm = float(round(ttms[-(index + 1)], 2))
    mid_ttm = float(round(util.median(ttms), 2))

    deal_data = []
    for row in data:
        date, ttm = row
        uint = {
            'date': date.strftime("%Y-%m-%d"),
            'ttm': float(round(ttm, 2)),
        }
        deal_data.append(uint)

    result = {
        'buy_ttm': buy_ttm,
        'sell_ttm': sell_ttm,
        'mid_ttm': mid_ttm,
        'ttms': deal_data,
    }
    return result


@app.route('/data/bias')
def get_bias():
    '''获取某股22日bias'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")
    start_date = request.args.get('start_date')
    if start_date == '':
        return error('start_date 不能为空')
    end_date = request.args.get('end_date')
    if end_date == '':
        return error('end_date 不能为空')

    data = g.dao.get_bias(code, start_date, end_date)
    return success(deal_bias_data(data))


def deal_bias_data(data):
    '''处理bias数据'''
    if len(data) == 0:
        return []

    biases = [row[1] for row in data]
    win, levels = get_bias_level(biases)

    data_num = len(biases)
    index = round(data_num * 0.1)

    biases.sort()
    buy_bias = float(round(biases[index], 2))
    sell_bias = float(round(biases[-(index + 1)], 2))
    mid_bias = float(round(util.median(biases), 2))

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
        'mid_bias': mid_bias,
        'biases': deal_data,
        'levels': levels,
        'win': win,
    }
    return result


def get_bias_level(biases):
    '''获取 bias 各个 level 分布
    小于-10, -5~-10, -3~-5, -1~-3
    -1~1, 1~3, 3~5, 5~10, 大于10
    '''
    levels = {
        '-10': 0,
        '-10~-5': 0,
        '-3~-5': 0,
        '-1~-3': 0,
        '-1~1': 0,
        '1~3': 0,
        '3~5': 0,
        '5~10': 0,
        '10': 0,
    }
    win_num = 0
    for bias in biases:
        if bias < -10:
            levels['-10'] += 1
        elif -10 <= bias < -5:
            levels['-10~-5'] += 1
        elif -5 <= bias < -3:
            levels['-3~-5'] += 1
        elif -3 <= bias < -1:
            levels['-1~-3'] += 1
        elif -1 <= bias <= 1:
            levels['-1~1'] += 1
        elif 1 < bias < 3:
            win_num += 1
            levels['1~3'] += 1
        elif 3 <= bias < 5:
            win_num += 1
            levels['3~5'] += 1
        elif 5 <= bias < 10:
            win_num += 1
            levels['5~10'] += 1
        else:
            win_num += 1
            levels['10'] += 1
    win_per = round(win_num / len(biases) * 100, 2)
    win = "{}%".format(win_per)
    return (win, levels)


def deal_data(data, data_type):
    '''处理数据'''
    prices = [row[1] for row in data]
    ave = float(round(util.average(prices), 2))
    mid = float(round(util.median(prices), 2))

    prices.sort()
    index = math.floor(len(prices) * 0.2)
    if data_type == 'low':
        price28 = prices[index]
    elif data_type == 'high':
        price28 = prices[-(index + 1)]
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

    done = g.dao.add_stock(code, code_name, start_date)
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
    done = g.dao.delete_code(code)
    if done:
        return success()
    else:
        return error("删除失败")


@app.route('/stock/list')
def list():
    '''股票列表'''
    page = request.args.get('page', 1)
    size = request.args.get('size', 10)
    name = request.args.get('name', '')
    total, rows = g.dao.get_stock_list(name, int(page), int(size))
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
    resp = {
        'data': data,
        'total': total,
    }

    return success(resp)


@app.route('/price/monitor/save', methods=['post'])
def price_monitor_save():
    '''保存价格监控'''
    errs = validate_price_monitor()
    if errs != '':
        return errs

    code = request.json.get('code', '')
    monitor_type = request.json.get('type')
    status = request.json.get('status')
    message = request.json.get('message', '')
    buy_bias = request.json.get('buy_bias', 0)
    sell_bias = request.json.get('sell_bias', 0)
    buy_price = request.json.get('buy_price', 0)
    sell_price = request.json.get('sell_price', 0)
    done = g.dao.save_price_monitor(code, monitor_type, buy_bias, sell_bias,
                                    buy_price, sell_price, message, status)
    if done:
        return success()
    return error("保存失败")


@app.route('/price/monitor')
def price_monitor():
    '''获取价格监控'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")

    rows = g.dao.get_price_monitor(code)
    if len(rows) > 0:
        row = rows[0]
        _, monitor_type, buy_bias, sell_bias, buy_price, sell_price, message, status = row
        data = {
            'status': status,
            'type': monitor_type,
            'buy_bias': float(round(buy_bias, 2)),
            'sell_bias': float(round(sell_bias, 2)),
            'buy_price': float(round(buy_price, 2)),
            'sell_price': float(round(sell_price, 2)),
            'message': message,
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

    monitor_type = request.json.get('type')
    buy_price = request.json.get('buy_price', 0)
    if monitor_type == 1 and buy_price == 0:
        return error("buy_price 不能为空/0")
    sell_price = request.json.get('sell_price', 0)
    if monitor_type == 1 and sell_price == 0:
        return error("sell_price 不能为空/0")
    buy_bias = request.json.get('buy_bias', 0)
    sell_bias = request.json.get('sell_bias', 0)
    if monitor_type == 0 and buy_bias == 0:
        return error("buy_bias 不能为空/0")
    if monitor_type == 0 and sell_bias == 0:
        return error("sell_bias 不能为空/0")
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

    result = g.dao.get_init_date(code)
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
    g.dao.track_stock(code)
    return success()


@app.route('/stock/untrack', methods=['post'])
def untrack():
    '''不再跟踪某股'''
    code = request.json.get('code', '')
    if code == '':
        return error("code 不能为空")
    g.dao.untrack_stock(code)
    return success()


@app.route('/stock/info')
def info():
    '''获取某股信息'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")
    result = g.dao.get_stock_info(code)
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
    g.dao.update_stock_info(code, code_name)
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
    rows = g.dao.get_stock_log(code)
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
    result = g.dao.get_codes()
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
