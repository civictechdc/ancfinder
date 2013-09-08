import csv
reader = csv.reader(open('data/historical-commissioners.csv', 'rb'), delimiter=',', quoting=csv.QUOTE_MINIMAL)
writer = csv.writer(open('data/anc-terms.csv', 'wb'), delimiter=',', quotechar='/') 

#Not sure if I used quotechar correctly, but this got the result I was trying to achieve.

terms = {}

for row in reader:
	short = str([row[3][:3] + " " + row[2][:3]])
	if row[2] == 'No candidate':
		continue
	elif short in terms:
		terms[short] += 1
		t = terms[short]
	else:
		terms[short] = 1
		t = 1
	output = [row[0]] + [row[1]] + [row[2]] + [row[3]] + [t]
	if row[0][:4] == "2012":
		writer.writerow(output)