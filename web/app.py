import json
import math

from flask import Flask, g
from flask import request

from dao.dao import Dao, TYPE_STOCK, TYPE_FUND
from elastic.es import ES
from crawl.crawl import Crawl
from crawl.init import Init
from utils import log
from utils import config
from utils import util

app = Flask(__name__)
VOLUME_UINT = 10000 * 100 # 单位万


@app.before_request
def ping_mysql():
    '''确保 mysql 连接没有丢失'''
    g.dao = Dao()
    g.es = ES()


@app.route('/stock/data')
def get_data():
    '''获取股票数据'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")
    code_type = request.args.get('code_type', -1)
    code_type = int(code_type)
    if code_type != TYPE_STOCK and code_type != TYPE_FUND:
        return error("非法 code type")
    start_date = request.args.get('start_date', '')
    if start_date == '':
        return error('start date 不能为空')
    end_date = request.args.get('end_date', '')
    if end_date == '':
        return error('end date 不能为空')

    resp = {
        'low': 0,
        'mid': 0,
        'high': 0,
        'stock_data': [],
    }
    if code_type == TYPE_STOCK:
        resp = get_stock_data(code, start_date, end_date)
    elif code_type == TYPE_FUND:
        resp = get_fund_data(code, start_date, end_date)
    return success(resp)


def get_stock_data(code, start_date, end_date):
    result = g.es.get_stock_day_data(code, start_date, end_date)
    stock_data = result['hits']['hits']
    data = deal_es_data(stock_data)

    aggs_data = result['aggregations']
    aggs_result = deal_es_aggs_data(aggs_data)
    resp = {
        'low': aggs_result['low'],
        'mid': aggs_result['mid'],
        'high': aggs_result['high'],
        'low_volume': aggs_result['low_volume'],
        'mid_volume': aggs_result['mid_volume'],
        'high_volume': aggs_result['high_volume'],
        'stock_data': data,
    }
    return resp


def deal_es_data(data):
    '''处理 es 数据'''
    resp_data = []
    for row in data:
        item = {
            'date': row['_source']['date'],
            'close': round(float(row['_source']['close']), 2),
            'volume': round(float(row['_source']['volume'])/VOLUME_UINT, 2),
        }
        resp_data.append(item)
    return resp_data


def deal_es_aggs_data(data):
    '''处理 es 聚合数据'''
    high = data['high']['values']['80.0']
    if high is None:
        high = 0
    else:
        high = round(high, 2)
    low = data['low']['values']['20.0']
    if low is None:
        low = 0
    else:
        low = round(low, 2)
    mid = data['close']['values']['50.0']
    if mid is None:
        mid = 0
    else:
        mid = round(mid, 2)
    low_volume = data['low_volume']['values']['20.0']
    if low_volume is None:
        low_volume = 0
    else:
        low_volume = round(low_volume/VOLUME_UINT, 2)
    mid_volume = data['mid_volume']['values']['50.0']
    if mid_volume is None:
        mid_volume = 0
    else:
        mid_volume = round(mid_volume/VOLUME_UINT, 2)
    high_volume = data['high_volume']['values']['80.0']
    if high_volume is None:
        high_volume = 0
    else:
        high_volume = round(high_volume/VOLUME_UINT, 2)
    resp = {
        'low': low,
        'mid': mid,
        'high': high,
        'low_volume': low_volume,
        'mid_volume': mid_volume,
        'high_volume': high_volume,
    }
    return resp


def get_fund_data(code, start_date, end_date):
    result = g.es.get_fund_day_data(code, start_date, end_date)
    fund_data = result['hits']['hits']
    data = deal_es_fund_data(fund_data)

    aggs_data = result['aggregations']
    low, mid, high = deal_es_aggs_fund_data(aggs_data)
    resp = {
        'low': low,
        'mid': mid,
        'high': high,
        'prices': data,
    }
    return resp


def deal_es_fund_data(data):
    resp_data = []
    for row in data:
        item = {
            'date': row['_source']['date'],
            'close': round(float(row['_source']['price']), 3),
        }
        resp_data.append(item)
    return resp_data


def deal_es_aggs_fund_data(data):
    low = data['price']['values']['20.0']
    if low is None:
        low = 0
    else:
        low = round(low, 3)
    mid = data['price']['values']['50.0']
    if mid is None:
        mid = 0
    else:
        mid = round(mid, 3)
    high = data['price']['values']['80.0']
    if high is None:
        high = 0
    else:
        high = round(high, 3)
    return low, mid, high


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
    '''获取某股bias'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")
    start_date = request.args.get('start_date')
    if start_date == '':
        return error('start_date 不能为空')
    end_date = request.args.get('end_date')
    if end_date == '':
        return error('end_date 不能为空')

    data = g.es.get_bias_data(code, start_date, end_date)
    return success(deal_es_bias_data(data))


