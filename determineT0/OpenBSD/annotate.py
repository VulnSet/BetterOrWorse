import os
import random

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

def test(vulname, vul_dir):
	all_vul_in_one_version = '2.3'
	earliest_version = '7.0'

	record = open(vul_dir + '/' + 'record.txt', 'r')
	each_file_version = open(vul_dir + '/' + 'each_file_version.txt', 'w')

	repository = '/mnt/f/data/OpenBSD/cvs'
	os.chdir(repository)

	name = record.readline().strip()
	#print(name)
	for line in record:
		tmp = line.strip()
		if ' ' not in tmp:
			vul_file = tmp
			print(f'{vulname} can not get file {vul_file} revision')
			return 
		else:
			vul_file = tmp.split(' ')[0]
			revision = tmp.split(' ')[1]

		annotate_cmd = 'cvs annotate -r%s %s'%(revision, vul_file)
		print(os.getcwd(), annotate_cmd)
		result = os.popen(annotate_cmd).readlines()
		#print(len(result))

		max_revision = '0.0'
		min_revision =  '10000.0'
		number = int(record.readline())
		vul_number_list = record.readline().strip().split(' ')

		for n in vul_number_list:
			tmp = result[int(n) - 1].split(' ')[0]
			if compareversion(tmp, max_revision) == 1:
				max_revision = tmp
			if compareversion(min_revision, tmp) == 1:
				min_revision = tmp 

		log_cmd = 'cvs log %s'%(vul_file)
		result = os.popen(log_cmd).readlines()
		print(result)
		for l in result:
			if 'symbolic names:' in l:
				break
		min_version = '7.0'
		min_version2 = '7.0'
		for l in result:
			if 'keyword substitution' in l:
				if min_version > all_vul_in_one_version:
					all_vul_in_one_version = min_version
				if min_version2 < earliest_version:
					earliest_version = min_version2
				print_line = '%s %s %s %s %s %s %s\n'%(name, vul_file, revision, max_revision, min_version, min_revision, min_version2)
				each_file_version.write(print_line)
				#print(name, vul_file, max_revision, revision, min_version)
				break
			if 'BASE' not in l or 'OPENBSD' not in l:
				continue
			tmp = l.split(':')
			r = tmp[1].strip() 
			if compareversion(r, max_revision) >= 0:
				version = tmp[0].strip()[8:11].replace('_', '.')
				#print(version)
				if version < min_version:
					min_version = version				

			if compareversion(r, min_revision) >= 0:
				version = tmp[0].strip()[8:11].replace('_', '.')
				#print(version)
				if version < min_version:
					print(l)
					min_version2 = version

		i = 0
		while i < number:
			record.readline()
			i += 1

	print_line = '%s %s\n'%(name, all_vul_in_one_version)
	ans.write(print_line)

