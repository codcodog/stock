import baostock as bs
import datetime
from datetime import date

from crawl.base import Base
from dao.dao import Dao
from utils import log


class Crawl(Base):
    def inc_crawl(self, code):
        '''增量爬取'''
        start = self.dao.get_log_crawl_date(code)
        # +1 day，防止已爬取的数据重复
        start = start + datetime.timedelta(days=1)

        start_date = start.strftime("%Y-%m-%d")
        end_date = date.today().strftime("%Y-%m-%d")

        try:
            data = self.get_stock_data(code, start_date, end_date)
            if len(data) > 0:
                self.dao.multi_add_stock_data(data)
                self.cal_22bias(data)
                self.incr_index_stock(data)

                # 爬取日志记录
                log_data = code, 0, '', end_date
                self.dao.log_crawl(log_data)
            else:
                msg = "获取股票数据为空，code: {}, start_date: {}, end_date: {}".format(
                    code, start_date, end_date)
                raise Exception(msg)
        except Exception as msg:
            log_data = code, 1, msg, end_date
            self.dao.log_crawl(log_data)

    @staticmethod
    def run():
        dao = Dao()
        codes = dao.get_stock_codes()
        if not codes:
            log.error("[Crawl.run] 获取 codes 失败.")
            return

        crawl = Crawl()
        for code, in codes:
            crawl.inc_crawl(code)
