import baostock as bs
from datetime import date

from crawl.base import Base
from utils import config
from dao.dao import TYPE_STOCK, TYPE_FUND
from fund import eastmoney


class Init(Base):
    def crawl_data(self, code, code_type, start_date):
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = date.today().strftime("%Y-%m-%d")

        if code_type == TYPE_STOCK:
            self.crawl_stock_data(code, start_date, end_date)
        elif code_type == TYPE_FUND:
            self.crawl_fund_data(code, start_date, end_date)
        else:
            return

        # 更新初始化状态和跟踪状态
        self.dao.stock_inited(code)

        # 爬取日志记录
        log_data = code, 0, '', end_date
        self.dao.log_crawl(log_data)

    def crawl_stock_data(self, code, start_date, end_date):
        '''爬取股票数据'''
        data = self.get_stock_data(code, start_date, end_date)

        self.dao.multi_add_stock_data(data)
        print('添加个股数据完成')

        self.cal_22bias(data)
        print('计算 bias 完成')

        self.incr_index_stock(data)
        print('es 索引完成')

    def crawl_fund_data(self, code, start_date, end_date):
        '''爬取基金数据'''
        data = eastmoney.get_data(code, start_date, end_date)

        self.dao.multi_add_fund_data(data)
        print('添加基金数据完成')

        self.cal_fund_22bias(data)
        print('计算 bias 完成')

        self.incr_index_fund(data)
        print('es 索引完成')

    @staticmethod
    def run(code, code_type, start_date):
        init = Init()
        init.crawl_data(code, code_type, start_date)
