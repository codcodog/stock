import re
import requests
from bs4 import BeautifulSoup

# 天天基金数据接口
uri = 'https://fundf10.eastmoney.com/F10DataApi.aspx?type=lsjz&code={code}&page={page}&sdate={start_date}&edate={end_date}&per=20'


def get(url):
    res = requests.get(url)
    return res.text


def get_data(code, start_date, end_date):
    '''获取数据'''
    pages = get_total_pages(code, start_date, end_date)
    page = 1
    records = []
    while page <= pages:
        url = uri.format(code=code,
                         page=page,
                         start_date=start_date,
                         end_date=end_date)
        html = get(url)
        soup = BeautifulSoup(html, 'html.parser')

        # 获取数据
        for row in soup.findAll("tbody")[0].findAll("tr"):
            tds = row.findAll('td')
            date = tds[0].contents[0]
            price = round(float(tds[1].contents[0]), 3)
            records.append((code, date, price))

        page += 1
    return records


def get_total_pages(code, start_date, end_date):
    page = 1
    url = uri.format(code=code,
                     page=page,
                     start_date=start_date,
                     end_date=end_date)
    html = get(url)
    soup = BeautifulSoup(html, 'html.parser')

    # 获取总页数
    pattern = re.compile(r'pages:(.*),')
    result = re.search(pattern, html).group(1)
    return int(result)
