股票数据分析
=============

### 需求
主要对某股或指数的历史数据进行计算，获取中位数，平均数.


### 使用
设置配置信息
```
$ cp .env.example .env
$ cp conf.d/www.ini.example www.ini
```
> 用户登录目前是直接设置在配置文件的

安装依赖
```
$ python -m venv venv
$ source venv/bin/activate

(venv) $ pip install -r requirements.txt
(venv) $ uwsgi www.ini
```

配置 `supervisor`
```
$ cp conf.d/supervisor.stock.com.ini.example /etc/supervisord.d/stock.com.ini
```

配置 `nginx`
```
$ cp conf.d/nginx.stock.com.conf.example /etc/nginx/conf.d/stock.com.conf
```

定时任务
```
# 价格监控
* 9-14 * * 1-5 /data/www/stock/scripts/monitor

# 定时增量爬取
0 19 * * 1-5 /data/www/stock/scripts/crawl
```

### 项目说明
项目主要由两部分组成：`股票数据获取` 和 `提供 web 端数据接口`.

#### 数据获取
主要使用 [baostock](http://baostock.com/baostock/index.php/%E9%A6%96%E9%A1%B5) 的 SDK.

#### web
主要使用 `Flask` 框架
