import pymysql

from utils import config
from utils import log


class Dao:
    def __init__(self):
        self.conn = pymysql.connect(config.get("DB_HOST"),
                                    config.get("DB_USER"),
                                    config.get("DB_PASSWORD"),
                                    config.get("DB_NAME"))
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def multi_add_stock_data(self, data):
        '''批量新增股票数据'''
        pre_sql = '''INSERT INTO `stock_day` (`date`, `code`, `open`,
                    `high`, `low`, `close`, `preclose`, `volume`, `amount`)
                    VALUES '''
        tpl = "('{}', '{}', {}, {}, {}, {}, {}, {}, {}),"
        multi_tpl = ""
        i = 0
        for stock_data in data:
            multi_tpl += tpl.format(*stock_data)
            i = i + 1
            if i % 200 == 0 or i == len(data):
                sql = pre_sql + multi_tpl
                sql = sql.rstrip(",")
                multi_tpl = ""
                self.execute(sql)

    def log_crawl(self, data):
        '''爬取日志记录'''
        tpl = '''INSERT INTO `crawl_log` (`code`, `status`, `message`, `date`) VALUES ('{}', {}, '{}', '{}')'''
        sql = tpl.format(*data)
        self.execute(sql)

    def execute(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception as err:
            log.error("SQL 执行失败，err:{}, sql:{}".format(err, sql))
            self.conn.rollback()
            return False
