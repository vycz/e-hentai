#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Orange'

import sys
import os
import multiprocessing
from urllib import request, parse
import re
from bs4 import BeautifulSoup
import libtorrent as bt
import pymysql
import time
success_count = 0


def getPages(html):
    return re.findall(r'onclick="return false">(\d+)</a>', html)


def get_url(pages, key):
    data = {
        'page': pages,
        'f_doujinshi': 'on',
        'f_manga': 'on',
        'f_artistcg': 'on',
        'f_gamecg': 'on',
        'f_western': 'on',
        'f_non-h': 'on',
        'f_imageset': 'on',
        'f_cosplay': 'on',
        'f_asianporn': 'on',
        'f_misc': 'on',
        'f_search': key,
        'f_apply': 'Apply Filter'
    }
    url_parame = parse.urlencode(data)
    url = "https://e-hentai.org/?"
    url_all = url+url_parame
    return url_all


def get_html(url):
    try:
        req = request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')
        with request.urlopen(req) as f:
            html = f.read().decode('utf-8')
    except:
        return 'error'
    return html


def get_down(url):
    html = get_html(url)
    if html == 'error':
        return html
    # time.sleep(1)
    soup = BeautifulSoup(html, 'html.parser')
    result = soup.find_all(href=re.compile(r'https://ehtracker.org/get/'))[0]['href']
    if result:
        return result
    else:
        return 'error'


def get_all(html):

    soup = BeautifulSoup(html, 'html.parser')
    for tr in soup.find_all('tr',class_=['gtr0','gtr1']):
        time = tr.find_all('td',{'style':"white-space:nowrap"})[0].string
        content = tr.find_all(class_='it2')[0].string
        if not content:
            img_url = tr.find_all('img')[1]['src']
            title = tr.find_all('img')[1]['alt']
        else:
            mix = re.split(r'~', content)
            img_url = 'https://ehgt.org/'+ mix[2]
            title = mix[3]
        sql_title = db.escape(title)
        sql = " select * from info where title= %s" % (sql_title,)
        cursor.execute(sql)
        if cursor.rowcount >= 1:
            print('已存在')
            continue
        if tr.find_all(href=re.compile(r'https://e-hentai.org/gallerytorrents.php')):
            down = get_down(tr.find_all(href=re.compile(r'https://e-hentai.org/gallerytorrents.php'))[0]['href'])
            if down == 'error':
                continue
            magnet = bt_link_to_magnet(down)
        else:
            magnet = ''
        global success_count
        if save_data(time, db.escape(img_url), sql_title, db.escape(magnet)):
            success_count += 1
            print('第%d条数据插入成功 数据名:%s' % (success_count, title))
        else:
            print('数据名:%s' % (title,))
    os.system('clear')


def bt_link_to_magnet(url):
    try:
        req = request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')
        with request.urlopen(req) as f:
            file = f.read()
        e = bt.bdecode(file)
        info = bt.torrent_info(e)
    except:
        return ''
    return "magnet:?xt=urn:btih:%s" % (info.info_hash())


def save_data(time, img_url, title, magnet):
    sql = " insert into info(time , title, img, magnet) values ('%s',%s,%s,%s)" % (time, title, img_url, magnet)
    try:
        cursor.execute(sql)
        db.commit()
        return 1
    except Exception as e:
        print("失败", e)
        db.rollback()
        return 0


def init(key):
    # pool = multiprocessing.Pool(multiprocessing.cpu_count())
    url = get_url(0, key)
    html = get_html(url)
    pages = getPages(html)[-1]                                         
    for i in range(0, int(pages)):
        print('这里是第%d页' % (i+1,))
        url = get_url(i, key)
        html = get_html(url)
        # pool.apply_async(get_all, (html,))
        get_all(html)
    # pool.close()
    # pool.join()
    cursor.close()
    db.close()


if __name__ == "__main__":
    db = pymysql.connect("localhost", "root", "passwd", "edata", charset="utf8")
    cursor = db.cursor()
    # key = input('输入搜索关键字(english):')
    key = 'chinese'
    init(key)

