#This script is used to add CMAP parameters in amber prmtop file
#Programmed by Wei Wang, Wei Ye, Dingjue Ji, and Dong Song in perl.
#Rewrite with python by Hao Liu

import os,sys,re
import argparse
import time
import math

def InputOptions():
	version = '1.1'
	update_info = '\n2020/05/97: Add support for ESFF1 residue environmental-specific force field.'
	version_info = sys.argv[0] + ' Version %s , updated 2020/05/07.  %s' % (version, update_info)
	options = argparse.ArgumentParser(description = 'Following is detail description')
	options.add_argument('-v', '--ver', action = 'version', version = version_info, help = 'Version')
	options.add_argument('-p', '--prmtop', required = True, type = str, help = 'amber prmtop file generated by tleap')
	options.add_argument('-c', '--cmap', required = True, type = str, help = 'user specific CMAP parameter file')
	options.add_argument('-o', '--output', required = True, type = str , help = 'prmtop file within CMAP energy terms')
	options.add_argument('-e', '--env', action = 'store_true', help = 'add environment-specific CMAP energy terms')
	options.add_argument('-s', '--silent', action = 'store_true', help = 'add CMAP for all residues without interacting information')
	options = options.parse_args()
	return options

def StartInfor():
	print('-' * 80)
	print('Adding CMAP parameters into AMBER prmtop file which is generated by tleap')
	print('Programmed by Wei Wang, Wei Ye, Dingjue Ji, and Dong Song in Perl.')
	print('Rewrite in Python by Hao Liu')
	print('-' * 80)

def Color(string, color):
	colors = {'black':'\033[30m', 'red':'\033[31m', 'green':'\033[32m', 'yellow':'\033[33m',
    		  'blue':'\033[34m', 'purple':'\033[35m', 'cyan':'\033[36m', 'white':'\033[37m',
			  'off':'\033[0m'}
	return colors[color]+str(string)+colors['off']

def FileExists(input_file):
	if not os.path.isfile(input_file):
		print('No such file: %s' % input_file)
		exit()

def Env(residue):
	protein_nonpolar = ['ALA', 'ILE', 'LEU', 'MET', 'PHE', 'PRO', 'TRP', 'VAL', 'ACE', 'NME']
	protein_polar = ['ARG', 'ASN', 'ASP', 'CYS', 'CYX', 'GLN', 'GLU', 'GLY', 'HID', 'HIE', 'HIP', 'HIS', 'LYS', 'SER', 'THR', 'TYR', 'NHE']
	env = 0
	if residue in protein_nonpolar:
		env = 1
	elif residue in protein_polar:
		env = 2
	return env

def ReadTop(top_lines, check, format_1, format_2):
	flag = 0
	content = []
	string = ''
	i = 0
	while i < len(top_lines):
		search = re.search('FLAG %s' % check, top_lines[i])
		if search:
			flag = 1
			i+=2

		if flag == 1:
			search = re.search('^%', top_lines[i])
			if not search:
				string += top_lines[i]
				for j in range(format_1):
					if top_lines[i][j*format_2:(j+1)*format_2].strip() != '':
						content.append(top_lines[i][j*format_2:(j+1)*format_2].strip())
			else:
				flag = 0
		i += 1
	return content, string
	
def Array2String(array):
	string = ''
	array_sorted = array
	array_sorted.sort()
	array = []
	#delete the same elements
	for i in array_sorted:
		if i not in array:
			array.append(i)
	if len(array) == 0:
		string += 'NONE'
	elif len(array) == 1:
		string += str(array[0])
	else:
		for i in range(len(array)):
			array[i] = int(array[i])
		for i in range(len(array)):
			if i == 0:
				string += str(array[i])
				if array[i+1] == array[i]+1:
					string += '-'
				else:
					string += ','
			elif i == len(array)-1:
				string += str(array[i])
			else:
				if array[i+1] == array[i]+1:
					if array[i] == array[i-1]+1:
						string += ''
					else:
						string += str(array[i]) + '-'
				else:
					string += str(array[i]) + ','
	return string

