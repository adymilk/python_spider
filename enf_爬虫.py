import datetime
import re
import time

import requests
from bs4 import BeautifulSoup
import urllib.request
import csv
from lxml import etree
import os

def log(str):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + str)


log('采集系统启动成功✨🌈😀...')
urlpage = input('请输入你要采集的网站链接：')
# 把网址 URL 存在变量里
# urlpage = 'https://www.enf.com.cn/directory/software'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/80.0.3987.149 Safari/537.36 '
}

page = urllib.request.urlopen(urlpage)
soup = BeautifulSoup(page, 'html.parser')
title = soup.title.text
title = ''.join(title.split())
log('页面加载完成，网站标题是：'+title)
with open(os.path.abspath("爬虫采集到的数据表.csv"), "w", newline='') as f:
    writer = csv.writer(f)
    # 先写入columns_name
    writer.writerow(['company', 'address', 'website', 'telephone', 'email'])
pagination = soup.find('ul', attrs={'class': 'enf-pagination'})
paginations = len(pagination.find_all('li')) - 1
log('系统检测到一共有' + str(paginations) + '页数据')
for pagination in range(paginations):
    time.sleep(2)
    pagination = str(pagination + 1)
    log('开始加载第'+ pagination +'页数据')
    page = urllib.request.urlopen(urlpage+'?page='+pagination)
    soup = BeautifulSoup(page, 'html.parser')
    # 在表格中查找数据
    table = soup.find('table', attrs={'class': 'enf-list-table'})
    results = table.find_all('tr')
    links = []
    companies = []
    log('加载成功！当前页面检测到需要采集的公司数量有：' + str(len(results)))
    # 遍历所有数据
    for index in range(len(results)):
        result = results[index]
        # 找到每一个 td 单元格的内容
        data = result.find('td').find('a')
        link = str(data.get('href')).strip()
        company = str(data.getText()).strip()
        links.append(link)
        companies.append(company)
        # 如果该单元格无数据，则跳过
        if len(data) == 0:
            continue


    for index, link in enumerate(links):
        company = companies[index]
        log('开始采集第'+ pagination +'页第'+ str(index +1) + '条数据.公司名称：'+company)
        # 获取网页内容，把 HTML 数据保存在 page 变量中
        page = urllib.request.urlopen(link)
        # 用 Beautiful Soup 解析 html 数据，
        # 并保存在 soup 变量里
        soup = BeautifulSoup(page, 'html.parser')
        # 在表格中查找数据
        try:
            table = soup.find('div', attrs={'class': 'enf-company-profile-info-main-spec'})
            address = table.find('td', attrs={'itemprop': 'address'}).getText().strip()
            website = table.find('a', attrs={'itemprop': 'url'}).getText().strip()
            telephone = table.find('td', attrs={'itemprop': 'telephone'})
        except:
            log('【警告⚠】无法识别的格式，已忽略' + company)
            continue

        try:
            telephoneSpan = telephone.find('span')
            email = table.find('td', attrs={'itemprop': 'email'})
            emailSpan = email.find('span')
        except:
            email = 'null'

        if telephoneSpan is not None:
            pattern = re.compile(r"\'(.*?)\'")
            token = pattern.findall(str(telephoneSpan))
            api = "https://www.enf.com.cn/api/company-phone/" + token[0]
            telephone = requests.get(api, headers=headers).text
            time.sleep(1)
        else:
            telephone = telephone.getText().strip()

        if emailSpan is not None:
            pattern = re.compile(r"\'(.*?)\'")
            token = pattern.findall(str(emailSpan))
            api = "https://www.enf.com.cn/company_email/" + token[0]
            email = requests.get(api, headers=headers).text
            time.sleep(1)
        else:
            try:
                email.getText().strip()
            except:
                email = 'null'

        if telephone == '已达到每日请求限制' or email == '已达到每日请求限制':
            log('【警告⚠】您的IP地址已达到每日请求限制，请手动切换IP后按任意键继续采集')
            input()

        with open("爬虫采集到的数据表.csv", "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([company, address, website, telephone, email])
        log('第' + str(index + 1) + '条数据采集完毕，保存成功！✨🌈✨🌈')
log('数据采集完毕，感谢您的使用！')
