import baostock as bs
from datetime import date

from crawl.base import Base
from utils import config


class Init(Base):
    def crawl_data(self, code, start_date):
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = date.today().strftime("%Y-%m-%d")
        data = self.get_stock_data(code, start_date, end_date)
        self.dao.multi_add_stock_data(data)

        # 更新初始化状态和跟踪状态
        self.dao.stock_inited(code)

        # 爬取日志记录
        log_data = code, 0, '', end_date
        self.dao.log_crawl(log_data)

    @staticmethod
    def run(code, start_date):
        init = Init()
        init.crawl_data(code, start_date)