def Display(display_mark, res_type, res_label):
	display_type = {}
	for i in range(len(res_type)):
		if res_type[i] == display_mark:
			if res_label[i] not in display_type:
				display_type[res_label[i]] = [i+1]
			else:
				display_type[res_label[i]].append(i+1)

	if len(display_type) >= 1:
		print('\n==%s==' % display_mark)
		for t in display_type:
			print('%s: %s' % (t, Array2String(display_type[t])))

def String2Array(string):
	array = []
	for s in string.split(','):
		if '-' in s:
			if int(s.split('-')[0]) < int(s.split('-')[1])+1:
				array.extend(range(int(s.split('-')[0]), int(s.split('-')[1])+1))
			else:
				array.extend(range(int(s.split('-')[1]), int(s.split('-')[0])+1))
		elif s != '':
			array.append(int(s))
	
	array_sorted = array
	array_sorted.sort()
	array = []
	#delete the same elements
	for i in array_sorted:
		if i not in array:
			array.append(i)

	return array

def InputCheck(string, display_index):
	check = 0
	array = []
	if re.match('^all$', string, re.I):
		for i in display_index:
			array.append(i-1)
		check += 1
		#print('CMAP parameters will be added to %s residues' % Color('ALL', 'blue'))
	elif re.search('[^0-9,-]', string):
		print('Syntax Error, please check you input %s' % Color(string, 'red'))
	else:
		array = String2Array(string)
		check += 1
		for i in range(len(array)):
			array[i] = array[i] - 1
	return check, array

