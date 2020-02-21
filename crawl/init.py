import baostock as bs

CODES = ["sh.000016"]


class Init:
    def __init__(self):
        # 登录系统
        lg = bs.login()
        if lg.error_code != '0':
            print('login respond error_code:' + lg.error_code)
            print('login respond  error_msg:' + lg.error_msg)

    def __del__(self):
        # 登出系统
        bs.logout()

    def crawl_data(self):
        start_date = '2020-02-17'
        end_date = '2020-02-17'
        for code in CODES:
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
            while rs.next():
                print(rs.get_row_data())

    @staticmethod
    def run():
        init = Init()
        init.crawl_data()
