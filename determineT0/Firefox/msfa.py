import os
import urllib
import pymysql
import re

from bs4 import BeautifulSoup
import requests

hostname = 'localhost'
username = 'root'
PSWD = 'admin'
dbname = 'firefox'

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
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

def timetransformer(text):
	text = text.replace('  ', ' ')
	time = text.split(' ')
	year = time[2]
	month = time[0]
	day = time[1][:-1]

	for i in range(12):
		if month in months[i]:
			month = str(i + 1) 
	ans = str(year) + '-' + month + '-' + str(day)
	return ans
	

def save(conn, cve, announced, reporter, impact, fixedin, references):
	#print(cve, announced, reporter, impact, fixedin, references)
	
	conn = pymysql.connect(host=hostname, user=username, passwd=PSWD, db=dbname)
	cur = conn.cursor()

	sql = "select bugids from new_mfsa where cve = '%s'"%(cve)
	try:
		cur.execute(sql)
		conn.commit()
		result = cur.fetchone()

		if result != None:
			bugids = result[0].split(' ')
			tmp = result[0]
			
			mymap = set(bugids)

			newids = references.split(' ')
			
			for i in newids:
				if i not in mymap:
					tmp += ' ' + i
					mymap.add(i)

			if tmp != result[0]:
				sql = "update new_mfsa set bugids = '%s' where cve = '%s'"%(tmp, cve)
				try:
					cur.execute(sql)
					cur.close()
					conn.commit()
				except:
					print(sql)
					conn.rollback()
		else:
			sql = "insert into new_mfsa(cve, reporttime, fixedin, bugids) values('%s', '%s', '%s', '%s')"%(cve, announced, fixedin, references)
			try:
				cur.execute(sql)
				cur.close()
				conn.commit()
			except:
				print(sql)
				conn.rollback()

	except:
		print(sql)
		conn.rollback()


def oneref(li, conn, announced, reporter, impact, fixedin):
	a = li.find('a')
	
	if 'https://bugzilla.mozilla.org/show_bug.cgi?id=' in a.get('href'):
		references = trans_ref(a.get('href')[45:])
		
	if 'https://bugzilla.mozilla.org/buglist.cgi?bug_id=' in a.get('href'):
		references = trans_ref(a.get('href')[48:])

	cve = re.search(r'\(CVE-[0-9]+-[0-9]+\)', li.text)
	#print(li)
	print(cve.group()[1:-1], references)
	save(conn, cve.group()[1:-1], announced, reporter, impact, fixedin, references)
	
def func1(url, conn):
	#print(url)
	content = requests.get(url=url, headers=headers).content.decode('utf-8')
	soup = BeautifulSoup(content, 'lxml')
	summary = soup.find('dl',attrs={'class':'summary'})
	dds = summary.find_all('dd')
	announced = dds[0].text
	announced = timetransformer(announced)
	tmp = dds[3]
	lis = tmp.find_all('li')
	fixedin = ''
	for li in lis:
		text = li.text
		if re.match('Firefox [0-9.]', text):
			fixedin += ' ' + text
	fixedin = fixedin.lstrip(' ')
		
	sections = soup.find_all('section', attrs={'class':'cve'})
	for section in sections:
		cve = section.find('h4').get('id')
		#print(cve)
		dds = section.find_all('dd')
		reporter = dds[0].text
		impact = dds[1].text
		description = section.find('p').text.replace('<strong>', '')
		
		refs = section.find_all('li')
		if len(refs) > 1:
			#print(url + cve + "has two ref")
			references = ''
			for ref in refs:
				if re.search(r'\(CVE-[0-9]+-[0-9]+\)', ref.text):
					oneref(ref, conn, announced, reporter, impact, fixedin)
					continue
				href = ref.find('a').get('href')
				if 'https://bugzilla.mozilla.org/show_bug.cgi?id=' in href:
					references += ' ' + href[45:]
				if 'https://bugzilla.mozilla.org/buglist.cgi?bug_id=' in href:
					references += ' ' + href[48:]
				
			references = references.lstrip(' ')
		else:
			href = refs[0].find('a').get('href')
			if 'https://bugzilla.mozilla.org/show_bug.cgi?id=' in href:
				references = href[45:]
			if 'https://bugzilla.mozilla.org/buglist.cgi?bug_id=' in href:
				references = href[48:]

		references = references.replace('%2C', ' ')
		references = references.replace('\n', ' ')
		if references == '':
			print('================' + url + ' ' + cve + ' ' + 'has no reference')
		else: 
			print(cve, references)
			save(conn, cve, announced, reporter, impact, fixedin, references)
		

def trans_ref(references):
	references = references.lstrip(' ')
	references = references.replace('%2C', ' ')
	references = references.replace(',', ' ')
	references = references.replace('\n', ' ')
	return references

