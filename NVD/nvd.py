import json
import os
import pymysql
import re
import xlwt
hostname = 'localhost'
username = 'root'
pwd = 'admin'
dbname = 'firefox'

conn = pymysql.connect(host = hostname, user = username, passwd = pwd, db = dbname)

def get_all_datafile():
	json_list = []
	for dirname,folder,files in os.walk("./NVD_Data"):
		for filename in files:
			if filename.endswith(".json"):
				json_list.append(os.path.join(dirname, filename))
	return json_list

def savePublication(cve, published):
	sql = "insert into nvdfirefox(cve, reporttime) value('%s', '%s')"%(cve, published)
	try:
		cur = conn.cursor()
		cur.execute(sql)
		cur.close()
		conn.commit()
		print(cve, published, ' success')
	except:
		print(sql)
		conn.rollback()


def load(json_file, cveList):
	print(json_file)
	with open(json_file, 'r', encoding='utf-8') as json_data:  
		data = json.load(json_data)
	#for key in data.keys():
	#	print(key)
	for items in data["CVE_Items"]:
		cve_info = items["cve"]
		#print(cve_info["CVE_data_meta"]["ID"])
		cve_id = cve_info["CVE_data_meta"]["ID"]
		if cve_id in cveList:
			published = items["publishedDate"][:10]
			#print(cve_id, published)
			savePublication(cve_id, published)
			#return 

def save(cve, url, name, refsource, tags):
	url = pymysql.escape_string(url)
	name = pymysql.escape_string(name)
	sql = "insert into cveref(cve, ref, name, refsource, tags) values('%s', '%s', '%s', '%s', '%s')"%(cve, url, name, refsource, tags)
	try:
		cur = conn.cursor()
		cur.execute(sql)
		cur.close()
		conn.commit()
	except:
		print(sql)
		conn.rollback()


def getRef_Year(json_file, cveList):
	with open(json_file, 'r', encoding='utf-8') as json_data:  
		data = json.load(json_data)

	for items in data["CVE_Items"]:
		cve_info = items["cve"]
		#print(cve_info["CVE_data_meta"]["ID"])
		cve_id = cve_info["CVE_data_meta"]["ID"]
		if cve_id in cveList:
			refs = cve_info["references"]["reference_data"]
			for ref in refs:
				url = ref["url"]
				name = ref["name"]
				refsource = ref["refsource"]
				tags = ','.join(ref["tags"])
				#print(cve_id, url, name, refsource, tags)
				save(cve_id, url, name, refsource, tags)
			#return

def getRefs():
	cveList = []
	with open('FirefoxCveList2.txt', 'r') as file:
		for line in file:
			cveList.append(line.strip())

	json_files = get_all_datafile()
	for json_file in json_files:
		getRef_Year(json_file, cveList)
		#return 

def cveAddReporttime():
	sql = "select cve from nvdfirefox"
	try:
		cur = conn.cursor()
		cur.execute(sql)
		result = cur.fetchall()
		cur.close()
		conn.commit()
	except:
		print(sql)

	had = []
	for r in result:
		had.append(r[0])

	cveList = []
	with open('FirefoxCveList2.txt', 'r') as file:
		for line in file:
			if line.strip() not in had:
				cveList.append(line.strip())

	json_files = get_all_datafile()
	for json_file in json_files:
		load(json_file, cveList)

def readCVSS():
	cveList = []
	with open('firefoxCVELack.txt', 'r') as file:
		for line in file:
			if line.strip() not in cveList:
				cveList.append(line.strip())

	#wb = xlwt.Workbook()
	#wb_sheet = wb.add_sheet('cvss', cell_overwrite_ok=True)
	#cnt = 0

	json_files = get_all_datafile()
	for json_file in json_files:
		tmp = int(json_file.split('.')[-2].split('-')[-1])
		if tmp < 2017:
			continue
		with open(json_file, 'r', encoding='utf-8') as json_data:  
			data = json.load(json_data)
		#for key in data.keys():
		#	print(key)
		for items in data["CVE_Items"]:
			cve_info = items["cve"]
			#print(cve_info["CVE_data_meta"]["ID"])
			cve_id = cve_info["CVE_data_meta"]["ID"]
			if cve_id in cveList:
				#print(cve_id)
				cveList.remove(cve_id)
	print(cveList)

	'''
				published = items["publishedDate"][:10]
				cwe = cve_info["problemtype"]["problemtype_data"][0]["description"][0]["value"]

				impact = items["impact"]["baseMetricV2"]
				v,s,AV,AC,Au,C,I,A,baseScore = impact["cvssV2"].values()
				exploitScore = impact["exploitabilityScore"]
				impactScore = impact["impactScore"]
				
				if AV == 'LOCAL':
					AV = 0.395
				elif AV == 'ADJACENT_NETWORK':
					AV = 0.646
				else:
					AV = 1.0

				if AC == 'HIGH':
					AC = 0.35
				elif AC == 'MEDIUM':
					AC = 0.61
				else:
					AC = 0.71

				if Au == 'SINGLE':
					Au = 0.56
				elif Au == 'NONE':
					Au = 0.704
				else:
					Au = 0.45

				if C == 'NONE':
					C = 0
				elif C == 'PARTIAL':
					C = 0.275
				else:
					C = 0.660

				if I == 'NONE':
					I = 0
				elif I == 'PARTIAL':
					I = 0.275
				else:
					I = 0.660

				if A == 'NONE':
					A = 0
				elif A == 'PARTIAL':
					A = 0.275
				else:
					A = 0.660

				d = [cve_id, baseScore, AV, AC, Au, C, I, A, cwe, impactScore, exploitScore]

				for i in range(11):
					wb_sheet.write(cnt, i, d[i])
				cnt += 1
	wb.save('cveInfo_20200605Add.xls')
'''

if __name__ == "__main__":
	#getRefs() 
	#cveAddReporttime()
	readCVSS()