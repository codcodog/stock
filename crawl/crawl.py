import baostock as bs
from datetime import date

from crawl.base import Base


class Crawl(Base):
    def inc_crawl(self):
        '''增量爬取'''
        for code in self.codes:
            start_date = self.dao.get_log_crawl_date(code)
            end_date = date.today().strftime("%Y-%m-%d")
            data = self.get_stock_data(code, start_date, end_date)
            if len(data) > 0:
                self.dao.multi_add_stock_data(data)

                # 爬取日志记录
                log_data = code, 0, '', end_date
                self.dao.log_crawl(log_data)
            else:
                msg = "获取股票数据为空，code: {}, start_date: {}, end_date: {}".format(
                    code, start_date, end_date)
                log_data = code, 1, msg, end_date
                self.dao.log_crawl(log_data)

    @staticmethod
    def run():
        crawl = Crawl()
        crawl.inc_crawl()
