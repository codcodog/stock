股票数据分析
=============

### 需求
主要对某股或指数的历史数据进行计算，获取中位数，平均数.


### 使用
设置配置信息
```
$ cp .env.example .env
```
> 用户登录目前是直接设置在配置文件的

安装依赖
```
$ python -m venv venv
$ source venv/bin/activate

(venv) $ pip install -r requirements.txt
(venv) $ uwsgi www.ini
```


### 项目说明
项目主要由两部分组成：`股票数据获取` 和 `提供 web 端数据接口`.

#### 数据获取
主要使用 [baostock](http://baostock.com/baostock/index.php/%E9%A6%96%E9%A1%B5) 的 SDK.

#### web
主要使用 `Flask` 框架
