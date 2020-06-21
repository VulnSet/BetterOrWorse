import re
import pymysql
import requests

hostname = 'localhost'
username = 'root'
pwd = 'admin'
dbname = 'firefox'
pattern = re.compile(r'<tr><td>milestone</td><td>(.*)</td></tr>')
versionPattern = re.compile(r'([\d.]+)')

def compareversion(a, b):
	if a == b:
		return 0
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

def save(bug, changeset, earliestVersion, earliestChangeset, conn):
	bugid = int(bug)
	changeset = ' '.join(changeset)
	#earliestVersion = earliest[bug]['earliestVersion']
	earliestChangeset = ' '.join(earliestChangeset)
	sql = "insert into vul2changeset_0527(bugid, changeset, earliestChangeset, earliestVersion) values( %d, '%s', '%s', '%s')"%(bugid, changeset, earliestChangeset, earliestVersion)
		#print sql
	try:
		cur = conn.cursor()
		cur.execute(sql)
		cur.close()
		conn.commit()
	except:
		print(sql)
		conn.rollback()
		

def readLog(filename, conn, bugList):
	file = open(filename, 'r')
	#out = open('imsucc.txt', 'w')
	m = dict()

	cnt = 0
	pre = ''
	backout_changeset = set()

	bugid_pattern = re.compile('bug[\s#]+\d+', re.I)
	backout_pattern = re.compile('back(ed)?\s?out', re.I)
	changeset_pattern = re.compile('[a-z0-9]{12}')

	#flag = False
	for line in file:
		cnt += 1
		#if cnt > 17000:
			#break
		a = line.split('|')
		node = a[0]

		bugid = ''
		desc = a[1]
		c = bugid_pattern.search(desc)
		d = backout_pattern.search(desc)
		if d:
			#Bug 825987 - Backed out changesets 1b9a99a17afb and 74493ca34d5e (bug 691061) due to regression with saving PDFs.
			#Backout 40f09f7bc670 & fc262e3c635f (bug 818670) for frequent fedora64 mochitest-3 leaks on a CLOSED TREE
			#backout 2620d0977696 because it landed w/ wrong bug number
			#Back out bug 824589 (rev 22695cac3896) on suspicion of Ts regression
			#Backout of changeset 816f076c2c15
			backout = True
			backout_index = d.start()
			if c:
				if c.start() > d.start():
					bugid = c.group()
				else:
					ids = bugid_pattern.finditer(desc)
					for i in ids:
						if i.start() > backout_index:
							bugid = i.group()

				if ' ' in bugid:
					bugid = bugid.replace('  ', ' ')
					bugid = bugid.split(' ')[1]
					if bugid[0] == '#':
						bugid = bugid[1:]
					backout_changeset.add(bugid)
				#else:
					#print bugid
			
			ch_list = changeset_pattern.findall(desc)
			for i in ch_list:
				backout_changeset.add(i)
			
		else:
			if c:
			#print node
				if ' ' not in c.group():
					continue
				bugid = c.group()
				bugid = bugid.replace('  ', ' ')
				bugid = bugid.split(' ')[1]
				if bugid[0] == '#':
					bugid = bugid[1:]

				if node != '' and bugid != '':
					if node in backout_changeset or bugid in backout_changeset:
						continue
					#save(node, bugid, conn)
					if bugid in bugList:
						bugList[bugid].append(node)
						#print(bugid, node)

	backout_changeset_file = open('backout_changeset.txt', 'w')
	for i in backout_changeset:
		backout_changeset_file.write(i + '\n')

	return bugList
		
def getBugList(conn):
	sql = 'select bugids from new_mfsa'
	try:
		cur = conn.cursor()
		cur.execute(sql)
		result = cur.fetchall()
		cur.close()
		conn.commit()
	except:
		print(sql)

	bugList = dict()
	for r in result:
		if r[0] == None or r[0] == '':
			continue
		bugids = r[0].split(' ')
		for bugid in bugids:
			if bugid == '':
				continue
			if bugid not in bugList:
				bugList[bugid] = []
	return bugList

def getAddBugList(conn):
	sql = "select bugid from vul2changeset_0527"
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
		bugid = str(r[0])
		had.append(bugid)

	file = open('Firefox_20200509add.txt', 'r')
	bugList = dict()
	for line in file:
		line = line.strip().split(' ')
		for bugid in line[1:]:
			if bugid == '':
				continue
			if bugid not in had and bugid not in bugList:
				#print(bugid)
				bugList[bugid] = []

	return bugList


def getMilestone(changeset):
	url = 'https://hg.mozilla.org/releases/mozilla-release/rev/' + changeset
	content = requests.get(url = url).content.decode("utf-8")
	milestone = pattern.search(content).group(1)
	version = versionPattern.search(milestone).group(1)
	print(changeset, milestone, version)
	return version

def confirmEarliestVersion(bugList, conn):
	earliest = dict()
	for bug in bugList:
		#if int(bug) < 1500000:
			#continue
		if len(bugList[bug]) == 0:
			continue
		print(bug, bugList[bug])
		changesetList = []
		earliestVersion = '100.0'
		for changeset in bugList[bug]:
			milestone = getMilestone(changeset)
			
			r = compareversion(earliestVersion, milestone)
			if r == 0:
				changesetList.append(changeset)
			elif r == 1:
				earliestVersion = milestone
				changesetList = []
				changesetList.append(changeset)

		save(bug, bugList[bug], earliestVersion, changesetList, conn)
	'''
		earliest[bug] = {
			'changesetList' : bugList[bug],
			'earliestVersion' : earliestVersion,
			'earliestChangeset' : changesetList
		}
	'''

def main():
	conn = pymysql.connect(host=hostname, user = username, passwd = pwd, db = dbname)
	file = 'F:/data/firefox/hglog20200527.txt'
	bugList = getAddBugList(conn) #getBugList(conn)
	bugList = readLog(file, conn, bugList)	
	earliest = confirmEarliestVersion(bugList, conn)
	conn.close()


if __name__ == '__main__':
	main()
	#getAddBugList()
#hg log --template '{node|short}|{tags}|{parents}|{desc|firstline}\n' > ../hglog.txt