# -*- coding: utf-8 -*-
import os
import re
import shutil

def solvediff(name, lines, diff_dir):
	#print(lines)
	revision = ''
	filePath = ''
	
	i = 0
	while lines[i][0:3] != '+++':
		line = lines[i].strip('\n')
		if line[0:3] == '---':
			temp = line.split('\t')
			if len(temp) == 3:
				filePath = temp[0].split(' ')[1]
				revision = temp[-1]
				#print(filePath, revision)
			break
		i = i + 1	

	if filePath == '':
		print(lines)
		print(f'{name} can not find changed file!')
	if '.' not in filePath:
		return -1
	if filePath == 'version.c':
		return -1

	filetype = filePath.split('.')
	filetype = filetype[-1]
	#print(filetype)
	if 'c' != filetype and 'h' != filetype:
		return -1
	
	#print(name, filePath, revision)
	
	vulline = []
	vulline_number = []
	line_pattern = re.compile('@@\s-(\d+),')

	note = False
	copy = False
	current = 0
	for i in range(len(lines)):
		line = lines[i]
		if line == '':
			current += 1
			continue
		if line[0:2] == '@@':
			note = False
			copy = True
			current = int(line_pattern.findall(line)[0])
		else:
			#print(len(line))
			if line[0] != '+' and current != 0:
				current += 1
				#qudiao zhushi
			if line[0] == '-' and line[0:3] != '---':
				line_strip = line[1:].strip()
				if line_strip[0:2] == '//':
					continue
				elif line_strip[0:2] == '/*':
					if line_strip[-2:] == '*/':
						continue
					note = True
				elif line_strip[-2:] == '*/' and '/*' not in line_strip:
					note = False
				elif note == False:
					'''
					if name == '3.1/common/003_fdalloc2.patch':
						print(line_strip, line_strip[-1])
						print(line_strip[0] == '*', line_strip[-1] not in [',', ';'])
						'''
					if line_strip == '' or '$' in line_strip or line_strip[-1] == '.' or line_strip == '*'\
					or (line_strip[0] == '*' and line_strip[-1] not in [',', ';']):
						continue 
					if copy:
						vulline_number.append(current - 1)
						vulline.append(lines[i])
	if len(vulline) < 1:
		return 0
	
	record_path = diff_dir + '/record.txt'
	record = open(record_path, 'a', encoding='utf-8', errors='ignore')
	record.write(filePath + ' ' + revision)
	record.write('\n')
	record.write(str(len(vulline)))
	record.write('\n') 
	for i in vulline_number:
		record.write(str(i) + ' ')
	record.write('\n')
	for i in vulline:
		record.write(i)
		record.write('\n') 
	return 1

def solvepatch(name, file_path, addline_vul, not_c_vul):#此name是补丁名称，path是补丁的路径
	print(name)
	diff_dir = 'F:/data/OpenBSD/diff1'
	#name = 6.0/common/026_perl.patch.sig
	tmp = name.split('/')
	version = tmp[0].replace('.', '')
	patch = tmp[2].replace('.patch.sig', '')
	diff_dir = f'{diff_dir}/{version}-{patch}'

	if not os.path.exists(diff_dir):
		os.mkdir(diff_dir)
	if os.path.exists(diff_dir + '/record.txt'):
		os.remove(diff_dir + '/record.txt')
	record = open(diff_dir + '/record.txt', 'w')
	record.write(name + '\n')
	record.close()

	#try:
	file = open(file_path, 'r', encoding='utf-8', errors='ignore')  #是在装有openbsd文件夹下运行吗
	lines = []
	cnt = 0#已读取index个数的标记
	state_not_C = True
	state_addline = True
	for line in file:   #可以分行读python文件
		line = line.rstrip()
		#print("no")
		#如果发现index，就是一个diff
		if 'Index:' in line:
			if cnt > 0:#已经读取了index就进行solvediff操作
				ans = solvediff(name, lines, diff_dir)
				print(ans)
				if ans >= 0:
					state_not_C = False
				if ans == 1:
					state_addline = False
			cnt+=1
				#myprint(lines)
			lines = [] 
		#if line != '\r\n':
		lines.append(line)
	ans = solvediff(name, lines, diff_dir)
	print(ans)
	if ans >= 0:
		state_not_C = False
	if ans == 1:
		state_addline = False
	file.close()
	print(state_not_C, state_addline)
	if state_not_C:
		not_c_vul.write(f'{name}\n')
	else:
		if state_addline:
			addline_vul.write(f'{name}\n')
	#except:
		#print(file_path + " can not open!")	