def main():
	options = InputOptions()
	prmtop = options.prmtop
	cmap   = options.cmap
	output = options.output
	env    = options.env
	silent = options.silent

	## print information
	StartInfor()
	
	## check if the input file is exists
	FileExists(prmtop)
	FileExists(cmap)
	search = re.search('.*(ff\d{2}).*', cmap)
	if search:
		force_field = search.group(1)
	elif re.search('ESFF1', cmap):
		force_field = 'ff14SB'

	## defined residues name
	known_protein = [
		'ALA', 'ARG', 'ASN', 'ASP', 'CYS',
		'CYX', 'GLN', 'GLU', 'GLY', 'HIS',
		'HID', 'HIE', 'HIP', 'ILE', 'LEU',
		'LYS', 'MET', 'PHE', 'PRO', 'SER',
		'THR', 'TRP', 'TYR', 'VAL', 'ACE', 
		'NHE', 'NME']
	known_protein_abbr = [
		'A', 'R', 'N', 'D', 'C',
		'C', 'Q', 'E', 'G', 'H',
		'H', 'H', 'H', 'I', 'L',
		'K', 'M', 'F', 'P', 'S',
		'T', 'W', 'Y', 'V', 'x',
		'y', 'z']
		
	cmap_residues =  [
		'ALA', 'ARG', 'ASN', 'ASP', 'CYS',
		'CYX', 'GLN', 'GLU', 'GLY', 'HIS',
		'HID', 'HIE', 'HIP', 'ILE', 'LEU',
		'LYS', 'MET', 'PHE', 'PRO', 'SER',
		'THR', 'TRP', 'TYR', 'VAL']
	
	##Step 1: Read CMAP parameter file
	print('Reading CMAP parameters file: %s' % Color(cmap, 'blue'))
	cmap_file = open(cmap, 'r')
	cmap_parameters = []
	cmap_type = [] #for protein or others
	cmap_order = []
	cmap_name = []
	cmap_count = []
	print('  Reading CMAP parameters of:')
	for line in cmap_file.readlines():
		if re.search('^#', line):
			continue
		match = re.match('%FLAG\s([\w]+)_MAP(\d?)(_?[0-9]?[0-9]?)', line)
		if match:
			left = '0'
			right = '0'
			if(len(cmap_name) % 5 == 4):
				print('  %s' % Color(match.group(1), 'blue'))
			else:
				print('  %s' % Color(match.group(1), 'blue'), end = '')
			res = match.group(1)
			if not match.group(2):
				cmap_type.append('Protein')
				cmap_order.append('0')
				order = '0'
			else:
				cmap_type.append('Others')
				cmap_order.append('9')
				order = '9'
				
			if match.group(3):
				match2 = re.match('_([0-9])([0-9])', match.group(3))
				if match2:
					left = match2.group(1)
					right = match2.group(2)
			temp_name = '%s%s%s-%s' % (left, res, right, order)
			cmap_name.append(temp_name)
			cmap_parameters.append('')
			cmap_count.append(0)
		else:
			cmap_parameters[-1] += line
			match = re.match('(\s*[0-9\.-]+){8}', line)
			if match:
				cmap_count[-1] += 8
			#else:
			#	print(line)
	print()

	#print(cmap_name)
	#print('  %d\t%d\t%d\t%d\t%d' % (len(cmap_parameters), len(cmap_type), len(cmap_order), len(cmap_name), len(cmap_count)))
	if len(cmap_parameters) < 1:
		print('  CMAP parameter FORMAT error!')
	else:
		for i in range(len(cmap_count)):
			if cmap_count[i] != 576:
				print('  Wrong number in CMAP parameter for: %s' % Color(cmap_name[i], 'blue'))
				exit()
	#print(cmap_count)
	print('Read CMAP file successfully!\n')

	##Step 2: Read prmtop file generated by tleap
	print('Reading prmtop file %s' % Color(prmtop, 'blue'))
	top = open(prmtop, 'r')
	top_lines = top.readlines()
	top.close()

	# Read Atom Name
	(atom_name, atom_name_string) = ReadTop(top_lines, 'ATOM_NAME', 20, 4)
	if len(atom_name) < 1:
		print('  %s not found, please check your prmtop file: %s' % (Color('FLAG ATOM_NAME', 'red'), Color(prmtop, 'blue')))
		print('  Make sure your prmtop file was generated by tleap successfully')
		exit()

	# Read Residues label
	(res_label, res_label_string) = ReadTop(top_lines, 'RESIDUE_LABEL', 20, 4)
	if len(res_label) < 1:
		print('  %s not found, please check your prmtop file: %s' % (Color('FLAG RESIDUE_LABEL', 'red'), Color(prmtop, 'blue')))
		print('  Make sure your prmtop file was generated by tleap successfully')
		exit()

	# Read Residues pointer
	(res_pointer, res_pointer_string) = ReadTop(top_lines, 'RESIDUE_POINTER', 10, 8)
	if len(res_pointer) < 1:
		print('  %s not found, please check your prmtop file: %s' % (Color('FLAG RESIDUE_POINTER', 'red'), Color(prmtop, 'blue')))
		print('  Make sure your prmtop file was generated by tleap successfully')
		exit()

	# Read Lennard Jones ACOEF
	(lj_acoef, lj_acoef_string) = ReadTop(top_lines, 'LENNARD_JONES_ACOEF', 5, 16)
	if len(lj_acoef) < 1:
		print('  %s not found, please check your prmtop file: %s' % (Color('FLAG LENNARD_JONES_ACOEF', 'red'), Color(prmtop, 'blue')))
		print('  Make sure your prmtop file was generated by tleap successfully')
		exit()

	(lj_bcoef, lj_bcoef_string) = ReadTop(top_lines, 'LENNARD_JONES_BCOEF', 5, 16)
	if len(lj_bcoef) < 1:
		print('  %s not found, please check your prmtop file: %s' % (Color('FLAG LENNARD_JONES_ACOEF', 'red'), Color(prmtop, 'blue')))
		print('  Make sure your prmtop file was generated by tleap successfully')
		exit()

	print('Read prmtop file successfully!\n')

	##Step3: Select the residues which will CMAP energy terms will be added
	print('Select the residues which CMAP energy terms will be added')
	res_type = []
	know_modified_res = {}

	# check residues type
	for i in range(len(res_label)):
		name = res_label[i]
		if name in known_protein:
			res_type.append(name)
		elif re.search('[\+\-]', name):
			res_type.append('Ions')
		elif name == 'WAT':
			res_type.append('Solvent')
		elif re.search('^(D|R)?[AGCTU][35]?$', name):
			res_type.append('NucAcids')
		elif name in know_modified_res:
			res_type.append('m%s' % know_modified_res[name])
		elif silent:
			res_type.append('Others')
		else:
			# save atom name of other residues
			other_atom_name = []
			if i != len(res_label)-1:
				for j in range(int(res_pointer[i]), int(res_pointer[i+1])):
					other_atom_name.append(atom_name[j])
			else:
				for j in range(int(res_pointer[i]), len(atom_name)-1):
					other_atom_name = []
			#print(other_atom_name)

			# detect the modified amino acids residues
			if 'N' in other_atom_name and 'CA' in other_atom_name and 'C' in other_atom_name and 'O' in other_atom_name:
				print('Amino acid like unknown residue %s found with residue number %s' % (Color(name, 'red'), Color(i+1, 'blue')))
				print('Is that a modified AA residues[Y/N]')
				binary = input()
				if re.match('y(es)?', binary, re.I):
					check = 0
					while check < 1:
						print('\nPlease tell me %s is modificated residue of which AA.' % name)
						print('Single and triple character abbreviations are both suppored:[ALA or A]')
						aa_input = input()
						aa_upper = aa_input.upper()
						if aa_upper in known_protein:
							print(  'Taking %s as modified %s' % (Color(name,'blue'), Color(aa_upper, 'blue')))
							res_type.append('m%s' % aa_upper)
							know_modified_res[name] = aa_upper
							check += 1
						elif aa_upper in known_protein_abbr:
							aa_upper = known_protein[known_protein_abbr.index(aa_upper)]
							print(  'Taking %s as modified %s' % (Color(name,'blue'), Color(aa_upper, 'blue')))
							res_type.append('m%s' % aa_upper)
							know_modified_res[name] = aa_upper
							check += 1
						else:
							print(  "I don't known what is %s" % Color(aa_input))
				else:
					print('Unknown residue %s found, ignore it!' % Color(name, 'red'))
					res_type.append('Others')
			else:
				print('Unknown residue %s found, ignore it!' % Color(name, 'red'))
				res_type.append('Others')
	print()

	# display residues
	print('Residues in prmtop file %s:' % Color(prmtop, 'blue'))
	print('Disorder-promoting residues are labelled in %s' % Color('blue', 'blue'))
	print('Unknown residues are labelled with "*"')
	if len(know_modified_res) >= 1:
		print('Modified residues are labelled in %s' % Color('red', 'red'))
	
	# amino acid
	display_string = [] #residues string
	display_index = [] # array for indecies of residues in 'Amino Acid'

	for i in range(len(res_type)):
		name = res_type[i]
		search = re.search('(m?)(\w+)', name)
		if search.group(2) in cmap_residues:
			if search.group(1):
				display_string.append(Color(known_protein_abbr[known_protein.index(search.group(2))], 'red'))
				display_index.append(i+1)
			else:
				display_string.append(Color(known_protein_abbr[known_protein.index(search.group(2))], 'blue'))
				display_index.append(i+1)
		elif search.group(2) in known_protein:
			display_string.append(Color(known_protein_abbr[known_protein.index(search.group(2))], 'white'))
			display_index.append(i+1)

	if len(display_index) >= 1:
		print('\n==Amino Acids==')
		seq_len = 0
		count = 0
		for i in range(int(display_index[0]), int(display_index[-1]+1)):
			if i in display_index:
				print(display_string[display_index.index(i)], end='')
				seq_len += 1
			else:
				print('*', end='')
				seq_len += 1
			if seq_len % 5 == 0 and seq_len != 50:
				print(' ', end='')

			if seq_len == 50:
				print()
				for j in range(10):
					print('%-6s' % str(display_index[0]+j*5+count*50), end='')
				print()
				seq_len = 0
				count += 1
		print()
		#print('seq_len is: %d' % seq_len)
		for j in range(int((seq_len-1)/5 + 1)):
			print('%-6s' % str(display_index[0]+j*5+count*50), end='')
		print()
	else:
		print('No amino acid residue is found in prmtop file: %s!' % Color(prmtop, 'red'))
		print('Exit now!')
		exit()

	# nucleic acids
	Display('NucAcids', res_type, res_label)

	# ions
	Display('Ions', res_type, res_label)

	# solvent
	Display('Solvent', res_type, res_label)

	# others
	Display('Others', res_type, res_label)
	print()
	
	# user select residues
	res_select = []
	res_select_env = []
	check = 0
	if not silent:
		while check < 1:
			print('Please select amino acid residues that CMAP energy terms will be added')
			print('"-" and "," are supported. Ex.: 1-20,35,39,40-80')
			print('If all residues are considered, type "all"')
			select = input()
			(check, res_select) = InputCheck(select, display_index)
			
		res_select_env = []
		if env:
			check = 0
			while check < 1:
				print('Please select amino acid residues that %s CMAP energy terms will be added' % Color('environment-specific', 'blue'))
				print('"-" and "," are supported. Ex.: 1-20,35,39,40-80')
				print('If all residues are considered, type "all"')
				select = input()
				(check, res_select_env) = InputCheck(select, display_index)
	else:
		(check, res_select) = InputCheck('all', display_index)
		if env:
			(check, res_select_env) = InputCheck('all', display_index)

	res_single = []
	res_env = []
	res_error = []
	for res in res_select:
		if res_type[res] in ['Ions', 'Solvent', 'NucAcids', 'Others']:
			res_error.append(res+1)
		else:
			if res in res_select_env:
				res_env.append(res+1)
			else:
				res_single.append(res+1)
	for res in res_select_env:
		if res_type[res] in ['Ions', 'Solvent', 'NucAcids', 'Others']:
			res_error.append(res+1)
	print(res_single)
	if len(res_error) > 1:
		print('The following selected residues are %s amino acids, ignore it!' % Color('NOT', 'red'))
		print(Array2String(res_error))
	print('%s CMAP energy terms will be added to the following resiudes:' % Color('Residue-specific', 'blue'))
	print(Array2String(res_single))
	if env:
		print('%s CMAP energy terms will be added to the following residues:' % Color('Environment-specific', 'blue'))
		print(Array2String(res_env))
	print()

	
	##Step 4: add CMAP energy sterms to selected residues
	print('Checking if CMAP parameters is available for selected residues')
	time.sleep(1)
	res_strip = []
	res_cmap = []
	res_cmap_num = []
	for i in res_single:
		if i == 1:
			print('Residue %s is a terminal residues, CMAP energy terms will not be added' % Color('%s%-4d' % (res_label[i-1], i), 'blue'))
			res_strip.append(i)
		elif i != len(res_label): # not the last residue
			for j in range(int(res_pointer[i-1])-1, int(res_pointer[i])-1):
				if atom_name[j] == 'H3' or atom_name[j] == 'OXT':
					print('Residue %s is a terminal residues, CMAP energy terms will not be added' % Color('%s%-4d' % (res_label[i-1], i), 'blue'))	
					res_strip.append(i)
			if i in res_strip:
				continue
			# check if cmap parameter of select residues are exists
			match = re.match('m?([A-Z]+)',res_type[i-1])
			res_name = match.group(1)
			if res_name in ['HIP', 'HIE', 'HID']:
				res_name = 'HIS'
			elif res_name == 'CYX':
				res_name = 'CYS'
			name = '0%s0-0' % res_name
			if name not in cmap_name:
				print('Warning: %s CMAP parameter is not found for this residue %s'
					  %(Color('Residue-specific', 'blue'), Color('%s%-4d' %(res_label[i-1], i), 'red')))
				res_strip.append(i)
			else:
				res_cmap.append(name)
				res_cmap_num.append(i-1)
		else:
			print('Residue %s is a terminal residues, CMAP energy terms will not be added' % Color('%s%-4d' % (res_label[i-1], i), 'blue'))
			res_strip.append(i)
	
	print('%s CMAP parameters will be added to following residues:' % Color('Residue-specific', 'blue'))
	count = 0
	if len(res_single) >= 1:
		for i in res_single:
			if i not in res_strip:
				print('%4s%-4d' % (res_type[i-1], i), end='')
				count += 1
			if count % 11 == 10:
				print()
				count = 0
		if len(res_cmap) >= 1:
			print()
		else:
			print('NONE')
	else:
		print('NONE\n')
	print()

	if env:
		res_strip = []
		res_cmap_env = []
		res_cmap_env_num = []
		for i in res_env:
			if i == 1:
				print('Residue %s is a terminal residues, CMAP energy terms will not be added' % Color('%s%-4d' % (res_label[i-1], i), 'blue'))
				res_strip.append(i)
			elif i != len(res_label): # not the last residue
				for j in range(int(res_pointer[i-1])-1, int(res_pointer[i])-1):
					if atom_name[j] == 'H3' or atom_name[j] == 'OXT':
						print('Residue %s is a terminal residues, CMAP energy terms will not be added' % Color('%s%-4d' % (res_label[i-1], i), 'blue'))	
						res_strip.append(i)
				if i in res_strip:
					continue

				# check if cmap parameter of select residues are exists
				match = re.match('m?([A-Z]+)',res_type[i-1])
				res_name = match.group(1)
				if res_name in ['HIP', 'HIE', 'HID']:
					res_name = 'HIS'
				elif res_name == 'CYX':
					res_name = 'CYS'
				match_left = re.match('m?([A-Z]+)',res_type[i-2])
				match_right = re.match('m?([A-Z]+)',res_type[i])
				#print('%s\t%s' % (match_left.group(1), match_right.group(1)))
				name = '%s%s%s-0' % (Env(match_left.group(1)), res_name, Env(match_right.group(1)))
				if name not in cmap_name:
					print('Warning: %s CMAP parameter is not found for this residue %s'
						  %(Color('Environment-specific', 'blue'), Color('%s%-4d' %(res_label[i-1], i), 'red')))
					res_strip.append(i)
				else:
					#print(name)
					res_cmap_env.append(name)
					res_cmap_env_num.append(i-1)
			else:
				print('Residue %s is a terminal residues, CMAP energy terms will not be added' % Color('%s%-4d' % (res_label[i-1], i), 'blue'))
				res_strip.append(i)

		print('%s CMAP parameters will be added to following residues:' % Color('Environment-specific', 'blue'))
		count = 0
		if len(res_env) >= 1:
			for i in res_env:
				if i not in res_strip:
					print('%s%-4d' % (res_type[i-1], i), end='')
					count += 1
				if count % 11 == 10:
					print()
					count = 0
			if len(res_cmap_env) >= 1:
				print()
			else:
				print('NONE')
		else:
			print('NONE\n')
		res_cmap.extend(res_cmap_env)
		res_cmap_num.extend(res_cmap_env_num)
		print()	
	
	res_cmap_unique = []
	res_cmap_unique_num = []
	#print(res_cmap)
	#print(res_cmap_num)
	for i in range(len(res_cmap)):
		if res_cmap[i] not in res_cmap_unique:
			res_cmap_unique.append(res_cmap[i])
			res_cmap_unique_num.append(res_cmap_num[i])
	#print(res_cmap_unique)
	#print(res_cmap_unique_num)
	
	#print(res_cmap)
	if not silent:
		print('The new PROTOP file %s with CMAP parameters will be output.' % Color(output, 'blue'))
		print('Please make sure the input PRMTOP file %s is generated with %s.' % (Color(prmtop, 'blue'), Color(force_field, 'blue')))
		print('Are you sure to continue?[Y/N]')
		binary = input()
		if re.match('y(es)?', binary, re.I):
			print('\nChanges will be output to %s' % Color(output, 'blue'))
		else:
			exit()
		
	cmap_title = ''
	cmap_add = ''
	cmap_title += '%FLAG FORCE_FIELD_TYPE\n'
	cmap_title += '%FORMAT(i2,a78)\n'
	cmap_title += ' 1 CHARMM  31       *>>>>>>>>CHARMM22 All-Hydrogen Topology File for Proteins <<\n'
	cmap_title += '%COMMENT ADD CMAP energy terms to AMBER PRMTOP with ADD_CMAP.py\n'
	cmap_title += '%%COMMENT for Amber %s force field\n' % force_field
	cmap_add += '%FLAG CHARMM_UREY_BRADLEY_COUNT\n'
	cmap_add += '%COMMENT  V(ub) = K_ub(r_ik - R_ub)**2\n'
	cmap_add += '%COMMENT  Number of Urey Bradley terms and types\n\n'
	cmap_add += '%FORMAT(2i8)\n'
	cmap_add += '     3      1\n'
	cmap_add += '%FLAG CHARMM_UREY_BRADLEY\n'
	cmap_add += '%COMMENT  List of the two atoms and its parameter index\n'
	cmap_add += '%COMMENT  in each UB term: i,k,index\n'
	cmap_add += '%FORMAT(10i8)\n'
	cmap_add += '       2       5       1       3       5       1       4       5       1\n'
	cmap_add += '%FLAG CHARMM_UREY_BRADLEY_FORCE_CONSTANT\n'
	cmap_add += '%COMMENT  K_ub: kcal/mole/A**2\n'
	cmap_add += '%FORMAT(5e16.8)\n'
	cmap_add += '  0.00000000E+02\n'
	cmap_add += '%FLAG CHARMM_UREY_BRADLEY_EQUIL_VALUE\n'
	cmap_add += '%COMMENT  r_ub: A\n'
	cmap_add += '%FORMAT(5e16.8)\n'
	cmap_add += '  0.00000000E+01\n'
	cmap_add += '%FLAG CHARMM_NUM_IMPROPERS\n'
	cmap_add += '%COMMENT  Number of terms contributing to the\n'
	cmap_add += '%COMMENT  quadratic four atom improper energy term:\n'
	cmap_add += '%COMMENT  V(improper) = K_psi(psi - psi_0)**2\n'
	cmap_add += '%FORMAT(10i8)\n'
	cmap_add += '       1\n'
	cmap_add += '%FLAG CHARMM_IMPROPERS\n'
	cmap_add += '%COMMENT  List of the four atoms in each improper term\n'
	cmap_add += '%COMMENT  i,j,k,l,index  i,j,k,l,index\n'
	cmap_add += '%COMMENT  where index is into the following two lists:\n'
	cmap_add += '%COMMENT  CHARMM_IMPROPER_{FORCE_CONSTANT,IMPROPER_PHASE}\n'
	cmap_add += '%FORMAT(10i8)\n'
	cmap_add += '      15       5      17      16       1\n'
	cmap_add += '%FLAG CHARMM_NUM_IMPR_TYPES\n'
	cmap_add += '%COMMENT  Number of unique parameters contributing to the\n'
	cmap_add += '%COMMENT  quadratic four atom improper energy term\n'
	cmap_add += '%FORMAT(i8)\n'
	cmap_add += '       1\n'
	cmap_add += '%FLAG CHARMM_IMPROPER_FORCE_CONSTANT\n'
	cmap_add += '%COMMENT  K_psi: kcal/mole/rad**2\n'
	cmap_add += '%FORMAT(5e16.8)\n'
	cmap_add += '  0.00000000E+03\n'
	cmap_add += '%FLAG CHARMM_IMPROPER_PHASE\n'
	cmap_add += '%COMMENT  psi: degrees\n'
	cmap_add += '%FORMAT(5e16.8)\n'  
	cmap_add += '  0.00000000E+00\n'
	cmap_add += '%FLAG LENNARD_JONES_14_ACOEF\n%FORMAT(5E16.8)\n'
	cmap_add += lj_acoef_string
	cmap_add += '%FLAG LENNARD_JONES_14_BCOEF\n%FORMAT(5E16.8)\n'
	cmap_add += lj_bcoef_string
	cmap_add += '%FLAG CHARMM_CMAP_COUNT\n'
	cmap_add += '%COMMENT  Number of CMAP terms, number of unique CMAP parameters\n'
	cmap_add += '%FORMAT(2I8)\n'
	cmap_add += '%8d%8d\n' % (len(res_cmap), len(res_cmap_unique))
	cmap_add += '%FLAG CHARMM_CMAP_RESOLUTION\n'
	cmap_add += '%COMMENT  Number of steps along each phi/psi CMAP axis\n'
	cmap_add += '%COMMENT  for each CMAP_PARAMETER grid\n'
	cmap_add += '%FORMAT(100I4)\n'
	for name in res_cmap_unique:
		cmap_add += '%4d' % math.sqrt(cmap_count[cmap_name.index(name)])
	cmap_add += '\n'
	
	for i in range(len(res_cmap_unique)):
		cmap_add += '%%FLAG CHARMM_CMAP_PARAMETER_%02d\n' % (i+1)
		match = re.match('(\d)(\w+)(\d)-(\d)', res_cmap_unique[i])
		cmap_add += '%%COMMENT    %s   C    N    CA   C    N    CA   C    N    ' % match.group(2)
		cmap_add += '%4d\n' % math.sqrt(cmap_count[cmap_name.index(res_cmap_unique[i])])
		cmap_add += cmap_parameters[cmap_name.index(res_cmap_unique[i])]
	
	cmap_add += '%FLAG CHARMM_CMAP_INDEX\n'
	cmap_add += '%COMMENT  Atom index i,j,k,l,m of the cross term\n'
	cmap_add += '%COMMENT  and then pointer to CHARMM_CMAP_PARAMETER_n\n'
	cmap_add += '%FORMAT(6I8)\n'

	for i in range(len(res_cmap)):
		cmap_dih_pointer = []
		name = res_cmap[i]	 #cmap name: 0ALA0-0
		num = res_cmap_num[i] #res index: range(0,len(res_label))
		for j in range(int(res_pointer[num-1])-1, int(res_pointer[num])-1):
			if atom_name[j] == 'C':
				cmap_dih_pointer.append(j+1)
		for j in range(int(res_pointer[num])-1, int(res_pointer[num+1])-1):
			if atom_name[j] == 'N':
				cmap_dih_pointer.append(j+1)
			elif atom_name[j] == 'CA':
				cmap_dih_pointer.append(j+1)
			elif atom_name[j] == 'C':
				cmap_dih_pointer.append(j+1)
		for j in range(int(res_pointer[num+1])-1, int(res_pointer[num+2])-1):
			if atom_name[j] == 'N':
				cmap_dih_pointer.append(j+1)
		for i in range(len(cmap_dih_pointer)):
			cmap_add += '%8d' % cmap_dih_pointer[i]
		cmap_add += '%8d\n' % (res_cmap_unique.index(name)+1)
	
	out = open(output, 'w')
	for i in range(len(top_lines)):
		if i == 0:
			out.write(top_lines[i])
			out.write(cmap_title)
		else:
			out.write(top_lines[i])
	out.write(cmap_add)
	out.write('\n')
	out.close()
	print('%s write finished!' % Color(output, 'blue'))


if __name__ == '__main__':
	main()
