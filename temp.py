#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Orange'

import pymysql

db = pymysql.connect("localhost", "root", "3396959", "edata", charset="utf8")
cursor = db.cursor()
sql = "select * from info order by time"
time = ''
title = ''
magnet = ''
sql2 = " insert into temp(time , title, img, magnet) values ('%s',%s,%s,%s)"
cursor.execute(sql)
results = cursor.fetchall()
count = 0
for row in results:
    title = row[2]
    time = row[1]
    img_url = row[3]
    magnet = row[4]
    sql3 = sql2 % (time, db.escape(title), db.escape(img_url), db.escape(magnet))
    count +=1
    print(count)
    try:
        cursor.execute(sql3)
        db.commit()
    except Exception as e:
        print('error',e)
print('done')