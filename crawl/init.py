import baostock as bs
from datetime import date

from dao.dao import Dao
from utils import config


class Init:
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

    def crawl_data(self):
        start_date = config.get("INIT_START_DATE")
        if start_date is None:
            print("初始化开始日期没有配置: .env->INIT_START_DATE is null")
            raise SystemExit
        end_date = date.today().strftime("%Y-%m-%d")
        for code in self.codes:
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
            self.dao.multi_add_stock_data(data)

            # 爬取日志记录
            log_data = code, 0, '', end_date
            self.dao.log_crawl(log_data)

    @staticmethod
    def run():
        init = Init()
        init.crawl_data()
