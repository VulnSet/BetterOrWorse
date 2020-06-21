import os
import urllib
import zipfile
import pymysql
from bs4 import BeautifulSoup
import requests
import re
import time

hostname = 'localhost'
username = 'root'
PSWD = 'admin'
dbname = 'firefox'
conn = pymysql.connect(host=hostname, user = username, passwd = PSWD, db = dbname)

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

header = {
	        "User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13",
	        #"User-Agent" = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13",
	        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	        "Accept-Language":"zh-cn,zh;q=0.5",
	        #"Accept-Encoding":"gzip,deflate",
	        "Accept-Charset":"GB2312,utf-8;q=0.7,*;q=0.7",
	        "Keep-Alive":"115",
	        "Connection":"keep-alive"
	        }

def writeToOther(info, file):
	tmp = ''
	for i in range(10):
		tmp += str(info[i]) + ','
	tmp = tmp[:-1] + '\n'
	file.write(tmp)

def writeToSql(info, conn):
	name = info[0]
	name = conn.escape(name)
	href = conn.escape(info[10])
	time = info[6].split(' ')
	year = time[2]
	month = time[0]
	day = time[1]

	for i in range(12):
		if month in months[i]:
			month = str(i + 1) 
	ans = str(year) + '-' + month + '-' + str(day)

	sql = "insert into securityfocus values('%s', %s, '%s', '%s', '%s', '%s', %s)"%(info[1], name, info[3], ans, info[8], info[9], href)
	try:
		cur = conn.cursor()
		cur.execute(sql)
		cur.close()
		conn.commit()
	except:
		print(sql)
		conn.rollback()

def compareversion(a, b):
	list_a = a.split('.')
	list_b = b.split('.')
	lenth = min(len(list_a), len(list_b))
	for i in range(lenth):
		#print(list_b[i], list_b[i])
		x = int(list_a[i])
		y = int(list_b[i])
		if x < y:
			return -1
		elif x > y:
			return 1
		else:
			continue
	if len(list_a) < len(list_b):
		return -1
	elif len(list_a) > len(list_b):
		return 1
	return 0

def save(bid, cve, reporttime, min_version, max_version, mid):
	
	sql = "insert into bid values('%s', '%s', '%s', '%s', '%s', %d)"%(bid, cve, reporttime, min_version, max_version, mid)
	try:
		cur = conn.cursor()
		cur.execute(sql)
		cur.close()
		conn.commit()
	except:
		print(sql)
		conn.rollback()

def getMessage(bid):
	flag = 0
	info = []
	url = 'http://www.securityfocus.com' + bid
	#print(url)
	content = requests.get(url = url, headers = header).content.decode("iso-8859-1")
	if 'You have entered a malformed request.' in content:
		return -1

	soup = BeautifulSoup(content, 'html.parser')
	#print(soup)
	divs = soup.find_all('div', attrs={'id':'vulnerability'})
	#print(len(divs))
	
	table = divs[0].find_all('table')
	trs = table[0].find_all('tr')
	#for i in range(7):
		#tds = trs[i].find_all('td')
		#info.append(tds[1].text.replace('\t', '').replace('\n', ' ').replace('  ', ' ').strip())
	
	cve = trs[2].find_all('td')[1].text.replace('\t', '').replace('\n', ' ').replace('  ', ' ').strip()

	ids = cve.split(' ')
	s = set(ids)
	cve = ''
	for i in s:
		cve += ' ' + i
	cve = cve.strip()


	reporttime = trs[5].find_all('td')[1].text.replace('\t', '').replace('\n', ' ').replace('  ', ' ').strip()[0:11]
	time = reporttime.split(' ')
	year = time[2]
	month = time[0]
	day = time[1]

	for i in range(12):
		if month in months[i]:
			month = str(i + 1) 
	reporttime = str(year) + '-' + month + '-' + str(day)

	#print(trs[8])
	tds = trs[8].find_all('td')
	text = tds[1].text.replace('\t', '').strip()
	text = text.replace('\n\n\n', '\n')
	text = text.replace('\n\n', '\n')
	softwares = text.split('\n')

	min_version = '100'
	max_version = '1'
	for software in softwares:
		software = software.strip()
		#print(software)
		if software == '+' or software == '-':
			continue
		software = software.strip()
		software = software.replace('  ', ' ')
		
		match =  re.search(r'Mozilla Firefox [0-9\.]+', software)
		
		if match:
			version = match.group()[16:]
			#print(version)
			if int(version.split('.')[0]) < 4:
				continue 
			#print(version)
			min_version = version if compareversion(min_version, version) == 1 else min_version
			max_version = version if compareversion(version, max_version) == 1 else max_version

	if compareversion('4.0', max_version) == 1:
		return 0
	if compareversion('4.0', min_version) == 1:
		min_version = '4.0'

	mid = 0
	if len(trs) > 9:
		tds = trs[10].find_all('td')
		text = tds[1].text.replace('\t', '').strip()
		text = text.replace('\n\n\n', '\n')
		text = text.replace('\n\n', '\n')
		softwares = text.split('\n')

		for software in softwares:
			software = software.strip()
			#print(software)
			if software == '+' or software == '-':
				continue
			software = software.strip()
			software = software.replace('  ', ' ')
			match =  re.search(r'Mozilla Firefox [0-9\.]+', software)
			
			if match:
				version = match.group()[16:]

				if compareversion(version, min_version) == 1 and compareversion(max_version, version) == 1 and compareversion(version, '4.0') == 1:
					mid = 1
	print(bid[5:], cve, reporttime, min_version, max_version, mid)		
	#save(bid[5:], cve, reporttime, min_version, max_version, mid)



