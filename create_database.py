'''
Star Trek episodes/characters/lines database creator
Coded by Drue Gilbert
Scripts found at: https://www.st-minutiae.com/resources/scripts.
Files have been renamed ("tng_s01e01.txt" through "dsn_s07e25.txt").
Some formatting has been fixed in TNG scripts, DS9 scripts have a lot
of errors, some of which have been accounted for in the line parsing method.
'''

import sqlite3
from sqlite3 import Error
from os import listdir
import re
import datetime as dt

REG_NONDIGITS = re.compile(r'\D+')
REG_EP_TITLE = re.compile(r'".+"')
REG_CHARACTER = re.compile(r'^(\t{5})([^\t()\n]+)')
REG_VOICE = re.compile(r"(\s+V\.\s?O\.)|('S?\s.+)|(\s+\(.+\))", re.I)
REG_LINE = re.compile(r'^( ?\t{3})([^\t\n]+)')
REG_PAREN = re.compile(r'^\t{4}[^\t\n]')

def create_connection(db_file):
	connection = None
	try:
		connection = sqlite3.connect(db_file)
	except Error as e:
		print(e)
	return connection

def create_table(connection, create_table_sql):
	try:
		cursor = connection.cursor()
		cursor.execute(create_table_sql)
	except Error as e:
		print(e)

def find_episode_id(connection, episode):
	cursor = connection.cursor()
	cursor.execute('SELECT id FROM episodes WHERE show=? AND season=? AND number=?;', episode)
	row = cursor.fetchone()
	if row is None:
		return None
	return row[0]

def create_episode(connection, episode):
	id = find_episode_id(connection, episode[:3])
	if id is not None:
		return id
	sql = '''INSERT INTO episodes (show, season, number, title)
			VALUES (?,?,?,?);'''
	cursor = connection.cursor()
	cursor.execute(sql, episode)
	return cursor.lastrowid

def find_character_id(connection, character):
	cursor = connection.cursor()
	cursor.execute('SELECT id FROM characters WHERE name=?', character)
	row = cursor.fetchone()
	if row is None:
		return None
	return row[0]

def create_character(connection, character):
	id = find_character_id(connection, character)
	if id is not None:
		return id
	sql = '''INSERT INTO characters (name)
			VALUES (?);'''
	cursor = connection.cursor()
	cursor.execute(sql, character)
	return cursor.lastrowid

def create_line(connection, line):
	sql = '''INSERT INTO lines (episode_id, character_id, line)
			VALUES (?,?,?);'''
	cursor = connection.cursor()
	cursor.execute(sql, line)
	return cursor.lastrowid

def parse_episode_title(path):
	with open(path, errors='replace') as f:
		r_line = f.readline()
		while r_line:
			title = REG_EP_TITLE.search(r_line)
			if title is not None:
				return title[0].replace('"', '')
			r_line = f.readline()
	return None

def parse_characters_lines(connection, path, ep_id):
	empties = 0
	with open(path, errors='replace') as file:
		read_line = file.readline()
		while read_line:
			reg_char = REG_CHARACTER.search(read_line)
			if reg_char is None:
				read_line = file.readline()
			else:
				char_name = REG_VOICE.sub('', reg_char[2]).strip().upper()
				if char_name.endswith(':'):
					### lots of DS9 episodes have directions with the same number of tabs as character names
					read_line = file.readline()
				else:
					### some names have a stray period
					char_name.rstrip('.')
					char_id = create_character(connection, (char_name,))
					read_line = file.readline()
					### lots of DS9 episodes have an extra blank line after name
					skip_blank = True
					line_parts = []
					while len(read_line) > 1 or skip_blank:
						if skip_blank:
							skip_blank = False
						reg_line = REG_LINE.search(read_line)
						if reg_line is not None:
							line_parts.append(reg_line[2].strip())
						### lots of DS9 episodes have a blank line after a parenthetical
						elif REG_PAREN.search(read_line) is not None:
							skip_blank = True
						read_line = file.readline()
					char_line = ' '.join(line_parts)
					line_id = create_line(connection, (ep_id, char_id, char_line))
					if len(char_line) == 0:
						empties += 1
						print(f'Empty line id: {line_id}')
	return empties

def process_folder(connection, folder, show):
	filenames = listdir(folder)
	filenames.sort()
	empties = 0
	for file in filenames:
		path = folder + '/' + file
		file_numbers = [int(n) for n in REG_NONDIGITS.split(file)[1:3]]
		ep_title = parse_episode_title(path)
		ep_id = create_episode(connection, (show, file_numbers[0], file_numbers[1], ep_title))
		empties += parse_characters_lines(connection, path, ep_id)
	print(f'Total empty lines in folder: {empties}')

def main():
	database = './star_trek_db.sqlite3'

	sql_create_episodes_table = '''CREATE TABLE IF NOT EXISTS episodes (
								id integer PRIMARY KEY,
								show text NOT NULL,
								season integer NOT NULL,
								number integer NOT NULL,
								title text
								);'''
	sql_create_characters_table = '''CREATE TABLE IF NOT EXISTS characters (
								id integer PRIMARY KEY,
								name text NOT NULL
								);'''
								### may add actor to character later
	sql_create_lines_table = '''CREATE TABLE IF NOT EXISTS lines (
								id integer PRIMARY KEY,
								episode_id integer NOT NULL,
								character_id integer NOT NULL,
								line text NOT NULL,
								FOREIGN KEY (episode_id) REFERENCES episodes (id),
								FOREIGN KEY (character_id) REFERENCES characters (id)
								);'''

	connection = create_connection(database)
	if connection is not None:
		print('Creating tables')
		create_table(connection, sql_create_episodes_table)
		create_table(connection, sql_create_characters_table)
		create_table(connection, sql_create_lines_table)

		### moved connection.commit() from every create method to just twice here. major speed improvement.
		### no need to worry about concurrent access to db from elsewhere.
		print('Processing: ./scripts/tng')
		tng_start = dt.datetime.now()
		process_folder(connection, './scripts/tng', 'TNG')
		tng_end = dt.datetime.now()
		print(f'Processing time: {tng_end - tng_start}')
		connection.commit()

		print('\nProcessing: ./scripts/dsn')
		dsn_start = dt.datetime.now()
		process_folder(connection, './scripts/dsn', 'DS9')
		dsn_end = dt.datetime.now()
		print(f'Processing time: {dsn_end - dsn_start}')
		connection.commit()

		connection.close()

if __name__ == '__main__':
	main()
