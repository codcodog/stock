import baostock as bs
from datetime import date

from crawl.base import Base
from utils import config


class Init(Base):
    def crawl_data(self):
        start_date = config.get("INIT_START_DATE")
        if start_date is None:
            print("初始化开始日期没有配置: .env->INIT_START_DATE is null")
            raise SystemExit

        end_date = date.today().strftime("%Y-%m-%d")
        for code in self.codes:
            data = self.get_stock_data(code, start_date, end_date)
            self.dao.multi_add_stock_data(data)

            # 爬取日志记录
            log_data = code, 0, '', end_date
            self.dao.log_crawl(log_data)

    @staticmethod
    def run():
        init = Init()
        init.crawl_data()
