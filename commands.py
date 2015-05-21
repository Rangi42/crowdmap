import os

def save(data):
	filename = data.get('filename')
	filename = os.path.join(os.path.dirname(__file__), filename)

	extension = os.path.splitext(filename)[1]
	if extension == '.blk':
		content = data.get('data')
		if content:
			if type(content) is list:
				content = bytearray(content)
			with open(filename, 'wb') as out:
				out.write(content)
	else:
		raise NotImplementedError

def add_map(data):
	label = data['label']
	group = data['group']
	header = data['header']
	header_2 = data['header_2']
	width = data['width']
	height = data['height']

	map_name = label.upper()

	header_line = '\tmap_header ' + ', '.join(map('{}'.format, [
		label,
		header['tileset'],
		header['permission'],
		header['location'],
		header['music'],
		header['lighting'],
		header['fish'],
	]))
	header_2_line = '\tmap_header_2 ' + ', '.join(map('{}'.format, [
		label,
		map_name,
		header_2['border_block'],
		'NONE',
	]))

	root = 'pokecrystal/'

	path = root + 'maps/map_headers.asm'
	path_2 = root + 'maps/second_map_headers.asm'
	blk_path = root + 'maps/' + label + '.blk'
	constants_path = root + 'constants/map_constants.asm'
	script_path = root + 'maps/' + label + '.asm'
	include_path = root + 'maps.asm'

	text = open(path).read()
	text_2 = open(path_2).read()
	if label + ',' in text.split() or label + ',' in text_2.split():
		raise Exception, 'yeah nah {} is already a map or existing macro'.format(label)

	lines = text.split('\n')

	for i, line in enumerate(lines):
		words = line.split()
		group_no = 0
		if 'dw' in words:
			group_no += 1
			if group in words:
				break
	index = -1
	map_no = 0
	for i, line in enumerate(lines):
		if group + ':' in line:
			index = i + 1
			map_no = 1
		else:
			if index != -1:
				if ':' in line.split(';')[0]:
					break
				if line:
					index = i + 1
					map_no += 1

	lines.insert(index, header_line)
	new_text = '\n'.join(lines)

	lines_2 = text_2.split('\n')
	lines_2.append(header_2_line)
	new_text_2 = '\n'.join(lines_2)

	blk = bytearray([1] * width * height)

	constants = open(constants_path).read()
	constants_lines = constants.split('\n')
	constants_lines.append('GROUP_{} EQU {}'.format(map_name, group_no))
	constants_lines.append('MAP_{} EQU {}'.format(map_name, map_no))
	constants_lines.append('{}_WIDTH EQU {}'.format(map_name, width))
	constants_lines.append('{}_HEIGHT EQU {}'.format(map_name, height))
	new_constants = '\n'.join(constants_lines)

	script = ''
	script += '{}_MapScriptHeader:\n'.format(label)
	script += '\t; triggers\n'
	script += '\tdb 0\n'
	script += '\n'
	script += '\t; callbacks\n'
	script += '\tdb 0\n'
	script += '\n; <scripts go here>\n'
	script += '\n; <text goes here>\n'
	script += '\n'
	script += '{}_MapEventHeader:\n'.format(label)
	script += '\t; filler\n'
	script += '\tdb 0, 0\n'
	script += '\n'
	script += '\t; warps\n'
	script += '\tdb 0\n'
	script += '\n'
	script += '\t; coord events\n'
	script += '\tdb 0\n'
	script += '\n'
	script += '\t; bg events\n'
	script += '\tdb 0\n'
	script += '\n'
	script += '\t; object events\n'
	script += '\tdb 0\n'
	script += '\n'

	include = open(include_path).read()
	include += '\n'
	include += 'SECTION "{}", ROMX\n'.format(label)
	include += 'INCLUDE "maps/{}.asm"'.format(label)
	include += 'SECTION "{} Blockdata", ROMX\n'.format(label)
	include += '{0}_BlockData: INCBIN "maps/{0}.blk"'.format(label)

	with open(path, 'w') as out:
		out.write(new_text)
	with open(path_2, 'w') as out:
		out.write(new_text_2)
	with open(blk_path, 'wb') as out:
		out.write(blk)
	with open(constants_path, 'w') as out:
		out.write(new_constants)
	with open(script_path, 'w') as out:
		out.write(script)
	with open(include_path, 'w') as out:
		out.write(include)

	print 'Added map {} to group {}'.format(data['label'], data['group'])

commands = {
	'save': save,
	'add_map': add_map,
}

def main(data):
	command = data.get('command')
	function = commands.get(command)
	if function:
		function(data)
