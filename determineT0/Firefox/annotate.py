#-*- coding:utf-8 -*-
import pymysql
import os
import re
import requests

hostname = 'localhost'
username = 'root'
pwd = 'admin'
dbname = 'firefox'
conn = pymysql.connect(host = hostname, user = username, passwd = pwd, db = dbname)
pattern = re.compile(r'<tr><td>milestone</td><td>(.*)</td></tr>')
versionPattern = re.compile(r'([\d.]+)')

VERSION = ['4.0', '4.0.1', '5.0', '5.0.1', '6.0', '6.0.1', '6.0.2', '7.0', '7.0.1', '8.0', '8.0.1', '9.0', '9.0.1',\
 '10.0', '10.0.1', '10.0.2', '11.0', '12.0', '13.0', '13.0.1', '14.0.1', '15.0', '15.0.1', '16.0', '16.0.1',\
 '16.0.2', '17.0', '17.0.1', '18.0', '18.0.1', '18.0.2', '19.0', '19.0.1', '19.0.2', '20.0', '20.0.1', '21.0',\
 '22.0', '23.0', '23.0.1', '24.0', '25.0', '25.0.1', '26.0', '27.0', '27.0.1', '28.0', '29.0', '29.0.1', '30.0',\
 '31.0', '32.0', '32.0.1', '32.0.2', '32.0.3', '33.0', '33.0.1', '33.0.2', '33.0.3', '33.1', '33.1.1', '34.0',\
 '34.0.5', '35.0', '35.0.1', '36.0', '36.0.1', '36.0.3', '36.0.4', '37.0', '37.0.1', '37.0.2', '38.0', '38.0.1',\
 '38.0.5', '39.0', '39.0.3', '40.0', '40.0.2', '40.0.3', '41.0', '41.0.1', '41.0.2', '42.0', '43.0', '43.0.1',\
 '43.0.2', '43.0.3', '43.0.4', '44.0', '44.0.1', '44.0.2', '45.0', '45.0.1', '45.0.2', '46.0', '46.0.1', '47.0',\
 '47.0.1', '47.0.2', '48.0', '48.0.1', '48.0.2', '49.0', '49.0.1', '49.0.2', '50.0', '50.0.1', '50.0.2', '51.0',\
 '51.0.1', '52.0', '52.0.1', '52.0.2', '53.0', '53.0.2', '53.0.3', '54.0', '54.0.1', '55.0', '55.0.1', '55.0.2', '55.0.3']


FILETYPE = ['c', 'C', 'cc', 'cpp', 'css', 'cxx', 'h', 'H', 'hh', 'hpp', 'hxx', 'inl']

def compareversion(a, b):
	if a == 'tip' and b == 'tip':
		return 0
	if a == 'tip':
		return 1
	if b == 'tip':
		return -1

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

def checkfiletype(changefilename):
	filename = changefilename.split('/')[-1]
	if '.' not in filename:
		return False
	filetype = filename.split('.')[-1]
	if filetype in FILETYPE:
		return True
	#print filetype
	return False

def solvechangefile(changefilename, lines, changeset, record, bugid):
	#print "solvechangefile"
	if not checkfiletype(changefilename):
		return -1, -1, '', ''
	
	current = 0
	cnt = 0
	diff_line = []

	line_pattern = re.compile('@@\s-(\d+),')

	for i in range(len(lines)):
		line = lines[i]
		#print(line)
		if line[0:2] == '@@':
			note = False
			current = int(line_pattern.findall(line)[0])
		else:
			if line[0] != '+':
				current += 1
			if line[0] == '-':
				#qudiao zhushi
				line_strip = line[1:].strip()
				if line_strip[0:2] == '//':
					continue
				elif line_strip[0:2] == '/*':
					if line_strip[-2:] == '*/':
						continue
					note = True
				elif line_strip[-2:] == '*/':
					note = False
				elif note == False:
					if line_strip != '{' and line_strip != '}' and line_strip != '':
						diff_line.append(current - 1)
			

	if len(diff_line) < 1:
		#print "no ----"
		return 10000000, 0, '', ''

	#print(diff_line)
	annotate_cmd = 'hg annotate -n -c -r ' + changeset + ' ' + changefilename  # + '> ../tmp/tmp.txt'f
	#print(annotate_cmd)

	#os.system(annotate_cmd + '> ../annotate/' + changefilename.split('/')[-1])
	result = os.popen(annotate_cmd).readlines()
		
	max_revision = 0
	max_revision_changeset = ''
	min_revision = 10000000
	min_revision_changeset = ''

	for i in diff_line:
		#print(result[i-1])
		r = result[i-1].strip().split(':')[0].split(' ')
		#print(r)
		tmp = int(r[0])
		if tmp > max_revision:
			max_revision = tmp
			max_revision_changeset = r[1]
		if tmp < min_revision:
			min_revision = tmp
			min_revision_changeset = r[1]

	str = '%s %d %s %d %s %d %s\n'%(changefilename, len(diff_line), ','.join('%s' % id for id in diff_line), min_revision, min_revision_changeset, max_revision, max_revision_changeset)
	record.write(str)
	#print revision
	return min_revision, max_revision, max_revision_changeset, min_revision_changeset