def solvepatch1(name, file_path, addline_vul, not_c_vul):#此name是补丁名称，path是补丁的路径
	print(name)
	diff_dir = 'F:/data/OpenBSD/diff1'
	#name = 6.0/common/026_perl.patch.sig
	diff_dir = f'{diff_dir}/{name}'

	if not os.path.exists(diff_dir):
		os.mkdir(diff_dir)
	if os.path.exists(diff_dir + '/record.txt'):
		os.remove(diff_dir + '/record.txt')
	record = open(diff_dir + '/record.txt', 'w')
	record.write(name + '\n')
	record.close()

	#try:
	file = open(file_path, 'r', encoding='utf-8', errors='ignore')  #是在装有openbsd文件夹下运行吗
	lines = []
	cnt = 0#已读取index个数的标记
	state_not_C = True
	state_addline = True
	for line in file:   #可以分行读python文件
		line = line.rstrip()
		#print("no")
		#如果发现index，就是一个diff
		if 'Index:' in line:
			if cnt > 0:#已经读取了index就进行solvediff操作
				ans = solvediff(name, lines, diff_dir)
				print(ans)
				if ans >= 0:
					state_not_C = False
				if ans == 1:
					state_addline = False
			cnt+=1
				#myprint(lines)
			lines = [] 
		#if line != '\r\n':
		lines.append(line)
	ans = solvediff(name, lines, diff_dir)
	print(ans)
	if ans >= 0:
		state_not_C = False
	if ans == 1:
		state_addline = False
	file.close()
	print(state_not_C, state_addline)
	if state_not_C:
		not_c_vul.write(f'{name}\n')
	else:
		if state_addline:
			addline_vul.write(f'{name}\n')

def checkvul():
	record = open('OpenBSDSecurityVuln_norepeat.txt', 'r')
	addline_vul = open('result_addline.txt', 'w')
	not_c_vul = open('result_notC.txt', 'w')
	for line in record:
		name = line.strip().split(' ')[0]
		#6.0_026_perl
		version = name.split('_')[0]
		patchname = name[4:]
		filename = patchname + '.patch.sig'
		#
		file_path = f'F:/data/OpenBSD/patches/{version}/common/{filename}'
		if os.path.exists(file_path):
			solvepatch(f'{version}/common/{filename}', file_path, addline_vul, not_c_vul)
		else:
			print(f'{name} can not find')
		#return

	record.close()
	addline_vul.close()
	not_c_vul.close()

'''
def notC():
	not_c_vul = open('result_notC.txt', 'r')
	for line in not_c_vul:
		name = line.strip('\n')
		file_path = 'E:/python/openbsd/patches/' + name
		print(name)
		solvepatch(name, file_path)

	not_c_vul.close()
'''

def checkPre():
	record = open('vulnPre.txt', 'r')
	addline_vul = open('result_addline.txt', 'a')
	not_c_vul = open('result_notC.txt', 'a')
	for line in record:
		name = line.strip()
		#25-007_chflags
		name = line.strip().split(' ')[0]
		#6.0_026_perl
		filename = name.replace('-', '/common/') + '.patch.sig'
		filename = filename[0] + '.' + filename[1:]
		file_path = f'F:/data/OpenBSD/patches/{filename}'
		if os.path.exists(file_path):
			solvepatch1(name, file_path, addline_vul, not_c_vul)
		else:
			print(f'{name} can not find')
		#return

	record.close()
	addline_vul.close()
	not_c_vul.close()


def main():
	checkPre()


if __name__ == '__main__':
	main()
	#solvepatch1('5.4/common/015_nginx.patch', 'E:/python/openbsd/patches/5.4/common/015_nginx.patch', )