def func2(url, conn):
	content = requests.get(url=url, headers=headers).content.decode('utf-8')
	soup = BeautifulSoup(content, 'lxml')
	dds = soup.find_all('dd')
	announced = dds[0].text
	announced = timetransformer(announced)
	reporter = dds[1].text
	impact = dds[2].text

	#print(len(dds))
	if len(dds) > 4:
		tmp = dds[4]
	else:
		tmp = dds[3]
	lis = tmp.find_all('li')
	fixedin = ''
	for li in lis:
		text = li.text
		if re.match('Firefox [0-9.]', text):
			#print(text)
			fixedin += ' ' + text
	fixedin = fixedin.lstrip(' ')

	tmp = soup.find('div', attrs={'class':'main-column'})
	description = tmp.find('p').text.replace('<strong>', '')

	references = ''
	cve = ''
	uls = tmp.find_all('ul')
	for i in range(1, len(uls)):
		lis = uls[i].find_all('li')
		for li in lis:
			links = li.find_all('a')
			#print(len(links))
			if len(links) < 2:
				print('-------------' + url + ' ' + 'has no cve')
			else:
				if 'https://bugzilla.mozilla.org/show_bug.cgi?id=' in links[0].get('href'):
					references = trans_ref(links[0].get('href')[45:])
					if 'http://cve.mitre.org/cgi-bin/cvename.cgi?name=' in links[1].get('href'):
						cve = links[1].get('href')[46:]
						save(conn, cve, announced, reporter, impact, fixedin, references)
						#print(cve, references, url)
					else:
						print('==============' + url + ' ' + 'has no cve')
				if 'https://bugzilla.mozilla.org/buglist.cgi?bug_id=' in links[0].get('href'):
					references = trans_ref(links[0].get('href')[48:])
					if 'http://cve.mitre.org/cgi-bin/cvename.cgi?name=' in links[1].get('href'):
						cve = links[1].get('href')[46:]
						save(conn, cve, announced, reporter, impact, fixedin, references)
						#print(cve, references, url)
					else:
						print('==============' + url + ' ' + 'has no cve')


		'''
		for a in links:
			href = a.get('href')
			#print(href)
			if 'https://bugzilla.mozilla.org/show_bug.cgi?id=' in href:
				references += ' ' + href[45:]
			if 'https://bugzilla.mozilla.org/buglist.cgi?bug_id=' in href:
				references += ' ' + href[48:]
			if 'http://cve.mitre.org/cgi-bin/cvename.cgi?name=' in href:
				cve += ' ' + href[46:]
		'''

	#cve = cve.lstrip(' ')
	#references = references.lstrip(' ')
	

	#if references == '':
		#print('================' + url + ' ' + 'has no reference')
	#if cve == '':
		#print('================' + url + ' ' + 'has no cve')
	#print(cve, announced, reporter, impact, fixedin, references)
	#print(cve, references, url)
	#save(conn, cve, announced, reporter, impact, fixedin, references)

def func3(url, conn):
	content = requests.get(url=url, headers=headers).content.decode('utf-8')
	soup = BeautifulSoup(content, 'lxml')
	dds = soup.find_all('dd')
	announced = dds[0].text
	announced = timetransformer(announced)
	reporter = dds[1].text
	impact = dds[2].text

	#print(len(dds))
	if len(dds) > 4:
		tmp = dds[4]
	else:
		tmp = dds[3]
	lis = tmp.find_all('li')
	fixedin = ''
	for li in lis:
		text = li.text
		if re.match('Firefox [0-9.]', text):
			#print(text)
			fixedin += ' ' + text
	fixedin = fixedin.lstrip(' ')

	tmp = soup.find('div', attrs={'class':'main-column'})
	description = tmp.find('p').text.replace('<strong>', '')

	
	uls = tmp.find_all('ul')
	for i in range(1, len(uls)):
		references = ''
		cve = ''
		links = uls[i].find_all('a')
		for a in links:
			href = a.get('href')
			#print(href)
			if 'https://bugzilla.mozilla.org/show_bug.cgi?id=' in href:
				references += ' ' + href[45:]
			if 'https://bugzilla.mozilla.org/buglist.cgi?bug_id=' in href:
				references += ' ' + href[48:]
			if 'http://cve.mitre.org/cgi-bin/cvename.cgi?name=' in href:
				cve += ' ' + href[46:]

		cve = cve.lstrip(' ')
		references = trans_ref(references)
	

		if references == '':
			print('================' + url + ' ' + 'has no reference')
		if cve == '':
			print('================' + url + ' ' + 'has no cve')
		#print(cve, announced, reporter, impact, fixedin, references)
		print(cve, references, url)
		#save(conn, cve, announced, reporter, impact, fixedin, references)

def main():
	conn = pymysql.connect(host=hostname, user=username, passwd=PSWD, db=dbname)
	flag = 0
	url = 'https://www.mozilla.org/en-US/security/known-vulnerabilities/firefox/'
	content = requests.get(url=url, headers=headers).content.decode('utf-8')
	soup = BeautifulSoup(content, 'lxml')
	lis = soup.find_all('li', attrs={'class':'level-item'})
	for li in lis:
		a = li.find_all('a')
		if not a:
			continue

		#print(a)
		href = a[0].get('href')
		#print(href)
		url = 'https://www.mozilla.org' + href
		if url == 'https://www.mozilla.org/en-US/security/advisories/mfsa2017-15/':
			break
		#print(url)
		if flag == 0:
			func1(url, conn)
		elif flag == 1:
			func2(url, conn)
		else:
			func3(url, conn)

		if url == 'https://www.mozilla.org/en-US/security/advisories/mfsa2016-85/':
			flag = 1
			
		if url == 'https://www.mozilla.org/en-US/security/advisories/mfsa2012-105/':
			flag = 2
			break
		


if __name__ == '__main__':
	main()
	#conn = pymysql.connect(host=hostname, user=username, passwd=PSWD, db=dbname)
	#func1('https://www.mozilla.org/en-US/security/advisories/mfsa2017-10/',conn)
	#func2('https://www.mozilla.org/en-US/security/advisories/mfsa2016-35/', conn)
	#func3('https://www.mozilla.org/en-US/security/advisories/mfsa2012-90/', conn)
	
#20200509 https://www.mozilla.org/en-US/security/advisories/mfsa2018-01/ msfa2018-05 have problem