import baostock as bs

from decimal import *

from utils import config
from dao.dao import Dao
from utils import util


class Base:
    def __init__(self):
        # 登录系统
        lg = bs.login()
        if lg.error_code != '0':
            message = "error_code: {}\nerror_msg: {}".format(
                lg.error_code, lg.error_msg)
            raise Exception(message)

        self.dao = Dao()

    def __del__(self):
        # 登出系统
        bs.logout()

    def get_stock_data(self, code, start_date, end_date):
        '''获取每天股票数据'''
        rs = bs.query_history_k_data_plus(
            code,
            "date,code,open,high,low,close,preclose,volume,amount,peTTM",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="3")
        if rs.error_code != '0':
            message = "error_code: {}, error_msg: {}".format(
                rs.error_code, rs.error_msg)
            raise Exception(message)

        # 存储数据
        data = []
        while rs.next():
            data.append(rs.get_row_data())
        return data

    def cal_22bias(self, data):
        '''计算22日bias'''
        for stock_data in data:
            date, code, _, _, _, close, *not_use = tuple(stock_data)
            close = Decimal(close)
            data = self.dao.get_22_stock_data(code, date)
            if len(data) < 22:
                continue
            prices = [row[0] for row in data]
            ave_close = util.average(prices)
            bias = round((close - ave_close) / ave_close * 100, 2)
            self.dao.add_22_bias(code, date, bias)