def solveVul(vulname, vul_dir):
	try:
		all_vul_in_one_version = '2.3'
		earliest_version = '7.0'

		record = open(vul_dir + '/' + 'record.txt', 'r')
		each_file_version = open(vul_dir + '/' + 'each_file_version.txt', 'w')

		repository = '/mnt/f/data/OpenBSD/cvs'
		os.chdir(repository)

		name = record.readline().strip()
		#print(name)
		for line in record:
			tmp = line.strip()
			if ' ' not in tmp:
				vul_file = tmp
				print(f'{vulname} can not get file {vul_file} revision')
				return 
			else:
				vul_file = tmp.split(' ')[0]
				revision = tmp.split(' ')[1]

			annotate_cmd = 'cvs annotate -r%s %s'%(revision, vul_file)
			print(os.getcwd(), annotate_cmd)
			result = os.popen(annotate_cmd).readlines()
			#print(len(result))

			max_revision = '0.0'
			min_revision =  '10000.0'
			number = int(record.readline())
			vul_number_list = record.readline().strip().split(' ')

			for n in vul_number_list:
				tmp = result[int(n) - 1].split(' ')[0]
				if compareversion(tmp, max_revision) == 1:
					max_revision = tmp
				if compareversion(min_revision, tmp) == 1:
					min_revision = tmp 

			log_cmd = 'cvs log %s'%(vul_file)
			result = os.popen(log_cmd).readlines()
			print(result)
			for l in result:
				if 'symbolic names:' in l:
					break
			min_version = '7.0'
			min_version2 = '7.0'
			for l in result:
				if 'keyword substitution' in l:
					if min_version > all_vul_in_one_version:
						all_vul_in_one_version = min_version
					if min_version2 < earliest_version:
						earliest_version = min_version2
					print_line = '%s %s %s %s %s %s %s\n'%(name, vul_file, revision, max_revision, min_version, min_revision, min_version2)
					each_file_version.write(print_line)
					#print(name, vul_file, max_revision, revision, min_version)
					break
				if 'BASE' not in l or 'OPENBSD' not in l:
					continue
				tmp = l.split(':')
				r = tmp[1].strip() 
				if compareversion(r, max_revision) >= 0:
					version = tmp[0].strip()[8:11].replace('_', '.')
					#print(version)
					if version < min_version:
						min_version = version				

				if compareversion(r, min_revision) >= 0:
					version = tmp[0].strip()[8:11].replace('_', '.')
					#print(version)
					if version < min_version:
						print(l)
						min_version2 = version

			i = 0
			while i < number:
				record.readline()
				i += 1

		print_line = '%s %s\n'%(name, all_vul_in_one_version)
		ans.write(print_line)
		#os.chdir('/media/shijian/新加卷/Openbsd/')
	except:
		print(vulname + ' has error')

def main():
	root_dir = '/mnt/f/data/OpenBSD/diff/'
	file = open('annotate_vul.txt', 'r')
	for line in file:
		line = line.strip().split(' ')
		vulname = line[0].replace('.', '')
		vulname = f"{vulname[:2]}-{vulname[3:]}"
		diff_dir = root_dir + vulname
		#solveVul(vulname, diff_dir)
		test(vulname, diff_dir)
		return 

if __name__ == '__main__':
	main()


	徐老师，这几天我在处理数据，首先是收集漏洞exploit的时间，有3个数据源，NVD中的reference（
	链接集中在exploit-db，securityfocus，bugzilla.mozilla.org, www.openwall.com中），
	Securityfocus中的exploit页面，exploit-db。两个软件找到的exploit分别是OpenBSD 100个，Firefox166个。
	把OpenBSD，Firefox的漏洞聚合在一起（收集Securityfocus中的Firefox漏洞，map到CVE跟识别exploit并提取时间是一起做的）
	截止到17号才把OpenBSD漏洞和Firefox漏洞聚合，把漏洞被发现的时间T1（bugzilla中bug opened的时间，2068个漏洞中有236个漏洞拒绝访问无法获取），漏洞被利用的时间（NVD，BID，exploit-db中的exploit）收集挖完。
	这部分数据没有写到文章里的原因是有可能根据后面数据的处理结果调整，比如会去掉不是C/C++语言的漏洞，会去掉两个Firefox大版本之间出现并修复的漏洞。

	然后补充17年到20年的漏洞数据。补充的内容是漏洞的产生时间T0，同时补充所有漏洞数据的T0’（所有删除行的最早的revision）。
	两个软件是不同的处理过程，OpenBSD是提取‘-’行，同时排除非C语言漏洞，对有‘-’行的漏洞在代码库中用annotate确定revision和version，对只有‘+’的漏洞修复
	需要提取函数，在历史版本中搜索；
	Firefox是从commit log中提取bug对应的commit，然后提取‘-’，排除非C/C++的漏洞，对有‘-’漏洞执行annotate，对只有‘+’漏洞提取函数并搜索。
	需要调整原来的程序并重新跑一遍原来的漏洞数据。这两天我先跑OpenBSD的漏洞数据，包括先从OpenBSD漏洞中提取修改行，然后用annotate追溯
	revision。克隆OpenBSD的源码库和执行程序时遇到了问题，克隆方式不对导致无法运行cvs命令，这个问题昨天解决。
	还有一个麻烦的地方是提取漏洞所在函数，需要识别并提取‘+’行所在函数体，原来写的程序是用antlr对文件语法解析提取函数，坏处是易出错而且识别C++函数和OpenBSD
	中的C语法有问题，我想用libclang重写一下。

	