def mymain(i):
	#file = open(str(i) + '.txt', 'w')
	#conn = pymysql.connect(host=hostname, user = username, passwd = PSWD, db = dbname)

	num = 0

	url = "http://www.securityfocus.com/cgi-bin/index.cgi?o=" + str(i*30);
	url = url + "&l=30&c=12&op=display_list&vendor=Mozilla&version=&title=Firefox&CVE="
	print(url)
	content = requests.get(url=url,headers = header).content.decode("iso-8859-1")
	soup = BeautifulSoup(content,'html.parser')
	hrefs = soup.find_all(name='a', attrs={"href":re.compile(r'^/bid/[0-9]+$')})
	cnt = 0
	for href in hrefs:
		cnt += 1
		if cnt&1:
			continue
		num += 1
		bid = href.get('href')
		print(bid)
		getMessage(bid)
		#getMessage(bid, file, conn)
	
	print(num)
	#file.close()
	#conn.close()


def main():
	file = open('bid_20200515.txt', 'w')

	num = 0
	for i in range(4):
		url = "http://www.securityfocus.com/cgi-bin/index.cgi?o=" + str(i*30);
		url = url + "&l=30&c=12&op=display_list&vendor=Mozilla&version=&title=Firefox&CVE="
		print(url)
		content = requests.get(url=url,headers = header).content.decode("iso-8859-1")
		soup = BeautifulSoup(content,'html.parser')
		hrefs = soup.find_all(name='a', attrs={"href":re.compile(r'^/bid/[0-9]+$')})
		cnt = 0
		for href in hrefs:
			cnt += 1
			if cnt&1:
				continue
			num += 1
			bid = href.get('href').split('/')[-1]
			
			file.write(bid + '\n')			

	print(num)

def updateBIDExploitTime(bid, date, url):
	sql = f"select id, isExploit from cveref where name='{bid}' and refsource='BID'"
	try:
		cur = conn.cursor()
		cur.execute(sql)
		result = cur.fetchone()
		cur.close()
		conn.commit()
	except:
		print(sql)

	if result == None:
		sql = f"insert into cveref(ref, name, refsource, publication, isExploit) \
			values('{url}', '{bid}', 'BID-ADD', '{date}', 1)"
		#print(sql)
	else:
		isExploit = result[1]
		sql = f"update cveref set publication='{date}', isExploit=1 where id={result[0]}"
		#print(sql)
	try:
		cur = conn.cursor()
		cur.execute(sql)
		cur.close()
		conn.commit()
	except:
		print(sql)
		conn.rollback()


def BidParser(bid):
	print(bid)
	date = ''
	sql = f"select reporttime from bid where bid = '{bid}'"
	try:
		cur = conn.cursor()
		cur.execute(sql)
		result = cur.fetchone()
		cur.close()
		conn.commit()
	except:
		print(sql)
	if result == None:
		url = f'https://www.securityfocus.com/bid/{bid}'
		content = requests.get(url = url, headers = header).content.decode("iso-8859-1")
		if 'You have entered a malformed request.' in content:
			return -1

		soup = BeautifulSoup(content, 'html.parser')
		divs = soup.find_all('div', attrs={'id':'vulnerability'})
		table = divs[0].find_all('table')
		trs = table[0].find_all('tr')
		
		cve = trs[2].find_all('td')[1].text.replace('\t', '').replace('\n', ' ').replace('  ', ' ').strip()

		ids = cve.split(' ')
		s = set(ids)
		cve = ''
		for i in s:
			cve += ' ' + i
		cve = cve.strip()

		reporttime = trs[5].find_all('td')[1].text.replace('\t', '').replace('\n', ' ').replace('  ', ' ').strip()[0:11]
		time = reporttime.split(' ')
		year = time[2]
		month = time[0]
		day = time[1]

		for i in range(12):
			if month in months[i]:
				month = str(i + 1) 
		reporttime = str(year) + '-' + month + '-' + str(day)
		print(bid, cve, reporttime)
		sql = "insert into bid(bid, cve, reporttime) values('%s', '%s', '%s')"%(bid, cve, reporttime)
		try:
			cur = conn.cursor()
			cur.execute(sql)
			cur.close()
			conn.commit()
		except:
			print(sql)
			conn.rollback()
		date = reporttime
	else:
		date = result[0]

	url = f'https://www.securityfocus.com/bid/{bid}/exploit'
	content = requests.get(url = url, headers = header).content.decode("iso-8859-1")
	#try:
	soup = BeautifulSoup(content, 'lxml')
	div = soup.find('div', attrs={'id':'vulnerability'})
	if 'vuldb@securityfocus.com' in div.text:
		return
	href = div.find_all('a')
	if len(href) < 1:
		return
	updateBIDExploitTime(bid, date, url)

def readBID():
	file = open('bid_20200516.txt', 'r')
	for line in file:
		line = line.strip()
		BidParser(line)

if __name__ == '__main__':
	readBID()
	#main()
	#mymain(0)
	#getMessage('/bid/64204')
		
	'''
	file = open('other.txt', 'w')
	conn = pymysql.connect(host=hostname, user = username, passwd = PSWD, db = dbname)
	getMessage("http://www.securityfocus.com/bid/27352", file, conn)
	file.close()
	conn.close()
	'''