def deal_es_bias_data(data):
    deal_data = []
    for row in data['hits']['hits']:
        item = {
            'date': row['_source']['date'],
            'bias': round(float(row['_source']['bias']), 2),
        }
        deal_data.append(item)

    biases = [float(row['_source']['bias']) for row in data['hits']['hits']]
    win, levels = get_bias_level(biases)

    aggs = data['aggregations']['bias']['values']
    result = {
        'buy_bias': round(float(aggs['20.0']), 2),
        'sell_bias': round(float(aggs['80.0']), 2),
        'mid_bias': round(float(aggs['50.0']), 2),
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
    code_type = request.json.get('type', -1)
    if code_type != TYPE_STOCK and code_type != TYPE_FUND:
        return error("非法股票类型")

    done = g.dao.add_stock(code, code_name, code_type, start_date)
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
        g.es.remove_stock_data(code)
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
        id, code, code_name, code_type, is_init, status = row
        uint = {
            'id': id,
            'code': code,
            'name': code_name,
            'code_type': code_type,
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

    start_date, code_type = result
    Init.run(code, code_type, start_date)

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
    code, code_name, code_type, init_date = result
    data = {
        'code': code,
        'name': code_name,
        'code_type': code_type,
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
    code_type = request.json.get('code_type', -1)
    if code_type != TYPE_STOCK and code_type != TYPE_FUND:
        return error("非法 code type")
    crawl = Crawl()
    crawl.inc_crawl(code, code_type)
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
        code, name, code_type = row
        uint = {'code': code, 'name': name, 'code_type': code_type}
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


@app.route('/stock/data/rebuild', methods=['post'])
def rebuild_data():
    '''重建数据'''
    code = request.json.get('code', '')
    if code == '':
        return error("code 不能为空")

    done = g.dao.del_code(code)
    if not done:
        return error("重建失败")
    g.es.remove_stock_data(code)

    result = g.dao.get_init_date(code)
    if not result:
        log.error("获取 {} 初始化日期失败".format(code))
        return error("服务异常.")

    start_date, code_type = result
    Init.run(code, code_type, start_date)
    return success()


@app.route('/data/volume')
def get_volume():
    '''获取某股volume'''
    code = request.args.get('code', '')
    if code == '':
        return error("code 不能为空")
    start_date = request.args.get('start_date')
    if start_date == '':
        return error('start_date 不能为空')
    end_date = request.args.get('end_date')
    if end_date == '':
        return error('end_date 不能为空')

    data = g.es.get_volume_data(code, start_date, end_date)
    return success(deal_es_volume_data(data))


def deal_es_volume_data(data):
    deal_data = []
    for row in data['hits']['hits']:
        item = {
            'date': row['_source']['date'],
            'volume': round(float(row['_source']['volume'])/VOLUME_UINT, 2),
        }
        deal_data.append(item)

    aggs = data['aggregations']['volume']['values']
    if aggs['20.0'] is None:
        low_volume = 0
    else:
        low_volume = round(float(aggs['20.0'])/VOLUME_UINT, 2)
    if aggs['50.0'] is None:
        mid_volume = 0
    else:
        mid_volume = round(float(aggs['50.0'])/VOLUME_UINT, 2)
    if aggs['80.0'] is None:
        high_volume = 0
    else:
        high_volume = round(float(aggs['80.0'])/VOLUME_UINT, 2)

    result = {
        'low_volume': low_volume,
        'high_volume': high_volume,
        'mid_volume': mid_volume,
        'volumes': deal_data,
    }
    return result


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
