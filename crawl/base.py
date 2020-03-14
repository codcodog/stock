import baostock as bs

from utils import config
from dao.dao import Dao


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
            "date,code,open,high,low,close,preclose,volume,amount",
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
