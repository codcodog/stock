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
            print(message)
            raise SystemExit
        self.dao = Dao()
        self.codes = self.get_codes()

    def __del__(self):
        # 登出系统
        bs.logout()

    def get_codes(self):
        '''获取股票代号'''
        return config.get("STOCK_CODES").split(",")

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
            print('query_history_k_data_plus respond error_code:' +
                  rs.error_code)
            print('query_history_k_data_plus respond  error_msg:' +
                  rs.error_msg)
            raise SystemExit

        # 存储数据
        data = []
        while rs.next():
            data.append(rs.get_row_data())
        return data
