#-*- coding: utf-8 -*-
import re
import requests
from bs4 import BeautifulSoup
import os
import pymysql

hostname = 'localhost'
username = 'root'
pwd = 'admin'
dbname = 'firefox'
conn = pymysql.connect(host = hostname, user = username, passwd = pwd, db = dbname)

headers = {
	        "User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13",
	        #"User-Agent" = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13",
	        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	        "Accept-Language":"zh-cn,zh;q=0.5",
	        #"Accept-Encoding":"gzip,deflate",
	        "Accept-Charset":"GB2312,utf-8;q=0.7,*;q=0.7",
	        "Keep-Alive":"115",
	        "Connection":"keep-alive"
	        }

		
def getBugzillTime(bugid):
	url = 'https://bugzilla.mozilla.org/show_bug.cgi?id=' + str(bugid)
	content = requests.get(url = url, headers = headers).content.decode('utf-8')
	bs = BeautifulSoup(content, 'lxml')
	spans = bs.find_all('span', attrs={'class':'bug-time-label'})

	for span in spans:
		if 'Opened' in span.text:
			real_time = span.span.get('title')[:10]
			return real_time
	return ''

def update(bugid, openTime):
	sql = "update final_regression set opendate='%s' where bugid=%d"%(openTime, bugid)
	try:
		cur = conn.cursor()
		cur.execute(sql)
		result = cur.fetchall()
		cur.close()
		conn.commit()
	except:
		print(sql)
		conn.rollback()


def main():
	sql = 'select bugid,opendate from final_regression'

	try:
		cur = conn.cursor()
		cur.execute(sql)
		result = cur.fetchall()
		cur.close()
		conn.commit()
	except:
		print(sql)
		conn.rollback()

	for r in result:
		if r[1] == None:
			bugid = r[0]
			openTime = getBugzillTime(bugid)
			if openTime == '':
				print(bugid, ' has error!')
			else:
				update(bugid, openTime)

if __name__ == '__main__':
	main()