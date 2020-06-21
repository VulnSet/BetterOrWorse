import os
import requests
import urllib
import zipfile
import pymysql
from bs4 import BeautifulSoup
import re

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

def download_files():
    if not os.path.exists(r'./NVD_zip'):
        os.mkdir('NVD_zip')
    if not os.path.exists(r'./NVD_Data'):
        os.mkdir('NVD_Data')
    download_url = 'https://nvd.nist.gov/vuln/data-feeds'
    getstr = requests.get(url=download_url,headers = header).content.decode("utf-8") 
    soup = BeautifulSoup(getstr,'html.parser')
    #print('ok')
    #print(soup)
    for tr in soup.find_all('tr', 'xml-feed-data-row'):
        #print(tr)
        for child in tr.find_all('a'):
            if child.string == 'ZIP':
                href = child.get('href')
                filename = href.split(r'/')[-1]
                print(href)
                if 'json/cve' in href:
                	urllib.request.urlretrieve(href, r'./NVD_zip/'+filename)
    #return
    for filename in os.listdir(r'./NVD_zip'):
        if re.match('nvdcve-1.1-\d\d\d\d.json.zip', filename):# or 'modified' in filename or 'Modified' in filename:
            zip_ = zipfile.ZipFile((r'NVD_zip/'+filename),'r')
            zip_.extractall(r'./NVD_Data')
            zip_.close()

if __name__ == '__main__':
	download_files()

'''
import pymysql


hostname = 'localhost'
username = 'root'
PSWD = 'admin'
dbname = 'nvd'

def main(id):
	conn = pymysql.connect(host = hostname, user = username, passwd = PSWD, db = dbname)

	sql = 'select id,patch,src from openbsdinfo where id = ' + id

	cur = conn.cursor()
	cur.execute(sql)
	result = cur.fetchall()

	for r in result:
'''