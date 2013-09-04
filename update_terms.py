import csv
f = open('data/ancs.csv', 'rb')
reader = csv.reader(f, delimiter=',', quotechar='"')

terms = {}

for row in reader:
	if row[2] == 'No Candidate':
		continue
	elif row[2] in terms:
		terms[row[2]] += 1
	else:
		terms[row[2]] = 1

print terms
	
f.close()