def update(bugid, min_bug_induce, max_bug_induce):
	#sql = "update vul2changeset_0527 set min_revision=%d, max_revision=%d, min_version='%s', max_version='%s' where bugid=%d"%(min_bug_induce, max_bug_induce, min_version, max_version, bugid)
	sql = "update vul2changeset_0527 set min_revision=%d, max_revision=%d where bugid=%d"%(min_bug_induce, max_bug_induce, bugid)
	#print sql
	try:
		cur = conn.cursor()
		cur.execute(sql)
		cur.close()
		conn.commit()
	except:
		print(sql)
		conn.rollback()

def getMilestone(bugid, changeset):
	url = 'https://hg.mozilla.org/releases/mozilla-release/rev/' + changeset
	try:
		content = requests.get(url = url).content.decode("utf-8")
		milestone = pattern.search(content).group(1)
		version = versionPattern.search(milestone).group(1)
		#print(changeset, milestone, version)
		return version
	except:
		print('%d %s get milestone error'%(bugid, changeset))
		return '100'

def annotate(bugid, changesetList):
	bug_dir = 'F:/data/firefox/diff/' + str(bugid)
	if not os.path.exists(bug_dir):
		os.mkdir(bug_dir)
	record = open(bug_dir + '/' + 'files.txt', 'w')
	changedfiles = []
	notCState = True
	onlyAddLine = True
	max_bug_induce = 0
	min_bug_induce = 10000000
	max_changeset = ''
	min_changeset = ''

	os.chdir('F:/data/firefox/mozilla-release')
	for changeset in changesetList:
		diff_filename = bug_dir + '/' + changeset + '.txt'
		if not os.path.exists(diff_filename):
			export_cmd = 'hg export -r ' + changeset + '> ' + diff_filename
			os.system(export_cmd)

		diff_file = open(diff_filename, 'r')
		try:
			lines = diff_file.readlines()
			#print('ok')
			#solvechangeset(bugid, bug_dir, changeset, diff_line)
			start = 0
			cnt = 0
			changefilename = ''

			for i in range(len(lines)):
				line = lines[i]
				#print(line)
				if 'diff -r' in line:
					parent = line.split(' ')[2]

					if cnt > 0:
						#print(changefilename)
						if changefilename not in changedfiles:
							changedfiles.append(changefilename)
							min_revision, max_revision, max_revision_changeset, min_revision_changeset = solvechangefile(changefilename, lines[start:i+1], parent, record, bugid)
							
							if min_revision != -1:
								notCState = False
								if min_revision != 10000000:
									onlyAddLine = False
									if max_bug_induce <  max_revision:
										max_bug_induce = max_revision
										max_changeset = max_revision_changeset
									if min_bug_induce > min_revision:
										min_bug_induce = min_revision
										min_changeset = min_revision_changeset
					cnt += 1

					words = line.split(' ')
					if len(words) > 5:
						changefilename = words[-1].strip()
						start = i + 3
					else:
						changefilename = lines[i + 1].strip()
						start = i + 4
			end = i + 1
			if changefilename not in changedfiles:
				changedfiles.append(changefilename)
				min_revision, max_revision, max_revision_changeset, min_revision_changeset = solvechangefile(changefilename, lines[start:end], parent, record, bugid)
				if min_revision != -1:
					notCState = False
					if min_revision != 10000000:
						onlyAddLine = False
						if max_bug_induce <  max_revision:
							max_bug_induce = max_revision
							max_changeset = max_revision_changeset
						if min_bug_induce > min_revision:
							min_bug_induce = min_revision
							min_changeset = min_revision_changeset
		except:
			#print('%d can not read changeset file'%bugid)
			with open('F:/data/firefox/annotateError.txt', 'a') as file:
				file.write('%d\n'%bugid)
			return

	if notCState:
		with open('F:/data/firefox/notCBug.txt', 'a') as file:
			file.write('%d\n'%bugid)
	elif onlyAddLine:
		with open('F:/data/firefox/onlyAddLineBug.txt', 'a') as file:
			file.write('%d\n'%bugid)
	elif min_bug_induce == 10000000:
		print('%d has error!'%bugid)
	else:
		#min_version = getMilestone(bugid, min_changeset)
		#max_version = getMilestone(bugid, max_changeset)
		#result = 'result %s %s %d %s %d %s\n'%(min_version, max_version, min_bug_induce, min_changeset, max_bug_induce, max_changeset)
		result = 'result %d %s %d %s\n'%(min_bug_induce, min_changeset, max_bug_induce, max_changeset)
		record.write(result)
		update(bugid, min_bug_induce, max_bug_induce)


def main():
	sql = 'select bugid, earliestChangeset, min_revision from vul2changeset_0527'
	cur = conn.cursor()
	cur.execute(sql)
	conn.commit()

	result = cur.fetchall()
	
	for r in result:
		bugid = r[0]
		changesetList = r[1].split(' ')
		if r[2] == None:
			print(bugid)
			annotate(bugid, changesetList)
			#
		#if bugid == 1549768:
		
		#return 

def main():
	sql = 'select bugid, earliestChangeset, min_revision from vul2changeset_0527'
	cur = conn.cursor()
	cur.execute(sql)
	conn.commit()

	result = cur.fetchall()
	
	for r in result:
		bugid = r[0]
		changesetList = r[1].split(' ')
		if r[2] == None:
			print(bugid)
			annotate(bugid, changesetList)

if __name__ == '__main__':
	main()
	#getversion()
	#os.chdir('../../firefox')
	#print solvechangeset('25b143f03be4', 'E:/firefox-diff/623998')