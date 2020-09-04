from os import listdir, rename

# rename('./scripts/tng/102.txt', './scripts/tng/tng_s01e01-2.txt')
# new = 3

# new = 1
# for old in range(551,575):
# 	old_file = f'./scripts/ds9/{old}.txt'
# 	new_file ='./scripts/ds9/ds9_s07e'
# 	if new < 10:
# 		new_file += '0'
# 	new_file += str(new) + '.txt'
# 	rename(old_file, new_file)
# 	new += 1

folder = './scripts/dsn/'
files = listdir(folder)
for old in files:
	new = old.replace('ds9', 'dsn')
	rename(folder + old, folder + new)
