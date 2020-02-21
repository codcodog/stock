import os
from dotenv import load_dotenv


# 先加载 .env 文件
def pre_dep():
    version = os.getenv("STOCK_VERSION")
    if version is None:
        load_dotenv()


pre_dep()


def get(name):
    return os.getenv(name)


def get_mysql_ins():
    pass
