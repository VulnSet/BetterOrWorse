import pymysql
hostname = 'localhost'
username = 'root'
PSWD = 'admin'
dbname = 'firefox'
conn = pymysql.connect(host=hostname, user = username, passwd = PSWD, db = dbname)


def main():
	cveList = dict()

	sql = "select cve, name from cveref where refsource='BID'"
	try:
		cur = conn.cursor()
		cur.execute(sql)
		result = cur.fetchall()
		cur.close()
		conn.commit()
	except:
		print(sql)

	for r in result:
		cve = r[0]
		bid = r[1]
		if cve not in cveList:
			cveList[cve] = [bid]
		else:
			if bid not in cveList[cve]:
				cveList[cve].append(bid)

	sql = "select cve, bid from bid"
	try:
		cur = conn.cursor()
		cur.execute(sql)
		result = cur.fetchall()
		cur.close()
		conn.commit()
	except:
		print(sql)

	for r in result:
		cves = r[0].split(' ')
		bid = r[1]
		for cve in cves:
			if cve not in cveList:
				cveList[cve] = [bid]
			else:
				if bid not in cveList[cve]:
					cveList[cve].append(bid)

	for cve in cveList:
		bids = ' '.join(cveList[cve])
		sql = f"insert into cve2bid values('{cve}', '{bids}')"
		try:
			cur = conn.cursor()
			cur.execute(sql)
			result = cur.fetchall()
			cur.close()
			conn.commit()
		except:
			print(sql)
			conn.rollback()

if __name__ == '__main__':
	main()