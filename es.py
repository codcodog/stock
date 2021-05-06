import sys
from elastic.es import ES, STOCK_ALIAS_INDEX_NAME, BIAS_ALIAS_INDEX_NAME
from dao.dao import Dao
from time import localtime, strftime, time
from datetime import datetime

es = ES()
dao = Dao()


def index_all_stocks():
    '''全量索引数据'''
    # 创建索引
    index_name = "stock.{}".format(strftime("%Y%m%d%H%M%S", localtime()))
    es.create_index(index_name, 'stock')

    codes = dao.get_codes()
    for code, _ in codes:
        data = dao.get_stock_day_data(code)
        stocks = []
        for item in data:
            _, code, open, high, low, close, preclose, volume, amount, turn, pe_ttm, d, *rest = item
            stock = {
                '_index': index_name,
                '_source': {
                    'code': code,
                    'open': open,
                    'high': high,
                    'low': low,
                    'close': close,
                    'preclose': preclose,
                    'volume': volume,
                    'amount': amount,
                    'turn': turn,
                    'pe_ttm': pe_ttm,
                    'date': d.strftime("%Y-%m-%d"),
                }
            }
            stocks.append(stock)
        es.bulk_index(stocks)
    es.create_alias(index_name, STOCK_ALIAS_INDEX_NAME)


def index_bias():
    '''全量索引 bias'''
    index_name = "bias.{}".format(strftime("%Y%m%d%H%M%S", localtime()))
    es.create_index(index_name, 'bias')

    codes = dao.get_codes()
    for code, _ in codes:
        data = dao.get_bias_data(code)
        bias_data = []
        for item in data:
            _, code, d, bias = item
            es_data = {
                '_index': index_name,
                '_source': {
                    'code': code,
                    'date': d.strftime("%Y-%m-%d"),
                    'bias': bias,
                }
            }
            bias_data.append(es_data)
        es.bulk_index(bias_data)
    es.create_alias(index_name, BIAS_ALIAS_INDEX_NAME)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("invalid params")
        raise SystemExit

    t = sys.argv[1]
    if t == 'stock':
        index_all_stocks()
    elif t == 'bias':
        index_bias()
    else:
        print("invalid type")
