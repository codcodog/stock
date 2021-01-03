import pymysql

from utils import config
from utils import log


class Dao:
    def __init__(self):
        self.conn = pymysql.connect(config.get("DB_HOST"),
                                    config.get("DB_USER"),
                                    config.get("DB_PASSWORD"),
                                    config.get("DB_NAME"),
                                    autocommit=True)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
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

    def get_log_crawl_date(self, code):
        '''获取爬取日志最新日期'''
        sql = '''select `date` from `crawl_log` where `status` = 0 and `code` = "{}"
                order by `date` DESC limit 1'''.format(code)
        date, = self.get(sql)
        return date

    def get(self, sql):
        '''获取单条结果集'''
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result
        except Exception as err:
            log.error("SQL 执行失败，err:{}, sql:{}".format(err, sql))
            self.conn.rollback()
            return tuple()

    def select(self, sql):
        '''获取全部结果集'''
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except Exception as err:
            log.error("SQL 执行失败，err:{}, sql:{}".format(err, sql))
            self.conn.rollback()
            return []

    def get_close(self, code, start_date, end_date):
        '''获取 close 数据'''
        fields = 'date,close'
        return self.get_data(fields, code, start_date, end_date)

    def get_low(self, code, start_date, end_date):
        '''获取 low 数据'''
        fields = 'date,low'
        return self.get_data(fields, code, start_date, end_date)

    def get_high(self, code, start_date, end_date):
        '''获取 high 数据'''
        fields = 'date,high'
        return self.get_data(fields, code, start_date, end_date)

    def get_data(self, fields, code, start_date, end_date):
        '''获取股票数据'''
        sql = '''select {fields} from `stock_day` where `code`= '{code}' and `date` between
        '{start_date}' and '{end_date}' order by `date` asc'''.format(
            fields=fields, code=code, start_date=start_date, end_date=end_date)
        return self.select(sql)

    def get_bias(self, code, start_date, end_date):
        '''获取22日bias'''
        sql = '''select `date`, `bias` from `bias_22` where `code` = '{code}' and `date` between
        '{start_date}' and '{end_date}' order by `date` asc'''.format(
            code=code, start_date=start_date, end_date=end_date)
        return self.select(sql)

    def add_stock(self, code, code_name, start_date):
        '''新增股票'''
        pre_sql = '''INSERT INTO `stocks` (`code`, `code_name`, `init_date`) 
        VALUES ('{}', '{}', '{}')'''
        sql = pre_sql.format(code, code_name, start_date)
        return self.execute(sql)

    def get_stock_list(self):
        '''获取股票列表'''
        sql = '''select `id`, `code`, `code_name`, `is_init`, `status`
        from `stocks` order by `id` DESC'''
        return self.select(sql)

    def get_init_date(self, code):
        '''获取某股初始化日期'''
        sql = '''select `init_date` from `stocks` where `code`='{}' limit 1'''.format(
            code)
        return self.get(sql)

    def stock_inited(self, code):
        '''更新某股初始化状态，跟踪状态'''
        sql = '''update `stocks` set `is_init` = 1, `status` = 1 where `code`="{}"'''.format(
            code)
        self.execute(sql)

    def track_stock(self, code):
        '''跟踪某股'''
        sql = '''update `stocks` set `status` = 1 where `code`="{}"'''.format(
            code)
        self.execute(sql)

    def untrack_stock(self, code):
        '''不再跟踪某股'''
        sql = '''update `stocks` set `status` = 0 where `code`="{}"'''.format(
            code)
        self.execute(sql)

    def get_stock_info(self, code):
        '''获取某股基本信息'''
        sql = '''select `code`, `code_name`, `init_date` from `stocks`
        where `code`="{}" limit 1'''.format(code)
        return self.get(sql)

    def update_stock_info(self, code, name):
        sql = '''update `stocks` set `code_name` = "{}" where `code`="{}"'''.format(
            name, code)
        self.execute(sql)

    def get_stock_codes(self):
        '''获取需要跟踪并且已经初始化的股票代码'''
        sql = '''select `code` from `stocks` where `status` = 1 and `is_init` = 1'''
        return self.select(sql)

    def get_stock_log(self, code):
        '''获取某股同步日志'''
        sql = '''select `id`, `code`, `status`, `message`, `date`
        from `crawl_log` where `code`="{}" order by id DESC limit 5'''.format(
            code)
        return self.select(sql)

    def get_codes(self):
        '''获取 codes 列表'''
        sql = '''select `code`, `code_name` from `stocks` order by id ASC'''
        return self.select(sql)

    def delete_code(self, code):
        '''删除某股
        删除 stocks, stock_day, crawl_log, bias_22
        '''
        sql1 = '''delete from `stocks` where `code`="{}"'''.format(code)
        sql2 = '''delete from `stock_day` where `code`="{}"'''.format(code)
        sql3 = '''delete from `crawl_log` where `code`="{}"'''.format(code)
        sql4 = '''delete from `bias_22` where `code`="{}"'''.format(code)
        sql5 = '''delete from `price_monitor` where `code`="{}"'''.format(code)

        try:
            self.cursor.execute(sql1)
            self.cursor.execute(sql2)
            self.cursor.execute(sql3)
            self.cursor.execute(sql4)
            self.cursor.execute(sql5)
            self.conn.commit()
            return True
        except Exception as err:
            log.error("SQL 执行失败，err:{}, sql1:{}, sql2:{}, sql3:{}".format(
                err, sql1, sql2, sql3))
            self.conn.rollback()
            return False

    def get_22_stock_data(self, code, date):
        '''获取某股22日数据'''
        sql = "select close from `stock_day` where `code`='{}' and date < '{}' order by date DESC limit 22".format(
            code, date)
        return self.select(sql)

    def add_22_bias(self, *data):
        '''新增22日bias数据'''
        pre_sql = '''INSERT INTO `bias_22` (`code`, `date`, `bias`) 
        VALUES ('{}', '{}', {})'''
        sql = pre_sql.format(*data)
        return self.execute(sql)

    def save_price_monitor(self, code, ave_price, buy_bias, sell_bias, status):
        '''新增/更新 价格监控'''
        data = self.get_price_monitor(code)
        if len(data) == 0:    # 新增
            sql = '''INSERT INTO `price_monitor` (`code`, `ave`, `buy_bias`, `sell_bias`,
            `status`) VALUES ('{code}', {ave}, {buy_bias}, {sell_bias}, {status})'''.format(
                code=code,
                ave=ave_price,
                buy_bias=buy_bias,
                sell_bias=sell_bias,
                status=status)
            return self.execute(sql)
        else:    # 更新
            sql = '''update `price_monitor` set `ave`={}, `buy_bias`={}, `sell_bias`={},
            `status`={} where `code`="{}"'''.format(ave_price, buy_bias,
                                                    sell_bias, status, code)
            return self.execute(sql)

    def get_price_monitor(self, code):
        '''获取价格监控'''
        sql = '''select `code`, `ave`, `buy_bias`, `sell_bias`, `status`
        from `price_monitor` where `code`='{}' limit 1'''.format(code)
        return self.select(sql)

    def get_price_monitor_list(self):
        '''获取监控列表'''
        sql = '''select `code`, `ave`, `buy_bias`, `sell_bias` from
        `price_monitor` where `status`=1'''
        return self.select(sql)
