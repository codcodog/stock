from elastic.es import ES, STOCK_ALIAS_INDEX_NAME
from dao.dao import Dao
from time import localtime, strftime, time
from datetime import datetime

es = ES()
dao = Dao()


def index_all_stocks():
    '''全量索引数据'''
    # 创建索引
    index_name = "stock.{}".format(strftime("%Y%m%d%H%M%S", localtime()))
    es.create_index(index_name)

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

    es.create_alias(index_name)


def incr_index_stock(data):
    '''增量索引数据'''
    stocks = []
    for item in data:
        _, code, open, high, low, close, preclose, volume, amount, turn, pe_ttm, d, *rest = item
        stock = {
            '_index': STOCK_ALIAS_INDEX_NAME,
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


if __name__ == '__main__':
    index_all_stocks()
