import re

# REG_NONDIGITS = re.compile(r'\D+')
# REG_EP_TITLE = re.compile(r'".+"')
REG_CHARACTER = re.compile(r'^(\t{5})([^\t()\n]+)')
REG_VOICE = re.compile(r"(\s+V\.O\.)|('S?\s.+)|(\s+\(.+\))")
REG_LINE = re.compile(r'^(\t{3})([^\t\n]+)')

with open('./scripts/dsn/dsn_s03e13.txt', errors='replace') as file:
	read_line = file.readline()
	while read_line:
		reg_char = REG_CHARACTER.search(read_line)
		if reg_char is None:
			read_line = file.readline()
		else:
			char_name = REG_VOICE.sub('', reg_char[2]).strip()
			print(char_name)
			read_line = file.readline()
			line_parts = []
			while len(read_line) > 1:
				reg_line = REG_LINE.search(read_line)
				if reg_line is not None:
					line_parts.append(reg_line[2].strip())
				read_line = file.readline()
			char_line = ' '.join(line_parts)
			print(f'{char_line}\n')
